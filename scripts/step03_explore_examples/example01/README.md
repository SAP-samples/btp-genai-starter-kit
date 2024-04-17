# Example: RAG on SAP BTP
This example shows how to create a simple RAG application that uses provisioned SAP BTP services.

## 1. Data Ingestion
We begin with data ingestion. This example uses LangChain to load sample documents that will be used for grounding the LLM responses. Document chunks and embedding vectors are then stored in SAP HANA Cloud Vector Engine using the Langchain Vector store adapter.

You can proceed with running the script `ingest_data.py`:
> `python ingest_data.py`

- We load the `.md` files from the [GitHub repo of the Terraform Provider for SAP BTP](https://github.com/SAP/terraform-provider-btp).
- We clean up any existing docs from the vector store. 
- We embed the documents with the `text-embedding-ada-002` model and load them into a table within the SAP HANA Cloud database of your SAP HANA Cloud service instance. 

This table will contain 3 columns:
- A column VEC_TEXT, which contains the text of the Document.
- A column VEC_META, which contains the metadata of the Document.
- A column VEC_VECTOR, which contains the embeddings-vector of the Document’s text.

## 2. Retrieval Augmanted Generation
Then we demonstrate *Retrieval Augmented Generation* with SAP HANA Cloud vector engine and SAP GenAI Hub.
We use LangChain `ConversationalRetrievalChain` to retrieve relevant documents and answer the question with the `gpt-35-turbo` model.

You can proceed with running the script `rag_on_sap_btp.py`:
> `python rag_on_sap_btp.py`