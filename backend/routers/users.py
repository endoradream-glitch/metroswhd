"""
User authentication routes.

Expose a token endpoint for obtaining JWTs and a simple endpoint to
retrieve the currently authenticated user. User data is maintained in
memory for demonstration. In a production system users would be stored
and retrieved from a database.
"""

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm

from ..dependencies import (
    authenticate_user,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    role_required,
)
from ..models import Token, User
from ..roles import Role


router = APIRouter(tags=["auth"])


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token)


@router.get("/users/me", response_model=User)
async def read_users_me(current_user_data=Depends(role_required(Role.VIEW_ONLY))):
    """Return the current authenticated user as a User model."""
    return User(username=current_user_data.username, role=current_user_data.role)