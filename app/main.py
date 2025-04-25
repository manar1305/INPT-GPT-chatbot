from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.routes import router
from app.rag_pipeline import initialize_rag_pipeline

app = FastAPI(title="INPT-GPT")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(router)

@app.get("/")
async def root():
    return FileResponse("static/index.html")

@app.on_event("startup")
async def on_startup():
    initialize_rag_pipeline()
