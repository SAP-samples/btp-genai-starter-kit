import logging

from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client
from gen_ai_hub.proxy.langchain.openai import OpenAIEmbeddings
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import GitLoader
from langchain_text_splitters import MarkdownHeaderTextSplitter
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.embeddings.langchain import LangchainEmbedding


log = logging.getLogger(__name__)


def execute_split_data():
    print("Compare different splitting strategies")

    # Load the documents from a GitHub repository
    loader = GitLoader(
        clone_url="https://github.com/SAP/terraform-provider-btp",
        repo_path="./gen/docs/",
        file_filter=lambda file_path: file_path.endswith(".md"),
        branch="main",
    )
    log.info("Getting the documents from the GitHub repository ...")
    tf_docs_all = loader.load()

    # Recursive splitter
    print("Recursive splitter")
    recursive_chunks = recursive_split_docs_into_chunks(documents=tf_docs_all)
    print("=" * 10, "RECURSIVE CHUNKS", "=" * 10)
    print(f"Loaded {len(recursive_chunks)} docs")
    print("chunk 0: ", recursive_chunks[0].page_content)
    print("chunk 1: ", recursive_chunks[1].page_content)

    # Markdown splitter
    print("Markdown splitter")
    markdown_chunks = markdown_split_docs_into_chunks(documents=tf_docs_all)
    print("=" * 10, "MARKDOWN CHUNKS", "=" * 10)
    print(f"Loaded {len(markdown_chunks)} docs")
    print("chunk 0: ", markdown_chunks[0].page_content)
    print("chunk 1: ", markdown_chunks[1].page_content)

    # Markdown and then recursive splitter
    markdown_recursive_chunks = recursive_split_docs_into_chunks(
        documents=markdown_chunks
    )
    print("Markdown and then recursive splitter")
    print("=" * 10, "MARKDOWN RECURSIVE CHUNKS", "=" * 10)
    print(f"Loaded {len(markdown_recursive_chunks)} docs")
    print("chunk 0: ", markdown_recursive_chunks[0].page_content)
    print("chunk 1: ", markdown_recursive_chunks[1].page_content)

    # Semantic splitter
    # load documents with llama_index
    required_exts = [".md"]

    reader = SimpleDirectoryReader(
        input_dir="./gen/docs/",
        required_exts=required_exts,
        recursive=True,
    )

    docs = reader.load_data()

    # Split the first 5 documents into chunks. Calls embedding models to create chunks.
    print("Semantic splitter")
    semantic_chunks = semantic_split_docs_into_chunks(docs[:10])
    print(f"Loaded {len(semantic_chunks)} docs")
    for i, chunk in enumerate(semantic_chunks[:5]):
        print(f"chunk {i}: {chunk.text}")

    log.success("Creation of chunks completed.")


# Split the docs into chunks
def recursive_split_docs_into_chunks(
    documents: list[Document], chunk_size: int = 256, chunk_overlap: int = 0
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


# Split the docs into chunks
def markdown_split_docs_into_chunks(documents: list[Document]):
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]

    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on, strip_headers=False
    )

    md_header_splits = []
    for text_document in documents:
        split_results = markdown_splitter.split_text(text_document.page_content)
        # merge page and chunk metadata
        for split_result in split_results:
            split_result.metadata = {**text_document.metadata, **split_result.metadata}
        md_header_splits.extend(split_results)

    log.info(f"Split {len(documents)} documents into {len(md_header_splits)} chunks.")

    return md_header_splits


# Split the docs into chunks
def semantic_split_docs_into_chunks(documents: list[Document]):
    # Get the proxy client for the AI Core service
    proxy_client = get_proxy_client("gen-ai-hub")
    # Create the OpenAIEmbeddings object
    embeddings = OpenAIEmbeddings(
        proxy_model_name="text-embedding-ada-002", proxy_client=proxy_client
    )
    embed_model = LangchainEmbedding(embeddings)

    splitter = SemanticSplitterNodeParser(
        buffer_size=1, breakpoint_percentile_threshold=95, embed_model=embed_model
    )

    nodes = splitter.get_nodes_from_documents(documents)

    log.info(f"Split {len(documents)} documents into {len(nodes)} chunks.")

    return nodes
