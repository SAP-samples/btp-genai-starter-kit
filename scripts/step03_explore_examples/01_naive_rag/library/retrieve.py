import logging

from langchain_community.vectorstores.hanavector import HanaDB
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory

from utils.hana import get_connection_to_hana_db

from .factory import create_llm_and_embeddings
from .config import TABLE_NAME

log = logging.getLogger(__name__)


def create_retriever():
    connection_to_hana = get_connection_to_hana_db()
    llm, embeddings = create_llm_and_embeddings()

    db = HanaDB(
        embedding=embeddings, connection=connection_to_hana, table_name=TABLE_NAME
    )

    # -------------------------------------------------------------------------------------
    # Fetch the data from the HANA DB and use it to answer the question using the
    # best 2 matching information chunks
    # -------------------------------------------------------------------------------------

    # Create a retriever instance of the vector store
    retriever = db.as_retriever(search_kwargs={"k": 2})
    # Create prompt template
    prompt_template = """
    You are a helpful assistant. You are provided multiple context items that are related to the prompt you have to answer.
    Use the following pieces of context to answer the question at the end. If the answer is not in the context, reply exactly with "I don't know".

    ```
    {context}
    ```

    Question: {question}
    """

    memory = ConversationBufferMemory(
        memory_key="chat_history", output_key="answer", return_messages=True
    )

    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )

    chain_type_kwargs = {"prompt": PROMPT}

    # Create a conversational retrieval chain
    return ConversationalRetrievalChain.from_llm(
        llm,
        retriever,
        return_source_documents=True,
        memory=memory,
        verbose=False,
        combine_docs_chain_kwargs=chain_type_kwargs,
    )
