from database.db import users_collection
from services.auth_service import hash_password

email = "saripudijayalakshmi@gmail.com"
new_password = "MedAssist@123"

result = users_collection.update_one(
    {"email": email},
    {"$set": {"password": hash_password(new_password)}}
)
print("Password updated successfully" if result.modified_count == 1 else "User not found")