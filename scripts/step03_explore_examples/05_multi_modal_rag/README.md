# Example: Multi Modal RAG

The following examples shows how to create a RAG system that uses complex PDF documnet (multicolumn text, tables, images) for grounding LLM responses.
As an axample document we uses the following file:

## Prerequisites

> Attention!
> Some libraries must be installed on the host environment for this example to work!

To extract information from the PDF multiple packages are required:

- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - for information extraction
- [Poppler utils](https://poppler.freedesktop.org/) - pdf rendering

## 1. Overview

In the first step we use Unstructured to extract information from the PDF. For the tables and images a summary is created. Afterwards embeddings are created for text, images, and tables.

## 2. How to run

Install dependensies:
> `poetry install`

You can proceed with running the script:
> `poetry run python main.py`

**Example questions:**
- What is the product for?
- Summarise curation time
- What are the storage conditions?
- Summarise Chemical/Solvent Resistance
- How to call Henkel Europe?