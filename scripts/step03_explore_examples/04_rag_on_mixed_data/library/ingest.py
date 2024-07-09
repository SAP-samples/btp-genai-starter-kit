import sys
from logging import getLogger

from gen_ai_hub.proxy.langchain.openai import ChatOpenAI
from gen_ai_hub.proxy.langchain.openai import OpenAIEmbeddings
from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client
from langchain_community.vectorstores.hanavector import HanaDB
from langchain_community.document_loaders import WikipediaLoader

from utils.rag import split_docs_into_chunks
from utils.hana import (
    get_connection_to_hana_db,
    teardown_hana_table,
    has_embeddings,
)

from .config import (
    LLM_MODEL_NAME,
    EMBEDDINGS_MODEL_NAME,
    STRUCTURED_DATA_TABLE_NAME,
    VECTOR_EMBEDDINGS_TABLE_NAME,
)

log = getLogger(__name__)



def create_llm_and_embeddings():
    # Get the proxy client for the AI Core service
    proxy_client = get_proxy_client("gen-ai-hub")

    llm = ChatOpenAI(
        proxy_model_name=LLM_MODEL_NAME, proxy_client=proxy_client, temperature=0
    )
    embeddings = OpenAIEmbeddings(
        proxy_model_name=EMBEDDINGS_MODEL_NAME, proxy_client=proxy_client
    )
    return llm, embeddings


def ingest_unstructured_data(cities):
    try:
        connection_to_hana = get_connection_to_hana_db()

        log.info("Start ingesting unstructured data.")
        log.info("Start fetching documents from Wikipedia")
        wiki_docs = [
            WikipediaLoader(query=row["city_name"], load_max_docs=1).load()[0]
            for row in cities
        ]
        log.success(f"Found {len(wiki_docs)} documents from Wikipedia.")

        # Split the documents into chunks
        chunks = split_docs_into_chunks(documents=wiki_docs)

        _, embeddings = create_llm_and_embeddings()

        # Create the HanaDB object
        db = HanaDB(
            embedding=embeddings,
            connection=connection_to_hana,
            table_name=VECTOR_EMBEDDINGS_TABLE_NAME,
        )

        # Delete already existing documents from the table
        log.info("Cleaning up table with vectoe embeddings.")
        db.delete(filter={})
        log.success("Table cleaned up successfully.")

        # add the loaded document chunks to the HANA DB
        log.info("Adding the loaded document chunks to the HANA DB")
        db.add_documents(chunks)
        has_embeddings(VECTOR_EMBEDDINGS_TABLE_NAME, verbose=True)
        log.success("Documents added successfully.")

        log.success("Unstructured data ingested successfully.")
    except Exception as e:
        log.error(f"Ingesting unstructured data failed: {str(e)}")
        sys.exit()


def ingest_structured_data(cities):
    try:
        log.info("Start ingesting structured data.")
        teardown_hana_table(STRUCTURED_DATA_TABLE_NAME)
        connection_to_hana = get_connection_to_hana_db()
        cur = connection_to_hana.cursor()

        cur.execute(
            f"CREATE TABLE {STRUCTURED_DATA_TABLE_NAME} (CITY_NAME NCHAR(16) PRIMARY KEY, POPULATION INTEGER, COUNTRY NCHAR(16))"
        )

        sql = f"INSERT INTO {STRUCTURED_DATA_TABLE_NAME} (CITY_NAME, POPULATION, COUNTRY) VALUES (:city_name, :population, :country)"
        for city in cities:
            cur.execute(
                sql,
                {
                    "city_name": city["city_name"],
                    "population": city["population"],
                    "country": city["country"],
                },
            )

        log.info("Table with structured data created:")
        cur.execute(f"SELECT * FROM {STRUCTURED_DATA_TABLE_NAME}")
        log.info(cur.fetchall())
        cur.close()

        log.success("Structured data ingested successfully.")
    except Exception as e:
        log.error(f"An error occurred while ingesting structured data: {str(e)}")
        teardown_hana_table(STRUCTURED_DATA_TABLE_NAME)
        sys.exit()


def ingest():
    cities = [
        {"city_name": "Toronto", "population": 2930000, "country": "Canada"},
        {"city_name": "Tokyo", "population": 13960000, "country": "Japan"},
        {"city_name": "Berlin", "population": 3645000, "country": "Germany"},
    ]

    ingest_structured_data(cities)
    ingest_unstructured_data(cities)
