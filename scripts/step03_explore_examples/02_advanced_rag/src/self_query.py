import logging
from typing import Optional

from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field

from utils.env import init_env

from helpers.config import PODCASTS_TABLE_NAME
from helpers.factory import setup_components

log = logging.getLogger(__name__)


def main():
    llm, _, db = setup_components(PODCASTS_TABLE_NAME)
    question = "What is the summary of the episode 65?"

    print("Without database filtering based on user query")
    qa_documents_with_filters(db, llm, question)

    print("With database filtering based on user query")
    podcast = extract_podcast_title_from_question(llm, question)

    advanced_db_filter = {"title": {"$like": f"%{podcast.title()}%"}}
    qa_documents_with_filters(db, llm, question, advanced_db_filter)

    log.success("""Self querying completed successfully!
                Now try to ask 'What is the summary of the episode 67?' and notice how self-querying can help to avoid hallucination.
                """)


# Extract the podcast title from the questionp
def extract_podcast_title_from_question(llm, question):
    class Podcast(BaseModel):
        title: Optional[str] = Field(
            default=None, description="The title or the episode number of the podcast"
        )

    # Define the prompt to extract data from user query
    system_template = """
    You are an expert extraction algorithm.
    Only extract relevant information from the question below.
    If you do not know the value of an attribute asked to extract,
    return null for the attribute's value.

    Text: {question}
    """

    prompt = PromptTemplate(template=system_template, input_variables=["question"])

    runnable = prompt | llm.with_structured_output(schema=Podcast)
    podcast = runnable.invoke({"question": question})
    print("Podcast Title:", podcast.title)
    return podcast.title


# Generate the answer to the question using retrieved documents and applied filters
def qa_documents_with_filters(db, llm, question, advanced_db_filter=None):
    qa_prompt_template = """
    You are an expert in SAP podcasts topics. You are provided multiple context items that are related to the prompt you have to answer.
    Use the following pieces of context to answer the question at the end.

    '''
    {context}
    '''

    Question: {question}
    """

    prompt = PromptTemplate(
        template=qa_prompt_template, input_variables=["context", "question"]
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm,
        chain_type="stuff",
        retriever=db.as_retriever(search_kwargs={"k": 5, "filter": advanced_db_filter}),
        return_source_documents=True,
        verbose=True,
        chain_type_kwargs={"prompt": prompt},
    )

    result = qa_chain.invoke({"query": question})

    print("Source Documents:")
    for doc in result["source_documents"]:
        print("Title:", doc.metadata["title"], " Page Number:", doc.metadata["page"])

    print("Result:", result["result"])


if __name__ == "__main__":
    # Load environment variables
    init_env()
    main()
