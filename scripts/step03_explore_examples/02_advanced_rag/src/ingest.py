import logging
import re
import sys

from langchain_community.document_loaders import GitLoader, PyMuPDFLoader
from utils.rag import split_docs_into_chunks

from helpers.factory import setup_components
from helpers.config import SAP_DOCS_TABLE_NAME, PODCASTS_TABLE_NAME

log = logging.getLogger(__name__)


def load_documents_from_github():
    """
    Load documents from a GitHub repository using GitLoader and split them into chunks.

    Returns:
        List of document chunks.
    """
    log.info("Getting the documents from the GitHub repository...")
    try:
        # Load the documents from a GitHub repository using GitLoader
        loader = GitLoader(
            clone_url="https://github.com/SAP-docs/btp-cloud-platform",
            repo_path="./gen/btp-cloud-platform",
            file_filter=lambda file_path: re.match(
                r"^./gen/btp-cloud-platform/docs/10-concepts/.*.md$", file_path
            ),
            branch="main",
        )
        text_documents = loader.load()

        # Split the documents into chunks
        chunks = split_docs_into_chunks(documents=text_documents)
        return chunks
    except Exception as e:
        log.error(f"Error loading documents from GitHub: {str(e)}")
        return []


def ingest_podcasts():
    """
    Ingest Podcast data into HANA db.
    """
    _, _, db = setup_components(PODCASTS_TABLE_NAME)

    try:
        # Clear any existing documents
        log.info("Deleting existing podcast documents from the table...")
        db.delete(filter={})
        log.info("Existing podcast documents deleted successfully!")

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
            if documents:
                db.add_documents(documents)
                log.info(f"Added documents for episode {ep['episode']} - {ep['title']}")
            else:
                log.warning(
                    f"No documents found for episode {ep['episode']} - {ep['title']}"
                )

        log.info("Retriever created successfully.")
    except Exception as e:
        log.error(f"Error during podcast ingestion: {str(e)}")


def load_and_process_documents(loader, podcast_title, episode):
    """
    Load documents using a loader and add metadata.

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
        log.error(f"Error loading documents for podcast '{podcast_title}': {str(e)}")
        sys.exit(1)


def ingest_sap_docs():
    """
    Ingest SAP documentation into HANA DB.
    """
    _, _, db = setup_components(SAP_DOCS_TABLE_NAME)

    chunks = load_documents_from_github()

    if not chunks:
        log.warning("No document chunks to ingest.")
        return

    try:
        # Delete already existing documents from the table
        log.info("Deleting existing SAP BTP documents from the table...")
        db.delete(filter={})
        log.info("Existing SAP BTP documents deleted successfully!")

        # Add the loaded document chunks to the HANA DB
        log.info("Adding SAP BTP document chunks to the HANA DB...")
        db.add_documents(chunks)
        log.success("Added SAP btp docs successfully!")
    except Exception as e:
        log.error(f"Error during SAP documents ingestion: {str(e)}")


def execute_ingestion():
    ingest_podcasts()
    ingest_sap_docs()

