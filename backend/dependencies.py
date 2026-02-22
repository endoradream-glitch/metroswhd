"""
Dependency functions for authentication and role-based access control.

This module defines helpers used across routers to enforce authentication
and authorization. For the purposes of this demonstration the user store
is kept in memory. In a production setting this would be backed by a
database or directory service.
"""

import time
from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from .roles import Role, has_permission


# JWT configuration
SECRET_KEY = "super-secret-key"  # In production, override via env var
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[Role] = None


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


# In-memory user store for demonstration purposes
fake_users_db = {
    # username: {"password": <hashed>, "role": Role}
    "admin": {
        "password": "c0de1ddab3f050be0e522a34d31b568d36594513205c8ea2a6b0f8aabd53268c",  # sha256("adminpw")
        "role": Role.SUPER_ADMIN,
    },
    "hq": {
        "password": "43986d7745daf5c64c540c50d4c560ceba3706d639782b4e87ed868fd77e7f11",  # sha256("hqops")
        "role": Role.HQ_OPS,
    },
    "comd": {
        "password": "9e59b563f828bace12da0490cb1a8094118c9a725bbfdb7b0874ae0e29ecef8e",  # sha256("comdpw")
        "role": Role.PATROL_COMD,
    },
    "member": {
        "password": "3d0d4d573f899dced0dc2463881f5305e7987d589e66ca29d51375bf2bca755b",  # sha256("memberpw")
        "role": Role.PATROL_MEMBER,
    },
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a SHA256-hashed password."""
    import hashlib

    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password


def authenticate_user(username: str, password: str) -> Optional[dict]:
    """Authenticate user credentials and return user data if valid."""
    user = fake_users_db.get(username)
    if not user:
        return None
    if not verify_password(password, user["password"]):
        return None
    return {"username": username, "role": user["role"]}


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token including an expiration."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> TokenData:
    """Decode a JWT and return TokenData or raise HTTPException."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")  # subject is the username
        role_str: str = payload.get("role")
        if username is None or role_str is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Malformed token")
        return TokenData(username=username, role=Role(role_str))
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    """Return the current user from a JWT token."""
    return decode_access_token(token)


def role_required(*required_roles: Role):  # type: ignore
    """Dependency to check that the current user has one of the required roles."""
    async def dependency(current_user: TokenData = Depends(get_current_user)):
        if current_user.role is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No role present")
        # Check permission using hierarchy: user must have equal or higher rank than one of required roles
        allowed = any(has_permission(current_user.role, role) for role in required_roles)
        if not allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient privileges")
        return current_user

    return dependency