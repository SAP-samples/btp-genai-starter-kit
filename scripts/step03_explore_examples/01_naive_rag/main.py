import logging
import sys

from utils.env import init_env
from utils.hana import teardown_hana_table

from library import (
    ingest,
    fetch_docs,
    create_retriever,
    TABLE_NAME,
)

log = logging.getLogger(__name__)


def chat():
    qa_chain = create_retriever()
    while True:
        question = input("Ask a question or type 'exit' to leave: ")

        # remove spaces from the question
        question = question.strip()

        if question.lower() == "exit":
            print("Goodbye!")
            sys.exit()

        elif not question:
            print("Please provide a question.")
            continue

        try:
            log.info(f"Asking a question: {question}")

            # Invoke the conversational retrieval chain with the user's question
            result = qa_chain.invoke({"question": question})

            # Output the answer from LLM
            log.success("Answer from LLM:")
            print(result["answer"])

            # Output the source document chunks used for the answer
            source_docs = result["source_documents"]
            print("================")
            log.info(f"Number of used source document chunks: {len(source_docs)}")
            for doc in source_docs:
                print("-" * 80)
                log.info(doc.page_content)
                log.info(doc.metadata)
        except Exception as e:
            log.error(f"Error occurred while asking a question: {str(e)}")


def main():
    # Load environment variables
    init_env()

    # -------------------------------------------------------------------------------------
    # Provide the response to the user
    # -------------------------------------------------------------------------------------

    print("Welcome to the interactive Q&A session\n")

    while True:
        print("0: Clean up database")
        print("1: Ingest data")
        print("2: Retrieve data")
        print("3: Exit\n")

        option = input("Which task would you like to run?").strip()

        if option == "0":
            teardown_hana_table(TABLE_NAME)
            continue
        elif option == "1":
            docs = fetch_docs()
            try:
                ingest(docs)
            except Exception as e:
                log.error(f"Error occurred while ingesting data: {str(e)}")
            continue
        elif option == "2":
            chat()
            break
        elif option == "3":
            print("Goodbye!")
            sys.exit()
        else:
            print("Invalid input. Please choose an option from the list above.")


if __name__ == "__main__":
    main()
