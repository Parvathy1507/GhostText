import os
import re
import secrets

from datetime import datetime, timezone

from argon2 import PasswordHasher
from argon2.exceptions import (
    VerifyMismatchError,
    VerificationError,
    InvalidHashError,
)
from itsdangerous import (
    URLSafeTimedSerializer,
    BadSignature,
    SignatureExpired,
)

from fastapi import APIRouter, HTTPException, Request, Response, Depends
from pydantic import BaseModel, Field

from app.database import create_user, get_user_by_username


router = APIRouter(prefix="/auth", tags=["Authentication"])

password_hasher = PasswordHasher()

SESSION_SECRET = os.getenv("GHOSTTEXT_SESSION_SECRET", "")

if not SESSION_SECRET:
    raise RuntimeError(
        "GHOSTTEXT_SESSION_SECRET is not configured. "
        "Set it in your environment before starting GhostText."
    )

serializer = URLSafeTimedSerializer(
    SESSION_SECRET,
    salt="ghosttext-session",
)

SESSION_COOKIE = "ghosttext_session"
SESSION_MAX_AGE = 60 * 60 * 8


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=12, max_length=128)


class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=1, max_length=128)


def normalize_username(username: str) -> str:
    username = username.strip().lower()

    if not re.fullmatch(r"[a-z0-9_]{3,30}", username):
        raise HTTPException(
            status_code=400,
            detail=(
                "Username must contain 3–30 characters: "
                "lowercase letters, numbers, or underscores."
            ),
        )

    return username


def get_current_user(request: Request):
    token = request.cookies.get(SESSION_COOKIE)

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Please log in first.",
        )

    try:
        user_id = serializer.loads(
            token,
            max_age=SESSION_MAX_AGE,
        )

        if not isinstance(user_id, int):
            raise BadSignature("Invalid user identifier.")

    except (BadSignature, SignatureExpired):
        raise HTTPException(
            status_code=401,
            detail="Your session is invalid or expired. Please log in again.",
        )

    from app.database import get_user_by_id

    user = get_user_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User account not found.",
        )

    return user


@router.post("/register", status_code=201)
def register(data: RegisterRequest):
    username = normalize_username(data.username)

    if len(data.password) < 12:
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least 12 characters.",
        )

    try:
        password_hash = password_hasher.hash(data.password)
        user_id = create_user(username, password_hash)

    except Exception as exc:
        # SQLite uses a UNIQUE constraint to prevent duplicate usernames.
        if "UNIQUE constraint failed" in str(exc):
            raise HTTPException(
                status_code=409,
                detail="That username is already registered.",
            )

        raise

    return {
        "message": "Account created successfully. Please log in.",
        "user_id": user_id,
        "username": username,
    }


@router.post("/login")
def login(data: LoginRequest, request: Request, response: Response):
    username = normalize_username(data.username)

    from app.database import get_user_by_username

    user = get_user_by_username(username)

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password.",
        )

    try:
        password_hasher.verify(
            user["password_hash"],
            data.password,
        )
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password.",
        )

    token = serializer.dumps(user["id"])

    response.set_cookie(
        key=SESSION_COOKIE,
        value=token,
        httponly=True,
        secure=os.getenv("GHOSTTEXT_HTTPS", "").lower() == "true",
        samesite="lax",
        max_age=SESSION_MAX_AGE,
        path="/",
    )

    return {
        "message": "Login successful.",
        "username": user["username"],
    }


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(
        key=SESSION_COOKIE,
        httponly=True,
        secure=os.getenv("GHOSTTEXT_HTTPS", "").lower() == "true",
        samesite="lax",
        path="/",
    )

    return {"message": "Logged out successfully."}


@router.get("/me")
def current_user(user=Depends(get_current_user)):
    return {
        "id": user["id"],
        "username": user["username"],
    }
