# auth_service.py
# Handles password hashing and JWT token creation/verification.

import os
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import jwt, JWTError
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
ALGORITHM = "HS256"                # standard, secure signing algorithm for JWTs
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # tokens valid for 24 hours

# CryptContext handles hashing/verifying passwords with bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Converts a plain-text password into a secure bcrypt hash."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Checks a plain-text password against a stored bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    """
    Creates a signed JWT token containing 'data' (usually user email/id),
    with an expiration time baked in.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict | None:
    """
    Verifies a JWT token's signature and expiration.
    Returns the decoded data if valid, None if invalid/expired.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None