from fastapi import FastAPI, UploadFile, File, Depends  # ADD Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
import os

from services.pdf_processor import process_pdf
from services.vector_store import embed_and_store_chunks, get_collection_count, retrieve_relevant_chunks
from services.llm_service import generate_answer
from services.auth_service import hash_password, verify_password, create_access_token, get_current_user  # ADD get_current_user
from services.chat_service import save_message, get_user_history  # NEW
from database.db import users_collection

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


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


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


@app.post("/register")
async def register(request: RegisterRequest):
    existing_user = users_collection.find_one({"email": request.email})
    if existing_user:
        return {"error": "A user with this email already exists."}
    hashed_pw = hash_password(request.password)
    users_collection.insert_one({
        "name": request.name,
        "email": request.email,
        "password": hashed_pw,
    })
    return {"message": "User registered successfully."}


@app.post("/login")
async def login(request: LoginRequest):
    user = users_collection.find_one({"email": request.email})
    if not user or not verify_password(request.password, user["password"]):
        return {"error": "Invalid email or password."}
    token = create_access_token({"sub": user["email"], "name": user["name"]})
    return {
        "access_token": token,
        "token_type": "bearer",
        "name": user["name"],
    }


# MODIFIED: now requires a valid token via Depends(get_current_user)
@app.post("/ask")
async def ask_question(request: QuestionRequest, current_user: dict = Depends(get_current_user)):
    """
    Protected route: only logged-in users can ask questions.
    Saves the exchange to chat history automatically.
    """
    retrieved_chunks = retrieve_relevant_chunks(request.question, top_k=5)
    result = generate_answer(request.question, retrieved_chunks)

    # NEW: save this exchange to the user's history
    save_message(
        user_email=current_user["email"],
        question=request.question,
        answer=result["answer"],
        sources=result["sources"],
    )

    return {
        "question": request.question,
        "answer": result["answer"],
        "sources": result["sources"],
        "retrieved_chunks": retrieved_chunks,
    }


# NEW: protected route to fetch a user's chat history
@app.get("/history")
async def get_history(current_user: dict = Depends(get_current_user)):
    history = get_user_history(current_user["email"])
    return {"history": history}