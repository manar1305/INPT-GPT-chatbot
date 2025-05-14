import streamlit as st
import os
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import ChatPromptTemplate

# Load OpenAI API key from environment variables
def load_api_key():
    return os.getenv("OPENAI_API_KEY")

# Prompt template
PROMPT_TEMPLATE = """
Answer the question using only the following context:

{context}

---

Question: {question}

Instructions:
Respond based solely on the context above.
If the context does not provide enough information to answer, respond with: {{NONE}}
"""

# Initialize Streamlit app
st.title("INPT-GPT 💬")

api_key = load_api_key()
if not api_key:
    st.error("OpenAI API key not found. Please set it in the .env file.")
    st.stop()

# Initialize vector store and model
CHROMA_PATH = "chroma"
embedding_function = OpenAIEmbeddings()
db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
model = ChatOpenAI(api_key=api_key, model_name="gpt-3.5-turbo-0125")

# Function to generate response
def get_response(query_text):
    results = db.similarity_search_with_relevance_scores(query_text, k=3)
    if not results or results[0][1] < 0.7:
        return "No relevant results found. Try rephrasing your question."
    
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _ in results])
    prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE).format(
        context=context_text,
        question=query_text
    )
    return model.predict(prompt)

# User input and response display
query_text = st.text_input("Ask something about INPT:")
if query_text:
    response = get_response(query_text)
    st.markdown("**Answer:**")
    st.write(response)
