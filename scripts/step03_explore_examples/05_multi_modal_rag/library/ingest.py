from logging import getLogger
import os
import base64
import requests
import uuid
from langchain.schema.messages import HumanMessage, AIMessage
from langchain.schema.document import Document
from unstructured.partition.pdf import partition_pdf
from utils.fs import get_script_dir
from library.config import (
    ID_KEY,
)

log = getLogger(__name__)


def load_pdf_from_url(url, path_to_folder):
    # Download the PDF file
    response = requests.get(url)

    # Save the PDF file to the data folder
    pdf_file_path = os.path.join(path_to_folder, "input.pdf")
    with open(pdf_file_path, "wb") as file:
        file.write(response.content)

    return pdf_file_path


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


# Function for text summaries
def summarize_text(llm, text_element):
    prompt = f"Summarize the following text:\n\n{text_element}\n\nSummary:"
    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content


# Function for table summaries
def summarize_table(llm, table_element):
    prompt = f"Summarize the following table:\n\n{table_element}\n\nSummary:"
    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content


# Function for image summaries
def summarize_image(llm_with_vision, encoded_image):
    prompt = [
        AIMessage(content="You are a bot that is good at analyzing images."),
        HumanMessage(
            content=[
                {"type": "text", "text": "Describe the contents of this image."},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"},
                },
            ]
        ),
    ]
    response = llm_with_vision.invoke(prompt)
    return response.content


# Function to add documents to the retriever
def add_documents_to_retriever(retriever, summaries, original_contents):
    doc_ids = [str(uuid.uuid4()) for _ in summaries]
    summary_docs = [
        Document(page_content=s, metadata={ID_KEY: doc_ids[i]})
        for i, s in enumerate(summaries)
    ]
    retriever.vectorstore.add_documents(summary_docs)
    retriever.docstore.mset(list(zip(doc_ids, original_contents)))


def ingest_data_with_unstructured(llm, retriever):
    text_elements = []
    table_elements = []
    image_elements = []

    script_dir = get_script_dir(__file__)
    # Create the data directory if it doesn't exist
    data_dir = os.path.join(script_dir, "gen/data")
    os.makedirs(data_dir, exist_ok=True)
    # Load the PDF file to ingest
    pdf_file_path = load_pdf_from_url(
        "https://datasheets.tdx.henkel.com/LOCTITE-HY-4090GY-en_GL.pdf",
        data_dir

    )
    # Set output directory for Images
    output_path = os.path.join(data_dir, "output_images")

    # Get elements
    raw_pdf_elements = partition_pdf(
        filename=pdf_file_path,
        # Using pdf format to find embedded image blocks
        extract_images_in_pdf=True,
        # Use layout model (YOLOX) to get bounding boxes (for tables) and find titles
        # Titles are any sub-section of the document
        infer_table_structure=True,
        # Post processing to aggregate text once we have the title
        chunking_strategy="by_title",
        max_characters=6000,
        new_after_n_chars=3800,
        combine_text_under_n_chars=2000,
        extract_image_block_output_dir=output_path,
    )

    for element in raw_pdf_elements:
        if "CompositeElement" in str(type(element)):
            text_elements.append(element)
        elif "Table" in str(type(element)):
            table_elements.append(element)

    table_elements = [i.text for i in table_elements]
    text_elements = [i.text for i in text_elements]

    for image_file in os.listdir(output_path):
        if image_file.endswith((".png", ".jpg", ".jpeg")):
            image_path = os.path.join(output_path, image_file)
            encoded_image = encode_image(image_path)
            image_elements.append(encoded_image)

    print(f"Table Elements: {len(table_elements)}")
    print(f"Text Elements: {len(text_elements)}")
    print(f"Images: {len(image_elements)}")

    # Summarise text, table and images
    table_summaries = []
    for i, te in enumerate(table_elements):
        summary = summarize_table(llm, te)
        table_summaries.append(summary)
        print(f"{i + 1}th element of tables processed.")

    text_summaries = []
    for i, te in enumerate(text_elements):
        summary = summarize_text(llm, te)
        text_summaries.append(summary)
        print(f"{i + 1}th element of texts processed.")

    image_summaries = []
    for i, ie in enumerate(image_elements):
        summary = summarize_image(llm, ie)
        image_summaries.append(summary)
        print(f"{i + 1}th element of images processed.")

    print(f"Example Text Summary: {text_summaries[0]}")
    print(f"Example Table Summary: {table_summaries[0]}")
    print(f"Example Image Summary: {image_summaries[0]}")

    # Add text summaries
    add_documents_to_retriever(retriever, text_summaries, text_elements)

    # Add table summaries
    add_documents_to_retriever(retriever, table_summaries, table_elements)

    # Add image summaries
    add_documents_to_retriever(
        retriever, image_summaries, image_summaries
    )  # hopefully real images soon

    log.success("Data ingestion completed.")

