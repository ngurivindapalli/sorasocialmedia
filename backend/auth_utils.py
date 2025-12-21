from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db, User

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password
    
    Note: bcrypt has a 72-byte limit. This function should only be called after validation.
    For safety, we truncate here as well, but validation should catch it first.
    """
    # Convert to bytes to check length
    password_bytes = password.encode('utf-8')
    
    # Bcrypt has a 72-byte limit - truncate if necessary (safety measure)
    # This should not be needed if validation is working, but it's a safety net
    if len(password_bytes) > 72:
        print(f"[AUTH] WARNING: Password exceeded 72 bytes ({len(password_bytes)} bytes), truncating")
        password_bytes = password_bytes[:72]
        # Decode back to string, handling any encoding errors
        try:
            password = password_bytes.decode('utf-8', errors='strict')
        except UnicodeDecodeError:
            # If truncation broke a multi-byte character, use error handling
            password = password_bytes.decode('utf-8', errors='ignore')
        print(f"[AUTH] Password truncated to {len(password_bytes)} bytes")
    
    # Passlib expects a string (it will handle encoding internally)
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current authenticated user from JWT token - optional, returns None if no auth"""
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None
    
    user = db.query(User).filter(User.username == username).first()
    return user


