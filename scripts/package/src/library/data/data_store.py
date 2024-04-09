from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain.schema import Document
from pathlib import Path
from library.util.io import get_files_in_folder
import logging

log = logging.getLogger(__name__)

# Info partly taken from https://python.langchain.com/docs/integrations/vectorstores/hanavector


# Get all the TF provider docs
def load_docs(tf_source_path: Path, glob_pattern: str = "*.md"):
    tf_docs_all = []
    files = get_files_in_folder(folder=tf_source_path, glob_pattern=glob_pattern)
    for file in files:
        document = TextLoader(file_path=str(file)).load()
        tf_docs_all.extend(document)

    return tf_docs_all


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
