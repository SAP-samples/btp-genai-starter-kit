import sys
from logging import getLogger

# local dependencies
from utils.env import init_env
from utils.hana import teardown_hana_table

from library import (
    create_llm_and_embeddings,
    ingest,
    create_agent,
    create_retriever,
    STRUCTURED_DATA_TABLE_NAME,
    VECTOR_EMBEDDINGS_TABLE_NAME,
)

log = getLogger(__name__)


def main():
    init_env()

    print("Welcome to the interactive Q&A session!\n")

    def ask():
        while True:
            llm, embeddings = create_llm_and_embeddings()
            retriever = create_retriever(embeddings)
            agent_executor = create_agent(llm, retriever)

            question = input("Ask a question or type 'exit' to leave: ")

            if question.lower() == "exit":
                break

            log.info(f"Asking a question: {question}")
            agent_executor.invoke({"input": question})

    while True:
        print("0: Clean up database")
        print("1: Ingest data")
        print("2: Retrieve data")
        print("3: Exit\n")

        option = input("Which task would you like to run? ").strip()

        if option == "0":
            teardown_hana_table(STRUCTURED_DATA_TABLE_NAME)
            teardown_hana_table(VECTOR_EMBEDDINGS_TABLE_NAME)
            continue
        elif option == "1":
            ingest()
            continue
        elif option == "2":
            ask()
            continue
        elif option == "3":
            print("Goodbye!")
            sys.exit()
        else:
            print("Invalid input. Please choose an option from the list above.")


if __name__ == "__main__":
    main()
