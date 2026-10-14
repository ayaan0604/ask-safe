from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db

from app.core.security import create_access_token, verify_password

from app.models.entities import User
from app.schemas.auth import CurrentUserResponse, LoginRequest, TokenResponse



router = APIRouter(prefix = '/api/auth', tags = ['Authentication'])


@router.post('/login', response_model= TokenResponse)
def login(
    credentials : LoginRequest,
    db: Annotated[Session, Depends(get_db)]
):
    user = db.scalar(
        select(User).where(User.email == credentials.email)
    )

    if (
        user is None or not verify_password(
            credentials.password,
            user.password_hash,
        )
    ):
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail = "Incorrect email or password",
            headers = {'WWW-Authenticate': "Bearer"}
        )

    return TokenResponse(
        access_token= create_access_token(user.id)
    )

@router.get('/me', response_model= CurrentUserResponse)
def get_me( current_user: Annotated[User, Depends(get_current_user)] ):
    return current_user