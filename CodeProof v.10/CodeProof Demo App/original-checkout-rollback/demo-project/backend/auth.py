"""Authentication module — handles user registration and login."""

import os
import sqlite3
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from jose import JWTError, jwt

from backend.database import get_db_connection, init_db

# Secret key for JWT — in production, use environment variable
SECRET_KEY = os.getenv("JWT_SECRET", "codeproof-demo-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def create_user(username: str, email: str, password: str) -> dict:
    """Register a new user. Returns user data or raises ValueError."""
    if not username or not email or not password:
        raise ValueError("Username, email, and password are required")

    if len(password) < 6:
        raise ValueError("Password must be at least 6 characters")

    password_hash = hash_password(password)

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, password_hash),
        )
        conn.commit()
        user_id = cursor.lastrowid
    except sqlite3.IntegrityError as e:
        conn.close()
        if "username" in str(e).lower():
            raise ValueError("Username already exists")
        raise ValueError("Email already exists")

    conn.close()

    return {
        "id": user_id,
        "username": username,
        "email": email,
    }


def authenticate_user(username: str, password: str) -> Optional[dict]:
    """Authenticate a user. Returns user data or None if authentication fails."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, username, email, password_hash FROM users WHERE username = ?",
        (username,),
    )
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    # BUG (auth-001): Direct comparison instead of bcrypt verification
    # This will always fail because we're comparing plaintext to hash
    if password == row["password_hash"]:
        return {
            "id": row["id"],
            "username": row["username"],
            "email": row["email"],
        }

    return None


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> Optional[dict]:
    """Verify a JWT token and return the payload."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
