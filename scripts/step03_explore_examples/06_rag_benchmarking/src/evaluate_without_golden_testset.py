import logging

from rag_benchmark_utils.common_utils import create_retriever, validate_response, print_results
from helpers.config import TERRAFORM_DOCS_TABLE_NAME

log = logging.getLogger(__name__)

def evaluate_without_golden_testset():
    """
    Evaluates the RAG application without using a golden test set.
    """
    # Define test queries
    test_cases = [
        {"query": "What is Terraform?"},
        {"query": "How to use Terraform with SAP?"},
        {"query": "Explain the concept of Infrastructure as Code."},
        {"query": "What are the benefits of using Terraform?"},
        {"query": "How to set up a Terraform provider for SAP BTP?"},
    ]

    qa_chain = create_retriever(TERRAFORM_DOCS_TABLE_NAME)
    results = []

    for case in test_cases:
        query = case["query"]

        try:
            log.info(f"Asking question: {query}")
            result = qa_chain.invoke({"query": query})
            actual_answer = result.get("result", "N/A")
            log.info(f"Response: {actual_answer}")
            # Validate the response using the LLM
            validation_result = validate_response(query, actual_answer)
            results.append([query, actual_answer, str(validation_result.rating), validation_result.reasoning])
        except Exception as e:
            log.error(f"Error occurred while asking question: {str(e)}")
            results.append([query, "N/A", "Failed", "Failed"])

    headers = ["Query", "Actual Answer", "Total rating", "Validation result reasoning"]
    print_results(results, headers)