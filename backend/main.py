from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
import os

from services.pdf_processor import process_pdf
from services.vector_store import embed_and_store_chunks, get_collection_count, retrieve_relevant_chunks
from services.llm_service import generate_answer  # NEW

app = FastAPI(title="MedAssist AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class QuestionRequest(BaseModel):
    question: str


@app.get("/")
def read_root():
    return {"message": "MedAssist AI backend is running!"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    chunks = process_pdf(file_path)
    stored_count = embed_and_store_chunks(chunks, file.filename)

    return {
        "filename": file.filename,
        "num_chunks": len(chunks),
        "chunks_stored_in_db": stored_count,
        "total_chunks_in_database": get_collection_count(),
        "first_chunk_preview": chunks[0] if chunks else None,
    }


@app.post("/ask")
async def ask_question(request: QuestionRequest):
    """
    Full RAG pipeline: retrieve relevant chunks, then generate
    a grounded answer using Llama 3 via Groq.
    """
    retrieved_chunks = retrieve_relevant_chunks(request.question, top_k=5)
    result = generate_answer(request.question, retrieved_chunks)

    return {
        "question": request.question,
        "answer": result["answer"],
        "sources": result["sources"],
        "retrieved_chunks": retrieved_chunks,  # kept for debugging; we can hide this later
    }