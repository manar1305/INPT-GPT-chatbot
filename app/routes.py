from fastapi import APIRouter, HTTPException
from app.models import QuestionRequest
from app.rag_pipeline import qa_chain

router = APIRouter()

@router.post("/api/ask")
async def ask_question(request: QuestionRequest):
    if not qa_chain:
        raise HTTPException(status_code=500, detail="RAG pipeline not initialized")

    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Empty question")

    result = qa_chain.invoke({"query": question})
    return {"answer": result["result"]}

@router.get("/health")
async def health_check():
    from app.rag_pipeline import qa_chain
    return {"status": "healthy", "rag_initialized": qa_chain is not None}
