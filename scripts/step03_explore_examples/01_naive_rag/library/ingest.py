from logging import getLogger

from langchain_community.vectorstores.hanavector import HanaDB
from langchain_community.document_loaders import GitLoader

from utils.rag import split_docs_into_chunks
from utils.hana import (
    get_connection_to_hana_db,
    teardown_hana_table,
    has_embeddings,
)

from .config import TABLE_NAME
from .factory import create_llm_and_embeddings

log = getLogger(__name__)


def fetch_docs():
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
        log.success("Documents loaded successfully.")
        return documents
    except Exception as e:
        log.error(f"Error occurred while loading documents: {str(e)}")


def ingest(documents):
    try:
        log.info(f"Start ingesting data in {TABLE_NAME}")

        teardown_hana_table(TABLE_NAME)
        connection_to_hana = get_connection_to_hana_db()
        _, embeddings = create_llm_and_embeddings()
        cur = connection_to_hana.cursor()
        chunks = split_docs_into_chunks(documents=documents)

        db = HanaDB(
            embedding=embeddings, connection=connection_to_hana, table_name=TABLE_NAME
        )
        log.success("Clear the HANA DB")
        db.delete(filter={})

        log.info("Add documents chunks to the HANA DB")
        db.add_documents(chunks)
        log.success("Documents added successfully.")

        has_embeddings(TABLE_NAME, verbose=True)
        log.success("Ingestion completed successfully.")

        cur.close()
    except Exception as e:
        log.error(f"Error occurred during ingestion: {str(e)}")
