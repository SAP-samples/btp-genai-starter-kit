import sys

from utils.env import init_env
from utils.hana import teardown_hana_table as execute_teardown_hana_table
from helpers.config import TERRAFORM_DOCS_TABLE_NAME
from src import (
    execute_ingestion,
    generate_golden_testset,
    evaluate_without_golden_testset,
    evaluate_with_golden_testset,
)

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
        print("2: RAG Benchmarking with LLM-as-a-judge")        
        print("3: Generate Golden Test Set")
        print("4: RAG Benchmarking with LLM-as-a-judge using golden test set")        
        print("5: Exit\n")

        option = input("Which task would you like to run?").strip()

        if option == "0":
            execute_teardown_hana_table(TERRAFORM_DOCS_TABLE_NAME)
            continue
        elif option == "1":
            execute_ingestion()
            continue
        elif option == "2":
            evaluate_without_golden_testset()
            continue        
        elif option == "3":
            generate_golden_testset()
            continue
        elif option == "4":
            evaluate_with_golden_testset()
            continue        
        elif option == "5":
            print("Goodbye!")
            sys.exit()
        else:
            print("Invalid input. Please choose an option from the list above.")

if __name__ == "__main__":
    main()