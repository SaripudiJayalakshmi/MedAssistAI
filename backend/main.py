from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
import os
from fastapi.responses import Response
from services.export_service import generate_chat_pdf
from fastapi.responses import Response
from services.export_service import generate_chat_pdf, generate_chat_docx
from services.pdf_processor import process_pdf_pages
from services.vision_service import ask_about_image
from services.document_service import record_upload, get_records, delete_record


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
    toggle_bookmark,
    get_bookmarked,
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

@app.patch("/history/{message_id}/bookmark")
async def bookmark_chat(message_id: str, current_user: dict = Depends(get_current_user)):
    result = toggle_bookmark(message_id, current_user["email"])
    if result is None:
        raise HTTPException(status_code=404, detail="Message not found.")
    return {"bookmarked": result}

@app.get("/bookmarks")
async def list_bookmarks(current_user: dict = Depends(get_current_user)):
    return {"bookmarks": get_bookmarked(current_user["email"])}  


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
@app.get("/export/{message_id}/docx")
async def export_docx(message_id: str, current_user: dict = Depends(get_current_user)):
    from bson import ObjectId
    msg = messages_collection.find_one({"_id": ObjectId(message_id), "user_email": current_user["email"]})
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found.")
    data = generate_chat_docx(msg["question"], msg["answer"], msg["sources"])
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": "attachment; filename=medassist_answer.docx"},
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

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    file_bytes = await file.read()

    if len(file_bytes) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"File exceeds {MAX_FILE_SIZE_MB}MB limit.")

    await file.seek(0)

    file_path = os.path.join(UPLOAD_DIR, os.path.basename(file.filename))

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        chunks, pages = process_pdf_pages(file_path)
        if not chunks:
            raise ValueError("No extractable text found (the PDF may be scanned images).")
        delete_document(file.filename)
        stored_count = embed_and_store_chunks(chunks, file.filename, pages)
    except Exception as e:
        record_upload(file.filename, "failed", admin["email"], size_bytes=len(file_bytes), error=str(e))
        raise HTTPException(status_code=422, detail=f"Could not process '{file.filename}': {e}")

    record_upload(file.filename, "ready", admin["email"], chunk_count=stored_count, pages=max(pages), size_bytes=len(file_bytes))

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
        "evidence": result["evidence"],
        "grounded": result["grounded"],
        "message_id": message_id,
    }
@app.post("/ask-image")
async def ask_image(
    file: UploadFile = File(...),
    question: str = Form(""),
    current_user: dict = Depends(get_current_user),
):
    if file.content_type not in ("image/jpeg", "image/png", "image/webp"):
        raise HTTPException(
            status_code=400,
            detail="Only JPG, PNG or WEBP images are allowed",
        )

    data = await file.read()

    if len(data) > 4 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="Image must be under 4 MB",
        )

    answer = ask_about_image(data, file.content_type, question)

    final_answer = (
        answer
        + "\n\nSource: Image analysis (educational, not a diagnosis)"
    )

    q_text = f"[Image: {file.filename}] " + (
        question.strip() or "Describe this image"
    )

    message_id = save_message(
        user_email=current_user["email"],
        question=q_text,
        answer=final_answer,
        sources=[],
    )

    return {
        "question": q_text,
        "answer": final_answer,
        "sources": [],
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
async def admin_list_documents(admin: dict = Depends(require_admin)):
    records = get_records()
    out = []
    indexed_names = set()
    for d in list_documents():
        name = d["filename"]
        indexed_names.add(name)
        r = records.get(name, {})
        out.append({"filename": name, "chunk_count": d["chunk_count"], "status": "ready", "pages": r.get("pages"), "uploaded_at": r.get("uploaded_at"), "error": None})
    for name, r in records.items():
        if name not in indexed_names and r.get("status") == "failed":
            out.append({"filename": name, "chunk_count": 0, "status": "failed", "pages": None, "uploaded_at": r.get("uploaded_at"), "error": r.get("error")})
    return {"documents": out}


# ============================================================
# ADMIN - DELETE DOCUMENT
# ============================================================

@app.delete("/admin/documents/{filename}")
async def admin_delete_document(filename: str, admin: dict = Depends(require_admin)):
    deleted_count = delete_document(filename)
    delete_record(filename)
    file_path = os.path.join(UPLOAD_DIR, os.path.basename(filename))
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except OSError:
        pass
    remaining = sum(1 for d in list_documents() if d["filename"] == filename)
    return {"filename": filename, "chunks_deleted": deleted_count, "chunks_remaining": remaining}


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