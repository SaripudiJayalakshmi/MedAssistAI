from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel  # NEW: for defining the shape of request bodies
import shutil
import os

from services.pdf_processor import process_pdf
from services.vector_store import embed_and_store_chunks, get_collection_count, retrieve_relevant_chunks  # NEW

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


# NEW: defines what JSON shape we expect in the request body for /ask
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
    Retrieval-only for now: takes a question, returns the most
    relevant chunks from ChromaDB. No LLM answer generation yet —
    that comes in Stage 6.
    """
    retrieved_chunks = retrieve_relevant_chunks(request.question, top_k=5)

    return {
        "question": request.question,
        "retrieved_chunks": retrieved_chunks,
    }