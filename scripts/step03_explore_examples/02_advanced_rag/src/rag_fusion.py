import logging

from langchain.load import dumps, loads
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

from utils.env import init_env

from helpers.config import SAP_DOCS_TABLE_NAME
from helpers.factory import setup_components

log = logging.getLogger(__name__)


def execute_rag_fusion():
    llm, _, db = setup_components(SAP_DOCS_TABLE_NAME)

    template = """
        Answer the question in detail and as truthfully as possible based only on the provided context. If you're unsure of the question or answer, say "Sorry, I don't know".
        <context>
        {context}
        </context>

        Question: {original_query}
    """

    prompt = ChatPromptTemplate.from_template(template)

    retriever = db.as_retriever(k=5)

    original_query = "Cloud Foundry, Kyma or what?"

    print("Invoke query without RAG Fusion")
    qa_without_fusion(llm, original_query, prompt, retriever)

    print("Invoke query with RAG Fusion")
    qa_with_rag_fusion(llm, original_query, prompt, retriever)

    log.success("RAG Fusion successfully completed.")


# Question answering without RAG Fusion
def qa_without_fusion(llm, original_query, prompt, retriever):
    chain = (
        {"context": retriever, "original_query": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    print("Query before rewrite: ", original_query)

    result = chain.invoke(original_query)
    print("QA result without query rewrite: ", result)
    return result


# Question answering with RAG Fusion
def qa_with_rag_fusion(llm, original_query, original_prompt, retriever):
    fusion_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful assistant that generates multiple search queries based on a single input query.",
            ),
            ("user", "Generate multiple search queries related to: {original_query}"),
            ("user", "OUTPUT (4 queries):"),
        ]
    )

    def print_and_split(generated_queries: str):
        print("Generated queries: ", generated_queries)
        return generated_queries.split("\n")

    # Define the pipeline that generates multiple search queries based on a single input query
    chain = (
        {
            "context": {
                "question_to_rewrite": RunnablePassthrough()
                | fusion_prompt
                | llm
                | StrOutputParser()
                | print_and_split
                | retriever.map()
                | reciprocal_rank_fusion
            },
            "original_query": RunnablePassthrough(),
        }
        | original_prompt
        | llm
        | StrOutputParser()
    )

    result = chain.invoke(original_query)

    print("Result with RAG Fusion: ", result)


# Define the reciprocal rank fusion function that combines the results from multiple retrievers into a single ranked list
def reciprocal_rank_fusion(results: list[list], k=60):
    fused_scores = {}
    for docs in results:
        for rank, doc in enumerate(docs):
            doc_str = dumps(doc)
            fused_scores.setdefault(doc_str, 0)
            fused_scores[doc_str] += 1 / (rank + k)

    reranked_results = [
        (loads(doc), score)
        for doc, score in sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)
    ]
    return reranked_results


