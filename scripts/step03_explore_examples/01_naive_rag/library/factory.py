from gen_ai_hub.proxy.langchain.openai import ChatOpenAI
from gen_ai_hub.proxy.langchain.openai import OpenAIEmbeddings
from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client
from .config import LLM_MODEL_NAME, EMBEDDINGS_MODEL_NAME


def create_llm_and_embeddings():
    # Get the proxy client for the AI Core service
    proxy_client = get_proxy_client("gen-ai-hub")

    llm = ChatOpenAI(
        proxy_model_name=LLM_MODEL_NAME, proxy_client=proxy_client, temperature=0
    )
    embeddings = OpenAIEmbeddings(
        proxy_model_name=EMBEDDINGS_MODEL_NAME, proxy_client=proxy_client
    )
    return llm, embeddings
