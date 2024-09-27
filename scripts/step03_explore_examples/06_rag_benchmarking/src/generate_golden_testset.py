import logging
from pathlib import Path
from ragas.testset.generator import TestsetGenerator
from ragas.testset.evolutions import simple, reasoning, multi_context
from gen_ai_hub.proxy.langchain.openai import ChatOpenAI
from gen_ai_hub.proxy.langchain.openai import OpenAIEmbeddings
from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client

from helpers.config import EMBEDDINGS_MODEL_NAME, CRITIC_LLM, TEST_SIZE, GENERATOR_LLM
from utils.ingest_docs import fetch_terraform_docs

GEN_AI_HUB = "gen-ai-hub"
DISTRIBUTIONS = {
    simple: 0.5,
    multi_context: 0.4,
    reasoning: 0.1
}
OUTPUT_PATH = Path('data/golden_test_set.csv')

logger = logging.getLogger(__name__)

def generate_golden_testset():
    """
    Generate a golden test set from documents in a Git repository using Ragas.
    """    
    try:
        documents = fetch_terraform_docs()
        logger.info(f"Total documents loaded: {len(documents)}")

        proxy_client = get_proxy_client(GEN_AI_HUB)
        
        generator_llm = ChatOpenAI(proxy_model_name=GENERATOR_LLM, proxy_client=proxy_client)
        critic_llm = ChatOpenAI(proxy_model_name=CRITIC_LLM, proxy_client=proxy_client)
        embeddings = OpenAIEmbeddings(proxy_model_name=EMBEDDINGS_MODEL_NAME, proxy_client=proxy_client)

        generator = TestsetGenerator.from_langchain(
            generator_llm,
            critic_llm,
            embeddings
        )

        testset = generator.generate_with_langchain_docs(documents, test_size=TEST_SIZE, distributions=DISTRIBUTIONS) 
        test_df =testset.to_pandas()
        logger.info(f"Generated test set:\n{test_df.head()}")

        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        test_df.to_csv(OUTPUT_PATH, index=False)
        logger.success(f"Test set saved to {OUTPUT_PATH}")
        
    except Exception as e:
        logger.error(f"An error occurred: {e}")