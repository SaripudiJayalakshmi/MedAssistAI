# chat_service.py
# Handles saving and retrieving chat history tied to specific users.

from datetime import datetime, timezone
from database.db import db

messages_collection = db["messages"]


def save_message(user_email: str, question: str, answer: str, sources: list[str]) -> str:
    """
    Saves one question/answer exchange to MongoDB, linked to the user's email.
    Returns the inserted document's ID as a string.
    """
    result = messages_collection.insert_one({
        "user_email": user_email,
        "question": question,
        "answer": answer,
        "sources": sources,
        "created_at": datetime.now(timezone.utc),
    })
    return str(result.inserted_id)


def get_user_history(user_email: str) -> list[dict]:
    """
    Retrieves all past question/answer pairs for a given user,
    most recent first.
    """
    cursor = messages_collection.find(
        {"user_email": user_email}
    ).sort("created_at", -1)

    history = []
    for doc in cursor:
        history.append({
            "id": str(doc["_id"]),
            "question": doc["question"],
            "answer": doc["answer"],
            "sources": doc["sources"],
            "created_at": doc["created_at"].isoformat(),
        })
    return history