import markdown
import re
from langchain_text_splitters import RecursiveCharacterTextSplitter

def load_and_clean_data(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        raw_md = f.read()
    html = markdown.markdown(raw_md)
    plain_text = re.sub(r'<[^<]+?>', '', html)
    return re.sub(r'\s+', ' ', plain_text).strip()

def create_text_chunks(text: str):
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    return splitter.split_text(text)
