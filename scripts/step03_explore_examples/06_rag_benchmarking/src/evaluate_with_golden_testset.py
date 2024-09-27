import logging
import sys
import csv
from pathlib import Path

from rag_benchmark_utils.common_utils import create_retriever, validate_response, print_results
from helpers.config import TERRAFORM_DOCS_TABLE_NAME

RELATIVE_FILE_PATH = Path("data/golden_test_set.csv")

log = logging.getLogger(__name__)

def read_test_cases_from_csv(file_path):
    """
    Reads test cases from a CSV file.
    """
    test_cases = []
    try:
        file_path = Path(file_path)
        with file_path.open(mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                test_cases.append(
                    {
                        "question": row.get("question"),
                        "ground_truth": row.get("ground_truth"),
                    }
                )
    except Exception as e:
        log.error(f"Error reading CSV file: {e}")
        sys.exit("Failed to read test cases from CSV file, program exiting.")
    return test_cases

def evaluate_with_golden_testset():
    """
    Evaluate the RAG application using the golden test set.
    """
    grandparent_dir = Path(__file__).resolve().parent.parent
    absolute_path = grandparent_dir / RELATIVE_FILE_PATH
    test_cases = read_test_cases_from_csv(absolute_path)

    qa_chain = create_retriever(TERRAFORM_DOCS_TABLE_NAME)
    results = []
    total_questions = len(test_cases)
    total_rating = 0

    for case in test_cases:
        query = case.get("question", "N/A")
        golden_answer = case.get("ground_truth", "N/A")

        try:
            log.info(f"Asking question: {query}")
            result = qa_chain.invoke({"query": query})
            actual_answer = result.get("result", "N/A")
            log.info(f"Response: {actual_answer}")            
            context = result.get("source_documents")
            # Validate the response using the LLM
            validation_result = validate_response(query, actual_answer, golden_answer, context)
            total_rating = total_rating + validation_result.answer_correctness
            results.append(
                [
                    query,
                    actual_answer,
                    golden_answer,
                    str(validation_result.answer_correctness),
                    str(validation_result.answer_faithfulness),
                    str(validation_result.answer_relevance),
                    str(validation_result.context_relevance),
                    validation_result.reasoning,
                ]
            )
        except Exception as e:
            log.error(f"Error occurred while asking question: {str(e)}")
            results.append(
                [
                    query,
                    "N/A",
                    golden_answer,
                    "Failed",
                    "Failed",
                    "Failed",
                    "Failed",
                    "Failed",
                ]
            )

    accuracy = (total_rating / total_questions) * 100
    headers = [
        "Query",
        "Actual Answer",
        "Reference/Golden Answer",
        "Answer Correctness",
        "Answer Faithfulness",
        "Answer Relevance",
        "Context Relevance",
        "Validation result reasoning",
    ]
    column_width = {
        "Query": 30,
        "Actual Answer": 30,
        "Reference/Golden Answer": 30,
        "Answer Correctness": 10,
        "Answer Faithfulness": 10,
        "Answer Relevance": 10,
        "Context Relevance": 10,
        "Validation result reasoning": 40,
    }    
    print_results(results, headers, accuracy, column_width)    