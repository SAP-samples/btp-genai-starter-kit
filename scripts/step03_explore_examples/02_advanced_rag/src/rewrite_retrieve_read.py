import logging

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

from helpers.factory import setup_components
from helpers.config import SAP_DOCS_TABLE_NAME


log = logging.getLogger(__name__)


def execute_rewrite_retrieve_read():
    print("Rewrite, retrieve, and read")

    llm, _, db = setup_components(SAP_DOCS_TABLE_NAME)

    template = """
        Answer the question in detail and as truthfully as possible based only on the provided context. If you're unsure of the question or answer, say "Sorry, I don't know".
        <context>
        {context}
        </context>

        Question: {question}
    """

    prompt = ChatPromptTemplate.from_template(template)

    def retriever(query):
        retrieved_chunks = db.similarity_search(query, k=5)
        return retrieved_chunks

    simple_query = "Cloud Foundry, Kyma or what?"

    print("QA without query rewrite")
    invoke_query_without_rewrite(llm, simple_query, prompt, retriever)

    print("QA with query rewrite")
    invoke_query_with_rewrite(llm, simple_query, prompt, retriever)

    log.success("Rewrite, retrieve, and read successfully completed.")


def invoke_query_without_rewrite(llm, simple_query, prompt, retriever):
    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    print("Query before rewrite: ", simple_query)

    result = chain.invoke(simple_query)
    print("QA result without query rewrite: ", result)
    return result


def invoke_query_with_rewrite(llm, simple_query, prompt, retriever):
    template = """Provide a better query for
    the database similarity retrieval and large language model to answer the given question.
    Question: {question_to_rewrite}
    Answer:"""
    rewrite_prompt = ChatPromptTemplate.from_template(template)

    def rewritten_query(rewritten_query: str):
        print("Query after rewrite: ", rewritten_query)
        return rewritten_query

    rewriter = rewrite_prompt | llm | StrOutputParser()

    rewrite_retrieve_read_chain = (
        rewriter
        | {
            "context": {"question_to_rewrite": RunnablePassthrough() | retriever},
            "question": RunnablePassthrough() | rewritten_query,
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    rewritten_result = rewrite_retrieve_read_chain.invoke(simple_query)
    print("QA result after query rewrite: ", rewritten_result)
