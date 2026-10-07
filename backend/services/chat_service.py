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
                "bookmarked": doc.get("bookmarked", False),
        })
    return history
from bson import ObjectId

def delete_message(message_id: str, user_email: str) -> bool:
    result = messages_collection.delete_one({"_id": ObjectId(message_id), "user_email": user_email})
    return result.deleted_count == 1

def update_feedback(message_id: str, user_email: str, feedback: str) -> bool:
    result = messages_collection.update_one(
        {"_id": ObjectId(message_id), "user_email": user_email},
        {"$set": {"feedback": feedback}}
    )
    return result.modified_count == 1
def toggle_bookmark(message_id: str, user_email: str) -> bool:
    from bson import ObjectId
    msg = messages_collection.find_one({"_id": ObjectId(message_id), "user_email": user_email})
    if not msg:
        return None
    new_state = not msg.get("bookmarked", False)
    messages_collection.update_one({"_id": ObjectId(message_id)}, {"$set": {"bookmarked": new_state}})
    return new_state

def get_bookmarked(user_email: str) -> list[dict]:
    cursor = messages_collection.find({"user_email": user_email, "bookmarked": True}).sort("created_at", -1)
    return [{"id": str(d["_id"]), "question": d["question"], "answer": d["answer"], "sources": d["sources"], "created_at": d["created_at"].isoformat()} for d in cursor]