import logging
import re

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.document_loaders import GitLoader

from utils.rag import split_docs_into_chunks

from helpers.factory import setup_components
from helpers.config import SAP_DOCS_TABLE_NAME, PODCASTS_TABLE_NAME, TERRAFORM_TABLE_NAME

log = logging.getLogger(__name__)


def load_documents_from_github():
    # Load the documents from a GitHub repository
    loader = GitLoader(
        clone_url="https://github.com/SAP-docs/btp-cloud-platform",
        repo_path="./gen/btp-cloud-platform",
        file_filter=lambda file_path: re.match(
            r"^./gen/btp-cloud-platform/docs/10-concepts/.*.md$", file_path
        ),
        branch="main",
    )
    text_documents = loader.load()
    log.info("Getting the documents from the GitHub repository ...")

    # Split the documents into chunks
    chunks = split_docs_into_chunks(documents=text_documents)
    return chunks


def ingest_podcasts():
    _, _, db = setup_components(PODCASTS_TABLE_NAME)

    print("Load the docuents into the HANA DB to get them vectorized")

    # Download transcript from Episode 64 of the SAP podcast
    loader_ep64 = PyMuPDFLoader(
        "https://sap-podcast-bucket.s3.amazonaws.com/the-future-of-supply-chain/The_Future_of_Supply_Chain_Episode_64_transcript.pdf"
    )
    # Download transcript from Episode 65 of the SAP podcast
    loader_ep65 = PyMuPDFLoader(
        "https://sap-podcast-bucket.s3.amazonaws.com/the-future-of-supply-chain/The_Future_of_Supply_Chain_Episode_65_transcript.pdf"
    )

    # Load the documents and split them into chunks
    chunks = loader_ep64.load_and_split()
    chunks += loader_ep65.load_and_split()

    print(chunks[0])

    # Delete already existing documents from the table
    log.info("Deleting existing podcasts from the table ...")
    db.delete(filter={})
    log.success("Podcasts deleted successfully!")

    # add the loaded document chunks to the HANA DB
    log.info("Adding podcast chunks to the HANA DB ...")
    db.add_documents(chunks)
    log.success("Added podcast chunks successfully!")


def ingest_sap_docs():
    _, _, db = setup_components(SAP_DOCS_TABLE_NAME)

    chunks = load_documents_from_github()

    # Delete already existing documents from the table
    log.info("Deleting existing sap btp docs from the table ...")
    db.delete(filter={})
    log.success("SAP btp docs chunks deleted successfully!")

    # add the loaded document chunks to the HANA DB
    log.info("Adding SAP btp docs chunks to the HANA DB ...")
    db.add_documents(chunks)
    log.success("Added SAP btp docs successfully!")

def load_terraform_docs_from_github():
    # Load the documents from a GitHub repository
    loader = GitLoader(
        clone_url="https://github.com/SAP/terraform-provider-btp",
        repo_path="./gen/docs/",
        file_filter=lambda file_path: file_path.startswith("./gen/docs/docs")
        and file_path.endswith(".md"),
        branch="main",
    )
    text_documents = loader.load()
    log.info("Getting the Terraform documents from the GitHub repository ...")

    # Split the documents into chunks
    chunks = split_docs_into_chunks(documents=text_documents)
    return chunks    

def ingest_terraform_docs():

    log.info("Ingesting Terraform docs ...")
    _, _, db = setup_components(TERRAFORM_TABLE_NAME)

    chunks = load_terraform_docs_from_github()

    # Delete already existing documents from the table
    log.info("Deleting existing Terraform docs from the table ...")
    db.delete(filter={})
    log.success("Terraform docs chunks deleted successfully!")

    # add the loaded document chunks to the HANA DB
    log.info("Adding Terraform docs chunks to the HANA DB ...")
    db.add_documents(chunks)
    log.success("Added Terraform docs successfully!")

def main():
    ingest_podcasts()
    ingest_sap_docs()
    ingest_terraform_docs()

if __name__ == "__main__":
    main()
