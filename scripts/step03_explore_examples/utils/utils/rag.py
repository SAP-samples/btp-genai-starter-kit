import logging
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

log = logging.getLogger(__name__)


def split_docs_into_chunks(
    documents: list[Document], chunk_size: int = 1000, chunk_overlap: int = 100
):
    """
    Splits a list of documents into chunks of specified size with overlap.

    Args:
        documents (list[Document]): The list of documents to be split into chunks.
        chunk_size (int, optional): The size of each chunk. Defaults to 1000.
        chunk_overlap (int, optional): The overlap between consecutive chunks. Defaults to 100.

    Returns:
        list[list[Document]]: A list of chunks, where each chunk is a list of documents.

    """
    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            add_start_index=True,
        )
        chunks = text_splitter.split_documents(documents)
        log.info(f"Split {len(documents)} documents into {len(chunks)} chunks.")

        return chunks
    except Exception as e:
        log.error(f"An error occurred while splitting documents into chunks: {str(e)}")
        raise
