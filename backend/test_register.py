# test_register.py
# Standalone script to test registration directly, bypassing FastAPI's error hiding.

from database.db import users_collection
from services.auth_service import hash_password

print("Step 1: Checking existing user...")
existing_user = users_collection.find_one({"email": "sarip@test.com"})
print(f"Existing user found: {existing_user}")

print("\nStep 2: Hashing password...")
hashed_pw = hash_password("test1234")
print(f"Hashed password: {hashed_pw}")

print("\nStep 3: Inserting user...")
result = users_collection.insert_one({
    "name": "Sarip",
    "email": "sarip@test.com",
    "password": hashed_pw,
})
print(f"Insert result: {result.inserted_id}")

print("\n✅ SUCCESS")