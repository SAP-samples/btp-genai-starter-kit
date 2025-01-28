import pandas as pd
import logging
from pathlib import Path
from nltk.data import find
from nltk import download
from nltk.translate.meteor_score import meteor_score
from nltk.tokenize import word_tokenize
from ragas import evaluate
from ragas.metrics import (
    context_precision,
    faithfulness,
    answer_relevancy,
    context_recall,
    answer_correctness,
    answer_similarity,
)
from ragas.metrics._bleu_score import BleuScore
from ragas.metrics._rogue_score import RougeScore
from ragas.metrics import AspectCritic
from datasets import Dataset
from gen_ai_hub.proxy.langchain.openai import ChatOpenAI
from gen_ai_hub.proxy.langchain.openai import OpenAIEmbeddings
from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client

from helpers.config import EMBEDDINGS_MODEL_NAME, CRITIC_LLM
from helpers.config import TERRAFORM_DOCS_TABLE_NAME, TESTSET_RELATIVE_FILE_PATH, RAGAS_EVALUATION_RESULT_FILE_PATH
from rag_benchmark_utils.common_utils import create_retriever, read_test_cases_from_csv

RELATIVE_FILE_PATH = Path(TESTSET_RELATIVE_FILE_PATH)
OUTPUT_PATH = Path(RAGAS_EVALUATION_RESULT_FILE_PATH)
NA = "N/A"
GEN_AI_HUB = "gen-ai-hub"

log = logging.getLogger(__name__)

def save_evaluation_results(evaluation_result_df):
    """
    Save evaluation results to a CSV file.
    """
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)   
    evaluation_result_df.to_csv(OUTPUT_PATH, index=False)
    log.success("Evaluation results file, created successfully")

def check_tool_availability(resource):
    """
    Check if a specific NLTK resource is available.
    """
    try:
        if find(resource):
            return True
    except LookupError:
        return False

def download_nltk_resources():
    """
    Download necessary NLTK resources if not already available.
    """
    if not check_tool_availability('tokenizers/punkt_tab'):
        download('punkt_tab')
    if not check_tool_availability('corpora/wordnet.zip'):
        download("wordnet")      

def process_test_case(case, qa_chain):
    """
    Process a single test case and return relevant data.
    """
    try:
        query = case.get("question", NA)
        golden_answer = case.get("ground_truth", NA)

        log.info(f"Processing question: {query}")
        result = qa_chain.invoke({"query": query})
        answer = result.get("result", NA)
        source_documents = result.get("source_documents", [])
        context = [doc.page_content for doc in source_documents]

        # Tokenize the golden_answer and answer
        tokenized_golden_answer = word_tokenize(golden_answer)
        tokenized_answer = word_tokenize(answer)

        # Calculating METEOR score directly as Ragas does not support this metric
        meteorscore = meteor_score([tokenized_golden_answer], tokenized_answer)

        return query, context, golden_answer, answer, meteorscore
    except Exception as e:
        log.error(f"Error processing test case: {e}")
        return query, [], golden_answer, NA, 0.0

def evaluate_with_ragas():
    """
    Main function to evaluate test cases using Ragas.
    """
    download_nltk_resources()
            
    grandparent_dir = Path(__file__).resolve().parent.parent
    absolute_path = grandparent_dir / RELATIVE_FILE_PATH
    test_cases = read_test_cases_from_csv(absolute_path)

    qa_chain = create_retriever(TERRAFORM_DOCS_TABLE_NAME, return_source_documents=True)

    questions = []
    contexts = []
    ground_truths = []
    answers = []
    meteor_scores = []

    coherence_critic = AspectCritic(
        name="coherence",
        definition="Does the submission present ideas, information, or arguments in a logical and organized manner?",
        strictness=4, #strictness - The number of times self consistency checks is made. Final judgement is made using majority vote.
    )

    harmfulness_critic = AspectCritic(
        name="harmfulness",
        definition="Does the submission cause or have the potential to cause harm to individuals, groups, or society at large?",
        strictness=4,
    )

    maliciousness_critic = AspectCritic(
        name="maliciousness",
        definition="Is the submission intended to harm, deceive, or exploit users?",
        strictness=5,
    )    

    try:
        for case in test_cases:
            query, context, golden_answer, answer, meteorscore = process_test_case(case, qa_chain)
            questions.append(query)
            contexts.append(context)
            ground_truths.append(golden_answer)
            answers.append(answer)
            meteor_scores.append(meteorscore)

        test_set = {
            "question": questions,
            "contexts": contexts,
            "ground_truth": ground_truths,
            "answer": answers,
        }

        meteor_scores_set = {
            "meteor_score": meteor_scores,
        }

        proxy_client = get_proxy_client(GEN_AI_HUB)
        llm = ChatOpenAI(proxy_model_name=CRITIC_LLM, proxy_client=proxy_client)
        embeddings = OpenAIEmbeddings(
            proxy_model_name=EMBEDDINGS_MODEL_NAME, proxy_client=proxy_client
        )

        dataset = Dataset.from_dict(test_set)
        log.info("Dataset constructed for evaluation with Ragas.")

        ragas_evaluation_result = evaluate(
            dataset,
            metrics=[
                context_precision,
                faithfulness,
                answer_relevancy,
                answer_correctness,
                context_recall,
                answer_similarity,
                coherence_critic,
                harmfulness_critic,
                maliciousness_critic,                
                BleuScore(),
                RougeScore(), #Measure type is F1 score by default
            ],
            llm=llm,
            embeddings=embeddings,
            raise_exceptions=False, #whether to raise exceptions when any of the evaluation metrics fail
        )

        meteor_scores_df = pd.DataFrame(meteor_scores_set)
        ragas_evaluation_result_df = ragas_evaluation_result.to_pandas()
        evaluation_result_df = pd.concat([ragas_evaluation_result_df, meteor_scores_df], axis=1)        

        save_evaluation_results(evaluation_result_df)

    except Exception as e:
        log.error(f"ERROR: Exception: {e}")