import logging
import textwrap
import re
import sys
from tabulate import tabulate
from pydantic import BaseModel, ConfigDict
from gen_ai_hub.proxy.langchain.openai import ChatOpenAI
from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import csv
from pathlib import Path

from helpers.factory import setup_components
from helpers.config import CRITIC_LLM

log = logging.getLogger(__name__)

GEN_AI_HUB = "gen-ai-hub"
DEFAULT_COLUMN_WIDTH = 40

class ValidationResult(BaseModel):
    query: str
    actual_answer: str
    rating: float = None
    reasoning: str
    golden_answer: str = None
    answer_correctness: float = None
    answer_faithfulness: float = None
    answer_relevance: float = None
    context_relevance: float = None

    model_config = ConfigDict(str_min_length=1, str_strip_whitespace=True)    

def create_retriever(table_name, return_source_documents=False):
    """
    Creates a RetrievalQA chain for querying HANA DB
    """
    llm, _, db = setup_components(table_name)
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
        return_source_documents=return_source_documents,
        chain_type_kwargs=chain_type_kwargs,
    )

def format_text(text, width):
    """
    Format text to wrap at a specified width.
    """    
    try:
        return '\n'.join(textwrap.wrap(text, width))
    except Exception as e:
        log.error(f"Error formatting text: {e}")
        return text

def print_results(results, headers, accuracy=None, column_width=None):
    """
    Print the results in a tabular format.
    """
    if accuracy is not None:
        print("Answer correctness, Answer faithfulness, Answer relevance and Context relevance are rated on a scale of 0 to 1")        
        print(f"Accuracy (expressed here as average Answer Correctnes): {accuracy:.2f} %")
    else:
        print("""Rated on a scale of 0 to 10, where 0 means that the system answer is not helpful at all, 
and 10 means that the answer completely and helpfully addresses the question.""")

    formatted_output = []
    for row in results:
        formatted_row = [
            format_text(row[i], width=column_width[headers[i]] if column_width else DEFAULT_COLUMN_WIDTH)
            for i in range(len(headers))
        ]
        formatted_output.append(formatted_row)
    table = tabulate(formatted_output, headers=headers, tablefmt="fancy_grid")
    print(table)

def extract_metric(pattern, text):
    """
    Extracts a float value from the text using the given regex pattern.
    """
    match = re.search(pattern, text)
    return float(match.group(1)) if match else 0.0, match

def sanitize_content(content, matches):
    """
    Sanitizes the provided content by removing all substrings that match the given regex patterns.
    """
    for match in matches:
        if match:
            content = content.replace(match.group(0), "")
    return content.strip()    

def validate_response(question: str, response: str, golden_answer: str = None, context: list = None) -> ValidationResult:
    """
    Use the LLM to validate the response.
    """
    proxy_client = get_proxy_client(GEN_AI_HUB)

    if golden_answer:
        system_prompt = f"""
        Please act as an impartial judge and compare system_answer with the golden_answer for user_question provided.
        Provide a 'Answer correctness' scoring how well the system_answer matches the golden_answer and addresses the user concerns expressed in the user_question.
        Give your answer as a float on a scale of 0 to 1, where 0 means that the system_answer is not helpful at all, and 1 means that the answer completely and helpfully addresses the question and matches the golden_answer.
        - The golden answer is the fact-based benchmark and shall be assumed as almost perfect answer for your evaluation.  
        - Semantic similarity and factual similarity between the system_answer and the golden_answer should be the most important criteria for the evaluation.

        Provide your feedback as follows:

        Feedback::: The reason for your rating goes here.
        Answer correctness: (your rating, as a float between 0 and 1)

        Also, please provide the following metrics:
        - Answer faithfulness as number calculated as following: The system_answer is regarded as faithful if all the claims made in the answer can be inferred from the given context. Give verdict as a float between 0 (not faithful at all) and 1 (extremely faithful).
        - Answer relevance as number calculated as following: The system_answer is deemed relevant when it directly and appropriately addresses the user_question.
        - Context relevance as the number of sentences from the context that are relevant to the user_question with self-consistency checks, in the relation to the overall number of sentences in the context. Provide it as a float between 0 (not relevant) and 1 (extremely relevant).
        
        Now here is the system_answer to be rated: {response}
        here is the golden_answer: {golden_answer}
        and here is the context: {context}"""
    else:
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
        proxy_model_name=CRITIC_LLM,
        proxy_client=proxy_client,
        temperature=0,
    )

    try:
        validation_result = llm.invoke(messages)
        log.info(validation_result.content)

        if golden_answer:
            answer_correctness_pattern = r"Answer correctness: (0(\.\d+)?|1(\.0+)?)"
            faithfulness_pattern = r"- Answer faithfulness: (0(\.\d+)?|1(\.0+)?)"
            context_relevance_pattern = r"- Context relevance: (0(\.\d+)?|1(\.0+)?)"
            answer_relevance_pattern = r"- Answer relevance: (0(\.\d+)?|1(\.0+)?)"

            answer_correctness, answer_correctness_match = extract_metric(answer_correctness_pattern, validation_result.content)
            answer_faithfulness, faithfulness_match = extract_metric(faithfulness_pattern, validation_result.content)
            context_relevance, context_relevance_match = extract_metric(context_relevance_pattern, validation_result.content)
            answer_relevance, answer_relevance_match = extract_metric(answer_relevance_pattern, validation_result.content)

            matches = [answer_correctness_match, faithfulness_match, context_relevance_match, answer_relevance_match]
            reasoning = (sanitize_content(validation_result.content, matches).replace("Feedback:::", "").strip())

            return ValidationResult(
                query=question,
                actual_answer=response,
                golden_answer=golden_answer,
                answer_correctness=answer_correctness,
                answer_faithfulness=answer_faithfulness,
                answer_relevance=answer_relevance,
                context_relevance=context_relevance,
                reasoning=reasoning,
            )
        else:
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