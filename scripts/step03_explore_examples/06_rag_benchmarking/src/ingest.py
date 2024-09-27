from utils.ingest_docs import fetch_terraform_docs, ingest_docs
from helpers.config import TERRAFORM_DOCS_TABLE_NAME, EMBEDDINGS_MODEL_NAME

def ingest_terraform_docs():
    documents = fetch_terraform_docs()
    ingest_docs(documents, TERRAFORM_DOCS_TABLE_NAME, EMBEDDINGS_MODEL_NAME)

def execute_ingestion():
    ingest_terraform_docs()