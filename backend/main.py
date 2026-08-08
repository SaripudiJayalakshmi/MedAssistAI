# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # NEW: lets us allow the frontend's origin

app = FastAPI(title="MedAssist AI Backend")

# NEW: Tell FastAPI which frontend origins are allowed to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # our Vite dev server's address
    allow_credentials=True,
    allow_methods=["*"],  # allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "MedAssist AI backend is running!"}

@app.get("/health")
def health_check():
    return {"status": "ok"}