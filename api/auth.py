"""
Authentication utilities for WasTask API
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import secrets

from config.api_settings import api_settings
from database_manager import get_db_pool

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = api_settings.secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Security scheme
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return payload
    except JWTError:
        return None


async def get_user_by_username(username: str) -> Optional[dict]:
    """Get user from database by username."""
    pool = await get_db_pool()
    
    query = """
        SELECT id, username, email, hashed_password, is_active, is_admin, created_at
        FROM wastask_users
        WHERE username = $1
    """
    
    async with pool.acquire() as conn:
        row = await conn.fetchrow(query, username)
        return dict(row) if row else None


async def get_user_by_email(email: str) -> Optional[dict]:
    """Get user from database by email."""
    pool = await get_db_pool()
    
    query = """
        SELECT id, username, email, hashed_password, is_active, is_admin, created_at
        FROM wastask_users
        WHERE email = $1
    """
    
    async with pool.acquire() as conn:
        row = await conn.fetchrow(query, email)
        return dict(row) if row else None


async def authenticate_user(username: str, password: str) -> Union[dict, bool]:
    """Authenticate a user with username and password."""
    user = await get_user_by_username(username)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    if not user["is_active"]:
        return False
    return user


async def create_user(username: str, email: str, password: str, is_admin: bool = False) -> dict:
    """Create a new user."""
    pool = await get_db_pool()
    
    # Check if user already exists
    existing_user = await get_user_by_username(username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    existing_email = await get_user_by_email(email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    hashed_password = get_password_hash(password)
    
    # Insert user
    query = """
        INSERT INTO wastask_users (username, email, hashed_password, is_admin)
        VALUES ($1, $2, $3, $4)
        RETURNING id, username, email, is_active, is_admin, created_at
    """
    
    async with pool.acquire() as conn:
        row = await conn.fetchrow(query, username, email, hashed_password, is_admin)
        return dict(row)


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Get current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise credentials_exception
    
    username = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    user = await get_user_by_username(username)
    if user is None:
        raise credentials_exception
    
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user"
        )
    
    return user


async def get_current_admin_user(current_user: dict = Depends(get_current_user)) -> dict:
    """Get current user and verify admin privileges."""
    if not current_user["is_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


def generate_api_key() -> str:
    """Generate a secure API key."""
    return secrets.token_urlsafe(32)