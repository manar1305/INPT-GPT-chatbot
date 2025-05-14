from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.vectorstores import Chroma
import os
from dotenv import load_dotenv

load_dotenv()


CHROMA_PATH = "chroma"
DATA_PATH = "data/raw/sample.md"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def main():
    generate_data_store()

def generate_data_store():
    documents = load_documents()
    chunks = split_text(documents)
    save_to_chroma(chunks)

def load_documents():
    loader = DirectoryLoader(DATA_PATH, glob="*.md")
    return loader.load()

def split_text(documents: list[Document]):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        length_function=len,
        add_start_index=True,
    )
    chunks = splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")
    
    # Display a sample chunk
    if chunks:
        print(chunks[0].page_content)
        print(chunks[0].metadata)

    return chunks

def save_to_chroma(chunks: list[Document]):
    db = Chroma.from_documents(
        chunks,
        OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY),
        persist_directory=CHROMA_PATH
    )
    print(f"Saved {len(chunks)} chunks to {CHROMA_PATH}.")

if __name__ == "__main__":
    main()
