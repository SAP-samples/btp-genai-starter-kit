import logging
import sys
from langchain_community.vectorstores.hanavector import HanaDB
from gen_ai_hub.proxy.langchain.openai import ChatOpenAI
from gen_ai_hub.proxy.langchain.openai import OpenAIEmbeddings
from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client

from utils.hana import get_connection_to_hana_db
from .config import LLM_MODEL_NAME, EMBEDDINGS_MODEL_NAME

log = logging.getLogger(__name__)

def setup_components(table_name, model_name=None, embeddings_model_name=None):
    try:
        model_name = model_name or LLM_MODEL_NAME
        embeddings_model_name = embeddings_model_name or EMBEDDINGS_MODEL_NAME

        assert table_name, "Table name is required"
        assert model_name, "LLM_MODEL_NAME is required"
        assert embeddings_model_name, "EMBEDDINGS_MODEL_NAME is required"

        connection = get_connection_to_hana_db()

        # Get the proxy client for the AI Core service
        proxy_client = get_proxy_client("gen-ai-hub")

        llm = ChatOpenAI(
            proxy_model_name=LLM_MODEL_NAME, proxy_client=proxy_client, temperature=0
        )

        embeddings = OpenAIEmbeddings(
            proxy_model_name=EMBEDDINGS_MODEL_NAME, proxy_client=proxy_client
        )

        db = HanaDB(embedding=embeddings, connection=connection, table_name=table_name)

        return llm, embeddings, db
    except Exception as e:
        log.error(f"Failed to setup components: {e}")
        sys.exit()