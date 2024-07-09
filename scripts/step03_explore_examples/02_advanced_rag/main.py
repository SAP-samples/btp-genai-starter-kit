import logging
import sys

from utils.env import init_env
from utils.hana import teardown_hana_table

from helpers.config import (
    SAP_DOCS_TABLE_NAME,
    PODCASTS_TABLE_NAME,
)

from src import (
    ingest_main,
    rag_fusion_main,
    rewrite_retrieve_read_main,
    self_query_main,
    split_data_main,
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
        print("6: Exit\n")

        option = input("Which task would you like to run?").strip()

        if option == "0":
            teardown_hana_table(SAP_DOCS_TABLE_NAME)
            teardown_hana_table(PODCASTS_TABLE_NAME)
            continue
        elif option == "1":
            ingest_main()
            continue
        elif option == "2":
            split_data_main()
            continue
        elif option == "3":
            self_query_main()
            break
        elif option == "4":
            rewrite_retrieve_read_main()
            break
        elif option == "5":
            rag_fusion_main()
            break
        elif option == "6":
            print("Goodbye!")
            sys.exit()
        else:
            print("Invalid input. Please choose an option from the list above.")


if __name__ == "__main__":
    main()
