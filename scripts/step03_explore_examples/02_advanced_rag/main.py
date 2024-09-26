import logging
import sys

from utils.env import init_env
from utils.hana import teardown_hana_table as execute_teardown_hana_table

from helpers.config import (
    SAP_DOCS_TABLE_NAME,
    PODCASTS_TABLE_NAME,
)

from src import (
    execute_ingestion,
    execute_rag_fusion,
    execute_rewrite_retrieve_read,
    execute_self_query,
    execute_split_data,
    execute_hana_self_query,
)

log = logging.getLogger(__name__)


def main():
    # Load environment variables
    init_env()

    # -------------------------------------------------------------------------------------
    # Provide the response to the user
    # -------------------------------------------------------------------------------------

    print("Welcome to the interactive Q&A session\n")
    while True:
        print("0: Prerequisite - Clean up database")
        print("1: Prerequisite - Ingest sample data")
        print("2: Advanced RAG - Compare Splitter Methods")
        print("3: Advanced RAG - Self Query")
        print("4: Advanced RAG - Rewrite Retrieve Read")
        print("5: Advanced RAG - RAG Fusion")
        print("6: Advanced RAG - HANA Self Query")
        print("7: Exit\n")

        option = input("Which task would you like to run?").strip()

        if option == "0":
            execute_teardown_hana_table(SAP_DOCS_TABLE_NAME)
            execute_teardown_hana_table(PODCASTS_TABLE_NAME)
            continue
        elif option == "1":
            execute_ingestion()
            continue
        elif option == "2":
            execute_split_data()
            continue
        elif option == "3":
            execute_self_query()
            continue
        elif option == "4":
            execute_rewrite_retrieve_read()
            continue
        elif option == "5":
            execute_rag_fusion()
            continue
        elif option == "6":
            execute_hana_self_query()
            continue
        elif option == "7":
            print("Goodbye!")
            sys.exit()
        else:
            print("Invalid input. Please choose an option from the list above.")


if __name__ == "__main__":
    main()
