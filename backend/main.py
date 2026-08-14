from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os

from services.pdf_processor import process_pdf  # our new function

app = FastAPI(title="MedAssist AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)  # create the folder if it doesn't already exist


@app.get("/")
def read_root():
    return {"message": "MedAssist AI backend is running!"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Accepts a PDF file upload, saves it, extracts+chunks its text,
    and returns how many chunks were created (just to verify it worked).
    """
    # Build the path where we'll save this file
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    # Save the uploaded file to disk
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Run our extract -> clean -> chunk pipeline
    chunks = process_pdf(file_path)

    return {
        "filename": file.filename,
        "num_chunks": len(chunks),
        "first_chunk_preview": chunks[0] if chunks else None,
    }