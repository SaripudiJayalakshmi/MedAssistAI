from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
import os
from fastapi.responses import Response
from services.export_service import generate_chat_pdf
from fastapi.responses import Response
from services.export_service import generate_chat_pdf
from services.pdf_processor import process_pdf


from services.vector_store import (
    embed_and_store_chunks,
    get_collection_count,
    retrieve_relevant_chunks,
    list_documents,
    delete_document,
)

from services.llm_service import generate_answer

from services.auth_service import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    require_admin,
)

from services.chat_service import (
    save_message,
    get_user_history,
    messages_collection,
    delete_message,
    update_feedback,
)

from database.db import users_collection


app = FastAPI(title="MedAssist AI Backend")


# ============================================================
# CORS CONFIGURATION
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:5176",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# UPLOAD DIRECTORY
# ============================================================

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ============================================================
# REQUEST MODELS
# ============================================================

class QuestionRequest(BaseModel):
    question: str


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str
class FeedbackRequest(BaseModel):
    feedback: str  # "like" or "dislike"

@app.delete("/history/{message_id}")
async def delete_chat(message_id: str, current_user: dict = Depends(get_current_user)):
    success = delete_message(message_id, current_user["email"])
    if not success:
        raise HTTPException(status_code=404, detail="Message not found.")
    return {"deleted": True}

@app.patch("/history/{message_id}/feedback")
async def feedback_chat(message_id: str, request: FeedbackRequest, current_user: dict = Depends(get_current_user)):
    success = update_feedback(message_id, current_user["email"], request.feedback)
    if not success:
        raise HTTPException(status_code=404, detail="Message not found.")
    return {"updated": True}


# ============================================================
# BASIC ROUTES
# ============================================================

@app.get("/")
def read_root():
    return {
        "message": "MedAssist AI backend is running!"
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }
@app.get("/export/{message_id}/pdf")
async def export_pdf(message_id: str, current_user: dict = Depends(get_current_user)):
    from bson import ObjectId
    msg = messages_collection.find_one({"_id": ObjectId(message_id), "user_email": current_user["email"]})
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found.")
    pdf_bytes = generate_chat_pdf(msg["question"], msg["answer"], msg["sources"])
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=medassist_answer.pdf"},
    )


# ============================================================
# PDF UPLOAD ROUTE
# ADMIN ONLY
# ============================================================

@app.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    admin: dict = Depends(require_admin)
):
    MAX_FILE_SIZE_MB = 1000

    file_bytes = await file.read()

    if len(file_bytes) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds {MAX_FILE_SIZE_MB}MB limit."
        )

    await file.seek(0)

    file_path = os.path.join(
        UPLOAD_DIR,
        file.filename
    )

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )

    chunks = process_pdf(file_path)

    stored_count = embed_and_store_chunks(
        chunks,
        file.filename
    )

    return {
        "filename": file.filename,
        "num_chunks": len(chunks),
        "chunks_stored_in_db": stored_count,
        "total_chunks_in_database": get_collection_count(),
        "first_chunk_preview": chunks[0] if chunks else None,
    }

# ============================================================
# REGISTER ROUTE
# ============================================================

@app.post("/register")
async def register(request: RegisterRequest):

    existing_user = users_collection.find_one(
        {
            "email": request.email
        }
    )

    if existing_user:
        return {
            "error": "A user with this email already exists."
        }

    hashed_pw = hash_password(
        request.password
    )

    users_collection.insert_one(
        {
            "name": request.name,
            "email": request.email,
            "password": hashed_pw,
            "is_admin": False,
        }
    )

    return {
        "message": "User registered successfully."
    }


# ============================================================
# LOGIN ROUTE
# ============================================================

@app.post("/login")
async def login(request: LoginRequest):

    user = users_collection.find_one(
        {
            "email": request.email
        }
    )

    if not user or not verify_password(
        request.password,
        user["password"]
    ):
        return {
            "error": "Invalid email or password."
        }

    token = create_access_token(
        {
            "sub": user["email"],
            "name": user["name"]
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "name": user["name"],
        "is_admin": user.get("is_admin", False),
    }


# ============================================================
# ASK QUESTION ROUTE
# LOGGED-IN USERS ONLY
# ============================================================

@app.post("/ask")
async def ask_question(
    request: QuestionRequest,
    current_user: dict = Depends(get_current_user)
):

    retrieved_chunks = retrieve_relevant_chunks(
        request.question,
        top_k=5
    )

    result = generate_answer(
        request.question,
        retrieved_chunks
    )

    message_id = save_message(
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
        "message_id": message_id,
    }

# ============================================================
# CHAT HISTORY ROUTE
# LOGGED-IN USERS ONLY
# ============================================================

@app.get("/history")
async def get_history(
    current_user: dict = Depends(get_current_user)
):

    history = get_user_history(
        current_user["email"]
    )

    return {
        "history": history
    }


# ============================================================
# ADMIN - LIST DOCUMENTS
# ============================================================

@app.get("/admin/documents")
async def admin_list_documents(
    admin: dict = Depends(require_admin)
):

    return {
        "documents": list_documents()
    }


# ============================================================
# ADMIN - DELETE DOCUMENT
# ============================================================

@app.delete("/admin/documents/{filename}")
async def admin_delete_document(
    filename: str,
    admin: dict = Depends(require_admin)
):

    deleted_count = delete_document(
        filename
    )

    return {
        "filename": filename,
        "chunks_deleted": deleted_count
    }


# ============================================================
# ADMIN - ANALYTICS
# ============================================================

@app.get("/admin/analytics")
async def admin_analytics(
    admin: dict = Depends(require_admin)
):

    total_users = users_collection.count_documents({})

    total_questions = messages_collection.count_documents({})

    total_documents = len(
        list_documents()
    )

    total_chunks = get_collection_count()

    return {
        "total_users": total_users,
        "total_questions_asked": total_questions,
        "total_documents": total_documents,
        "total_chunks_in_db": total_chunks,
    }