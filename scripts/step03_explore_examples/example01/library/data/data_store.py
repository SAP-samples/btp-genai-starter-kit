from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import logging

log = logging.getLogger(__name__)

# Split the docs into chunks
def split_docs_into_chunks(
    documents: list[Document], chunk_size: int = 500, chunk_overlap: int = 0
):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)
    log.info(f"Split {len(documents)} documents into {len(chunks)} chunks.")

    return chunks
