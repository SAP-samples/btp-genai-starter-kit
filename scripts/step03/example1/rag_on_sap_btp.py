from gen_ai_hub.proxy.langchain.openai import ChatOpenAI
from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client
from gen_ai_hub.proxy.langchain.openai import OpenAIEmbeddings
from library.constants.folders import FILE_ENV
from library.constants.table_names import TABLE_NAME
from library.util.logging import initLogger
from langchain_community.vectorstores.hanavector import HanaDB
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from library.data.hana_db import get_connection_to_hana_db
from dotenv import load_dotenv
import logging

log = logging.getLogger(__name__)
initLogger()

def main():
    # Load environment variables
    load_dotenv(dotenv_path=str(FILE_ENV), verbose=True)

    # Get the connection to the HANA DB
    connection_to_hana = get_connection_to_hana_db()
    log.info("Connection to HANA DB established")

    # Get the proxy client for the AI Core service
    proxy_client = get_proxy_client("gen-ai-hub")

    # Create the OpenAIEmbeddings object
    embeddings = OpenAIEmbeddings(
        proxy_model_name="text-embedding-ada-002", proxy_client=proxy_client
    )
    log.info("OpenAIEmbeddings object created")

    llm = ChatOpenAI(proxy_model_name="gpt-35-turbo", proxy_client=proxy_client)
    log.info("ChatOpenAI object created")

    # Create a memory instance to store the conversation history
    memory = ConversationBufferMemory(
        memory_key="chat_history", output_key="answer", return_messages=True
    )
    log.info("Memory object created")

    # Create the HanaDB object
    db = HanaDB(
        embedding=embeddings, connection=connection_to_hana, table_name=TABLE_NAME
    )

    # -------------------------------------------------------------------------------------
    # Fetch the data from the HANA DB and use it to answer the question using the
    # best 2 matching information chunks
    # -------------------------------------------------------------------------------------

    # Create a retriever instance of the vector store
    retriever = db.as_retriever(search_kwargs={"k": 2})
    log.info("Retriever instance of the vector store created")

    # -------------------------------------------------------------------------------------
    # Call the LLM with the RAG information retrieved from the HANA DB
    # -------------------------------------------------------------------------------------

    # Create prompt template
    prompt_template = """
    You are a helpful assistant. You are provided multiple context items that are related to the prompt you have to answer.
    Use the following pieces of context to answer the question at the end. If the answer is not in the context, reply exactly with "I don't know".

    ```
    {context}
    ```

    Question: {question}
    """

    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )
    chain_type_kwargs = {"prompt": PROMPT}

    # Create a conversational retrieval chain
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm,
        retriever,
        return_source_documents=True,
        memory=memory,
        verbose=False,
        combine_docs_chain_kwargs=chain_type_kwargs,
    )

    # -------------------------------------------------------------------------------------
    # Provide the response to the user
    # -------------------------------------------------------------------------------------

    log.header("Welcome to the interactive Q&A session! Type 'exit' to end the session.")  
      
    while True:  
        # Prompt the user for a question  
        question = input("Please ask a question or type 'exit' to leave: ")  
          
        # Check if the user wants to exit  
        if question.lower() == 'exit':  
            print("Goodbye!")  
            break  
  
        log.info(f"Asking a question: {question}", )  
          
        # Invoke the conversational retrieval chain with the user's question  
        result = qa_chain.invoke({"question": question})  
          
        # Output the answer from LLM  
        log.success("Answer from LLM:")  
        print(result["answer"])  
          
        # Output the source document chunks used for the answer  
        source_docs = result["source_documents"]
        print("================")
        log.info(f"Number of used source document chunks: {len(source_docs)}")  
        for doc in source_docs:
            print("-" * 80)
            log.info(doc.page_content)
            log.info(doc.metadata)

if __name__ == "__main__":
    main()
