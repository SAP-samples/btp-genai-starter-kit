import logging

from helpers.config import PODCASTS_TABLE_NAME
from helpers.factory import setup_components
from langchain.chains import RetrievalQA
from langchain.chains.query_constructor.base import AttributeInfo
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain_community.query_constructors.hanavector import HanaTranslator
from utils.env import init_env

log = logging.getLogger(__name__)


def main():
    llm, _, db = setup_components(PODCASTS_TABLE_NAME)
    question = "What is the summary of the episode 65?"

    print("=" * 10, "User query without database filtering", "=" * 10)
    qa_documents_with_filters(db, llm, question)

    print("=" * 10, "Performing HANA Self query", "=" * 10)
    qa_with_hana_self_query(db, llm, question)

    log.info(
        "Self querying completed successfully! Now try to ask 'What is the summary of the episode 67?' and notice how self-querying can help to avoid hallucination."
    )


def qa_with_hana_self_query(db, llm, query):
    """
    Perform a self-query using HANA and the provided LLM.

    Args:
        db: The database object.
        llm: The language model object.
        query: The query string.
    """
    try:
        metadata_field_info = [
            AttributeInfo(
                name="podcast_title", description="Title of the Podcast", type="string"
            ),
            AttributeInfo(
                name="episode",
                description="Episode number of the Podcast",
                type="integer",
            ),
        ]

        document_content_description = "A collection of podcasts from the SAP podcast."
        hana_translator = HanaTranslator()

        retriever = SelfQueryRetriever.from_llm(
            llm,
            db,
            document_content_description,
            metadata_field_info,
            structured_query_translator=hana_translator,
        )

        docs = retriever.invoke(input=query)
        log.info(f"Running the query: {query}")
        log.info("Source document metadata below\n")
        for doc in docs:
            log.info("-" * 80)
            log.info(
                f"Podcast title: {doc.metadata['podcast_title']}\nEpisode: {doc.metadata['episode']}"
            )

        # Concatenate the content of the retrieved documents
        context = " ".join(doc.page_content for doc in docs)
        system_message = f"You are a helpful assistant. Use the following context to answer the user query:\n{context}"
        human_message = query
        messages = [
            ("system", system_message),
            ("human", human_message),
        ]

        answer = llm.invoke(messages)
        log.info("Answer to the query:")
        log.info(answer.content)
    except Exception as e:
        log.error(f"Error performing query: {str(e)}")


def qa_documents_with_filters(db, llm, question, advanced_db_filter=None):
    """
    Generate the answer to the question using retrieved documents and applied filters.

    Args:
        db: The database object.
        llm: The language model object.
        question: The question string.
        advanced_db_filter: Optional filter to apply to the database query.
    """
    try:
        system_template = """
        You are an expert in SAP podcasts topics. You are provided multiple context items that are related to the 
        prompt you have to answer.
        Use the following pieces of context to answer the question at the end.
        '''
        {context}
        '''
        """

        human_template = "{question}"

        messages = [
            SystemMessagePromptTemplate.from_template(system_template),
            HumanMessagePromptTemplate.from_template(human_template),
        ]

        prompt = ChatPromptTemplate.from_messages(messages)

        qa_chain = RetrievalQA.from_chain_type(
            llm,
            chain_type="stuff",
            retriever=db.as_retriever(
                search_kwargs={"k": 5, "filter": advanced_db_filter}
            ),
            return_source_documents=True,
            verbose=True,
            chain_type_kwargs={"prompt": prompt},
        )

        result = qa_chain.invoke({"query": question})

        log.info("Source Documents:")
        for doc in result["source_documents"]:
            log.info(
                f"Title: {doc.metadata['title']} Page Number: {doc.metadata['page']}"
            )

        log.info(f"Result: {result['result']}")
    except Exception as e:
        log.error(f"Error during QA chain execution: {str(e)}")


if __name__ == "__main__":
    # Load environment variables
    init_env()
    main()
