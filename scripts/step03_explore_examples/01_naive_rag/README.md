# Example: Naive RAG on SAP BTP
This example shows how to create a simple RAG application that uses provisioned SAP BTP services.

## Installation

1. Create virtual environment

Poetry automatically creates and manages virtual environments. To create one for your project, run:

```sh
poetry install
```

This command creates a virtual environment and installs any dependencies specified in your pyproject.toml file.


2. Run the script

```sh
poetry run python main.py
```

And select one of the available options
0. Cleanup HANA DB
1. Run Data Ingestion
2. Run Retrieval Augmented Generation

## 1. Run Data Ingestion
We begin with data ingestion. This example uses LangChain to load sample documents that will be used for grounding the LLM responses. Document chunks and embedding vectors are then stored in SAP HANA Cloud Vector Engine using the Langchain Vector store adapter.

- We load the `.md` files from the [GitHub repo of the Terraform Provider for SAP BTP](https://github.com/SAP/terraform-provider-btp).
- We clean up any existing docs from the vector store. 
- We embed the documents with the `text-embedding-ada-002` model and load them into a table within the SAP HANA Cloud database of your SAP HANA Cloud service instance. 

This table will contain 3 columns:
- A column VEC_TEXT, which contains the text of the Document.
- A column VEC_META, which contains the metadata of the Document.
- A column VEC_VECTOR, which contains the embeddings-vector of the Document’s text.

## 2. Run Retrieval Augmented Generation
Then we demonstrate *Retrieval Augmented Generation* with SAP HANA Cloud vector engine and SAP GenAI Hub.
We use LangChain `ConversationalRetrievalChain` to retrieve relevant documents and answer the question with the `gpt-35-turbo` model.
