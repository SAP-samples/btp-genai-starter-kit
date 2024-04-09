# Example: RAG on SAP BTP

## 1. Data Ingestion
We begin with data ingestion. This example uses LangChain to load sample documents (documentation for Terraform Provider for SAP BTP) that will be used for grounding the LLM responce. Document chunks and embedding vectors are then stored in SAP HANA Cloud Vector Engine using the Langchain Vector store adapter.

- We load the sample files from the folder `docs/rag_sources`.
- We clean up any existing documnets from the table. 
- We embed the documents with the `text-embedding-ada-002` model and load them into a table within the SAP HANA Cloud database of your SAP HANA Cloud service instance. This table will contain the vectorized information from the files in the `docs/rag_sources` folder.

You can proceed with running the script `ingest_data.py`:
> `python ingest_data.py`

## 2. Retrieval Augmanted Generation
Then we demonstrate *Retrieval Augmented Generation* with SAP HANA Cloud Vector Engine and SAP GenAI Hub.
We use LangChain `ConversationalRetrievalChain` to retrieve relevant documents and answer the question with the `gpt-35-turbo` model.

You can proceed with running the script `rag_on_sap_btp.py`:
> `python rag_on_sap_btp.py`