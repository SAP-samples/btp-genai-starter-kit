import logging
import textwrap
import sys
import re
from tabulate import tabulate
from pydantic import BaseModel

from gen_ai_hub.proxy.langchain.openai import ChatOpenAI
from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client

from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

from helpers.config import TERRAFORM_TABLE_NAME, JUDGE_LLM
from helpers.factory import setup_components

log = logging.getLogger(__name__)

class ValidationResult(BaseModel):
    query: str
    actual_answer: str
    rating: float
    reasoning: str

    class Config:
        str_min_length = 1
        str_strip_whitespace = True
        
def create_retriever():
    """
    Creates a RetrievalQA chain for querying HANA DB
    """
    llm, _, db = setup_components(TERRAFORM_TABLE_NAME)
   
    retriever = db.as_retriever(search_kwargs={"k": 5})
    prompt_template = """
    You are a helpful assistant. You are provided multiple context items that are related to the prompt you have to answer.
    Use the following pieces of context to answer the question at the end. If the answer is not in the context, reply exactly with "I don't know".

    ```
    {context}
    ```

    Question: {question}
    """

    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )

    chain_type_kwargs = {"prompt": PROMPT}

    return RetrievalQA.from_chain_type(
        llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs=chain_type_kwargs,
    )

def validate_response(question: str, response: str) -> ValidationResult:
    """
    Use the LLM to validate the response.
    """
    proxy_client = get_proxy_client("gen-ai-hub")

    system_prompt = f"""
    You will be given a user_question by the user.
    Your task is to provide a 'total rating' scoring how well the system_answer answers the user concerns expressed in the user_question.
    Give your answer as a float on a scale of 0 to 10, where 0 means that the system_answer is not helpful at all, and 10 means that the answer completely and helpfully addresses the question.

    Provide your feedback as follows:

    Feedback::: The reason for your rating goes here.
    Total rating: (your rating, as a float between 0 and 10)
    
    Now here is the system_answer to be rated: {response}"""    

    human_prompt = f"""
    user_question: {question}"""

    messages = [
        ("system",system_prompt,),
        ("human", human_prompt),
    ]

    llm = ChatOpenAI(
        proxy_model_name=JUDGE_LLM,
        proxy_client=proxy_client,
        temperature=0,
    )

    try:
        validation_result = llm.invoke(messages)
        log.info(validation_result.content)
        rating_match = re.search(r"Total rating: (\d+(\.\d+)?)", validation_result.content)
        rating = float(rating_match.group(1)) if rating_match else 0.0               
        reasoning = validation_result.content.replace(rating_match.group(0), '').replace("Feedback:::", '').strip() if rating_match else validation_result.content  
        return ValidationResult(
            query=question, 
            actual_answer=response, 
            rating=rating,
            reasoning = reasoning
        )
    except Exception as e:
        log.error(f"Error during response validation: {e}")
        sys.exit("Response validation failed, program exiting.")

def format_text(text, width=40):
    """
    Format text to wrap at a specified width.
    """    
    try:
        return '\n'.join(textwrap.wrap(text, width))
    except Exception as e:
        log.error(f"Error formatting text: {e}")
        return text

def print_results(results):
    """
    Print the results in a tabular format.
    """
    print("""Rated on a scale of 0 to 10, where 0 means that the system answer is not helpful at all, 
and 10 means that the answer completely and helpfully addresses the question.""")
    headers = ["Query", "Actual Answer", "Total rating", "Validation result reasoning"]
    formatted_output = []
    for row in results:
        formatted_row = [format_text(cell) for cell in row]
        formatted_output.append(formatted_row)
    table = tabulate(formatted_output, headers=headers, tablefmt="fancy_grid")     
    print(table)   

def benchmark_accuracy():
    """
    Benchmark the accuracy of the RAG application.
    """
    # Define test queries
    test_cases = [
        {"query": "What is Terraform?"},
        {"query": "How to use Terraform with SAP?"},
        {"query": "Explain the concept of Infrastructure as Code."},
        {"query": "What are the benefits of using Terraform?"},
        {"query": "How to set up a Terraform provider for SAP BTP?"},
    ]

    qa_chain = create_retriever()
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

    print_results(results)