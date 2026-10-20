from datetime import datetime, timezone
from database.db import users_collection

docs = users_collection.database["documents"]


def record_upload(filename, status, uploaded_by, chunk_count=0, pages=0, size_bytes=0, error=None):
    docs.update_one(
        {"filename": filename},
        {"$set": {
            "filename": filename,
            "status": status,
            "uploaded_by": uploaded_by,
            "chunk_count": chunk_count,
            "pages": pages,
            "size_bytes": size_bytes,
            "error": error,
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
        }},
        upsert=True,
    )


def get_records():
    return {d["filename"]: d for d in docs.find({}, {"_id": 0})}


def delete_record(filename):
    docs.delete_one({"filename": filename})