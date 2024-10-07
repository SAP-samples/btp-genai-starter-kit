from logging import getLogger

from langchain_community.vectorstores.hanavector import HanaDB
from langchain_community.document_loaders import GitLoader
from gen_ai_hub.proxy.langchain.openai import OpenAIEmbeddings
from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client

from utils.rag import split_docs_into_chunks
from utils.hana import (
    get_connection_to_hana_db,
)

log = getLogger(__name__)

def fetch_terraform_docs():
    try:
        log.info("Getting the documents from the GitHub repository")
        loader = GitLoader(
            clone_url="https://github.com/SAP/terraform-provider-btp",
            repo_path="./gen/docs/",
            file_filter=lambda file_path: file_path.startswith("./gen/docs/docs")
            and file_path.endswith(".md"),
            branch="main",
        )
        documents = loader.load()
        log.info("Terraform documents loaded successfully.")
        return documents
    except Exception as e:
        log.error(f"Error occurred while loading documents: {str(e)}")

def ingest_docs(documents, table_name, embeddings_model_name):   
    try:
        log.info(f"Start ingesting data in {table_name}")
        assert table_name, "Table name is required"
        assert embeddings_model_name, "EMBEDDINGS_MODEL_NAME is required"
        connection_to_hana = get_connection_to_hana_db()
        proxy_client = get_proxy_client("gen-ai-hub")       
        embeddings = OpenAIEmbeddings(
            proxy_model_name=embeddings_model_name, proxy_client=proxy_client
        )
        cur = connection_to_hana.cursor()
        chunks = split_docs_into_chunks(documents=documents)

        db = HanaDB(
            embedding=embeddings, connection=connection_to_hana, table_name=table_name
        )
        log.info(f"Deleting existing document chunks from the table {table_name}")
        db.delete(filter={})
        log.success("Document chunks deleted successfully!")

        log.info(f"Add document chunks to the table {table_name}")
        db.add_documents(chunks)
        log.success("Document chunks added successfully.")

        cur.close()
    except Exception as e:
        log.error(f"Error occurred during ingestion: {str(e)}")