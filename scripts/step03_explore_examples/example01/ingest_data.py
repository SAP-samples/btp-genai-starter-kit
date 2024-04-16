from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client
from gen_ai_hub.proxy.langchain.openai import OpenAIEmbeddings
from langchain_community.vectorstores.hanavector import HanaDB
from langchain_community.document_loaders import GitLoader
from library.constants.folders import FILE_ENV
from library.constants.table_names import TABLE_NAME
from library.data.data_store import split_docs_into_chunks
from library.data.hana_db import get_connection_to_hana_db
from library.util.logging import initLogger


from dotenv import load_dotenv
import logging

log = logging.getLogger(__name__)
initLogger()


# This function loads the documents into the HANA DB to get them vectorized and validates the documents are loaded correctly
def main():
    # Load environment variables
    load_dotenv(dotenv_path=str(FILE_ENV), verbose=True)

    log.header("Load the documents into the HANA DB to get them vectorized")

    # Load the documents from a GitHub repository
    loader = GitLoader(
        clone_url="https://github.com/SAP/terraform-provider-btp",
        repo_path="./gen/docs/",
        file_filter=lambda file_path: file_path.endswith(".md"),
        branch="main",
    )
    log.info("Getting the documents from the GitHub repository ...")
    tf_docs_all = loader.load()

    # Split the documents into chunks
    chunks = split_docs_into_chunks(documents=tf_docs_all)

    # Get the connection to the HANA DB
    connection_to_hana = get_connection_to_hana_db()
    log.info("Connection to HANA DB established")

    # Get the proxy client for the AI Core service
    proxy_client = get_proxy_client("gen-ai-hub")
    # Create the OpenAIEmbeddings object
    embeddings = OpenAIEmbeddings(
        proxy_model_name="text-embedding-ada-002", proxy_client=proxy_client
    )

    # Create the HanaDB object
    db = HanaDB(
        embedding=embeddings, connection=connection_to_hana, table_name=TABLE_NAME
    )

    # Delete already existing documents from the table
    db.delete(filter={})
    log.info("Deleted already existing documents from the table")

    # add the loaded document chunks to the HANA DB
    log.info("Adding the loaded document chunks to the HANA DB ...")
    db.add_documents(chunks)
    log.success("Done!")

    # -------------------------------------------------------------------------------------
    # Validate the documents are loaded correctly
    # -------------------------------------------------------------------------------------
    log.info("Validate the documents are loaded correctly")
    cur = connection_to_hana.cursor()
    cur.execute(f"SELECT VEC_TEXT, VEC_META, TO_NVARCHAR(VEC_VECTOR) FROM {TABLE_NAME} LIMIT 1")

    rows = cur.fetchall()
    print(rows[0][0])  # The text
    print(rows[0][1])  # The metadata
    print(f"{rows[0][2][:100]}...")  # The vector (printing only first 100 characters as it is quite long)
    cur.close()

    log.success("Data ingestion completed.")


if __name__ == "__main__":
    main()
