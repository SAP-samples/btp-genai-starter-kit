import sys
import logging
from library.config import (
    LLM_MODEL_NAME,
    EMBEDDINGS_MODEL_NAME,
)

from utils.env import init_env
from library import (
    ingest_data_with_unstructured,
    create_retriever,
    ask
)
from gen_ai_hub.proxy.langchain.openai import ChatOpenAI
from gen_ai_hub.proxy.langchain.openai import OpenAIEmbeddings
from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client

log = logging.getLogger(__name__)


# This function loads the documents into the HANA DB to get them vectorized and validates the documents are loaded correctly
def main():
    # Load environment variables
    init_env()
    # Get the proxy client for the AI Core service
    proxy_client = get_proxy_client("gen-ai-hub")

    # Initialize the LLM and embeddings
    llm = ChatOpenAI(
        proxy_model_name=LLM_MODEL_NAME, proxy_client=proxy_client, temperature=0
    )
    embeddings = OpenAIEmbeddings(
        proxy_model_name=EMBEDDINGS_MODEL_NAME, proxy_client=proxy_client
    )

    # Initialize the retriever
    retriever = create_retriever(embeddings)

    while True:
        print("0: Clean up database")
        print("1: Ingest data with Unstructured")
        print("2: Retrieve data")
        print("3: Exit\n")

        option = input("Which task would you like to run? ").strip()

        if option == "0":
            retriever.vectorstore.delete(filter={})
            continue
        if option == "1":
            ingest_data_with_unstructured(llm, retriever)
            continue
        elif option == "2":
            ask(llm, retriever)
            break
        elif option == "3":
            print("Goodbye!")
            sys.exit()
        else:
            print("Invalid input. Please choose an option from the list above.")


if __name__ == "__main__":
    main()
