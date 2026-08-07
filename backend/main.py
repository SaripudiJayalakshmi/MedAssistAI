# main.py
# This is the entry point of our FastAPI backend.

from fastapi import FastAPI  # FastAPI is the framework that lets us build the API

# Create the FastAPI "app" object — this represents our entire backend application
app = FastAPI(title="MedAssist AI Backend")

# This is a "route" — it tells FastAPI:
# "When someone visits the URL '/', run this function and send back its return value"
@app.get("/")
def read_root():
    return {"message": "MedAssist AI backend is running!"}

# A second route, just to prove routing works with multiple paths
@app.get("/health")
def health_check():
    return {"status": "ok"}