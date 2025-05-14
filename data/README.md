# Data Collection for RAG Chatbot

This folder contains the data used for our RAG (Retrieval-Augmented Generation) chatbot system. The data was collected from the INPT (Institut National des Postes et Télécommunications) website.

## Data Source

- **Website**: [INPT](https://inpt.ac.ma)
- **Collection Method**: Web scraping using BeautifulSoup4 and Mistral

## Data Organization

This directory contains two main components:

### 1. Raw Data

- `sitemap.xml`: Contains all URLs (pdf and non pdf) from the INPT website used for scraping
- `sample.md`: Sample of processed data to demonstrate the format

### 2. Processed Data

The `processed` folder contains samples of transformed data in markdown format:
- `pdfs_markdown/`: PDF documents converted to markdown using Mistral
- `website_markdown/`: HTML pages converted to markdown using BeautifulSoup4

## Data Collection Process

1. URLs were extracted from `sitemap.xml`
2. PDF URLs were processed using a Mistral LLM to extract text and convert to markdown
3. Regular web pages were processed using BeautifulSoup4 and converted to markdown format

## Data Sample

Here's a brief example of what the processed data looks like (from `sample.md`):

```markdown
# https://inpt.ac.ma/en/about-us

The National Institute of Posts and Telecommunications is a Moroccan engineering school...