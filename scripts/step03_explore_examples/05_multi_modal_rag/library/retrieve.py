import sys
from logging import getLogger
from utils.hana import (
    get_connection_to_hana_db,
)
from langchain.schema.runnable import RunnablePassthrough
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain_community.vectorstores.hanavector import HanaDB
from langchain.storage import InMemoryStore
from langchain.retrievers.multi_vector import MultiVectorRetriever
from .config import TABLE_NAME, ID_KEY

log = getLogger(__name__)


def create_retriever(embeddings):
    assert TABLE_NAME, "TABLE_NAME is not defined. Please define it before proceeding."

    try:
        # Initialize the vector store and storage layer
        connection_to_hana = get_connection_to_hana_db()

        vectorstore = HanaDB(
            embedding=embeddings,
            connection=connection_to_hana,
            table_name=TABLE_NAME,
        )

        store = InMemoryStore()

        # Initialize the retriever
        retriever = MultiVectorRetriever(
            vectorstore=vectorstore,
            docstore=store,
            id_key=ID_KEY,
            search_kwargs={"k": 10},
        )
        return retriever
    except Exception as e:
        log.error(f"An error occurred while creating the retriever: {str(e)}")
        sys.exit()


def ask(llm, retriever):
    template = """Answer the question based only on the following context, which can include text, images and tables:
        {context}
        Question: {question}
    """
    prompt = ChatPromptTemplate.from_template(template)

    chain = (
        {
            "context": retriever,
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    log.header(
        "Welcome to the interactive Q&A session! Type 'exit' to end the session."
    )
    while True:
        # Prompt the user for a question
        question = input("Please ask a question or type 'exit' to leave: ")

        # Check if the user wants to exit
        if question.lower() == "exit":
            break

        log.info(
            f"Asking a question: {question}",
        )

        # Invoke the conversational retrieval chain with the user's question
        # Output the answer from LLM
        log.success("Answer from LLM:")
        result = chain.invoke(question)
        print(result)
