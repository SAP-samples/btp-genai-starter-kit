from gen_ai_hub.proxy.langchain.openai import ChatOpenAI
from gen_ai_hub.proxy.langchain.openai import OpenAIEmbeddings
from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client
from .config import LLM_MODEL_NAME, EMBEDDINGS_MODEL_NAME
from langchain_core.rate_limiters import InMemoryRateLimiter


def create_llm_and_embeddings():
    # Get the proxy client for the AI Core service
    proxy_client = get_proxy_client("gen-ai-hub")

    rate_limiter = InMemoryRateLimiter(
        requests_per_second=0.5,  # We can only make a request once every 5 seconds
        check_every_n_seconds=0.1,  # Wake up every 100 ms to check whether allowed to make a request,
        max_bucket_size=10,  # Controls the maximum burst size.
    )

    llm = ChatOpenAI(
        proxy_model_name=LLM_MODEL_NAME,
        proxy_client=proxy_client,
        temperature=0,
        rate_limiter=rate_limiter,
    )

    embeddings = OpenAIEmbeddings(
        proxy_model_name=EMBEDDINGS_MODEL_NAME,
        proxy_client=proxy_client,
        show_progress_bar=True,
    )
    return llm, embeddings
