import os
import argparse
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import ChatPromptTemplate

# Load environment variables (from .env)
load_dotenv()

CHROMA_PATH = "chroma"

PROMPT_TEMPLATE = """
Answer the question using only the following context:

{context}

---

Question: {question}

Instructions:
Respond based solely on the context above.
If the context does not provide enough information to answer, respond with: {{NONE}}
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="Query to ask the chatbot.")
    args = parser.parse_args()
    query_text = args.query_text

    # Load API key securely from environment variables
    api_key = os.getenv("OPENAI_API_KEY")

    # Load vector database and embedding model
    embedding_function = OpenAIEmbeddings()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Load the chat model
    model = ChatOpenAI(api_key=api_key, model_name="gpt-3.5-turbo-0125")

    # Perform similarity search
    results = db.similarity_search_with_relevance_scores(query_text, k=3)

    if len(results) == 0 or results[0][1] < 0.7:
        print("No relevant results found.")
    else:
        context_text = "\n\n---\n\n".join([doc.page_content for doc, _ in results])
        prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        prompt = prompt_template.format(context=context_text, question=query_text)

        response_text = model.invoke(prompt)
        sources = [doc.metadata.get("source") for doc, _ in results]

        print(f"Response: {response_text}\nSources: {sources}")

if __name__ == "__main__":
    main()
