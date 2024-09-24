import logging
import re
import sys

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.document_loaders import GitLoader

from utils.rag import split_docs_into_chunks

from helpers.factory import setup_components
from helpers.config import SAP_DOCS_TABLE_NAME, PODCASTS_TABLE_NAME

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
    """
    Ingest Podcast data into HANA db.
    """
    _, _, db = setup_components(PODCASTS_TABLE_NAME)

    # Clear any existing documents
    db.delete(filter={})

    # Podcast data
    episodes = [
        {
            "url": "https://sap-podcast-bucket.s3.amazonaws.com/the-future-of-supply-chain/The_Future_of_Supply_Chain_Episode_64_transcript.pdf",
            "title": "Future of Supply Chain: Episode 64: Proactively Planning for Risk in Your Supply Chain with Everstream's Koray Kose and SAP's Volker Wilhelm",
            "episode": 64,
        },
        {
            "url": "https://sap-podcast-bucket.s3.amazonaws.com/the-future-of-supply-chain/The_Future_of_Supply_Chain_Episode_65_transcript.pdf",
            "title": "The Future of Supply Chain: Episode 65: Grounding Your Supply Chain in Data with Google Cloud’s Paula Natoli",
            "episode": 65,
        },
    ]

    # Process and add documents for each episode
    for ep in episodes:
        loader = PyMuPDFLoader(ep["url"])
        documents = load_and_process_documents(loader, ep["title"], ep["episode"])
        db.add_documents(documents)

    log.info("Retriever created successfully.")


def load_and_process_documents(loader, podcast_title, episode):
    """
    Load documents using PyMuPDFLoader and add metadata.

    Args:
        loader: The document loader object.
        podcast_title: The title of the podcast.
        episode: The episode number.

    Returns:
        List of documents with added metadata.
    """
    try:
        documents = loader.load()
        for doc in documents:
            doc.metadata["podcast_title"] = podcast_title
            doc.metadata["episode"] = episode
        return documents
    except Exception as e:
        log.info(f"Error loading documents: {str(e)}")
        sys.exit(1)


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


def main():
    ingest_podcasts()
    ingest_sap_docs()


if __name__ == "__main__":
    main()
