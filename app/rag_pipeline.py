from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq

from app.utils import load_and_clean_data, create_text_chunks
from app.config import *

embeddings = None
qa_chain = None

def create_prompt_template():
    return PromptTemplate(
        template="""You are INPT-GPT, an assistant answering questions based on the given academic context.
        
        Context:
        {context}
        
        Question:
        {question}
        
        Instructions:
        - Base your answer solely on the context provided.
        - If unsure, say "I don't have enough information to answer that question."
        - Be concise and accurate.
        - Do not invent any information.
        
        Answer:
        """,
        input_variables=["context", "question"]
    )

def initialize_rag_pipeline():
    global embeddings, qa_chain

    text = load_and_clean_data(DATA_FILE)
    chunks = create_text_chunks(text)

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL, model_kwargs={'device': 'cpu'})
    vectorstore = FAISS.from_texts(chunks, embeddings)

    llm = ChatGroq(api_key=GROQ_API_KEY, model_name=LLM_MODEL_NAME, temperature=0.1, max_tokens=1024)
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 6}),
        chain_type_kwargs={"prompt": create_prompt_template()},
        return_source_documents=False
    )
