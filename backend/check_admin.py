from database.db import users_collection

result = users_collection.update_one(
    {"email": "admin@test.com"},
    {"$set": {"is_admin": True}}
)

print("Matched:", result.matched_count)
print("Modified:", result.modified_count)