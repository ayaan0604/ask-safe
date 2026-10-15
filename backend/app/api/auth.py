from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.api.deps import get_current_user
from app.core.database import get_db

from app.core.security import create_access_token, verify_password, hash_password

from app.models.entities import User
from app.schemas.auth import CurrentUserResponse, LoginRequest, TokenResponse, SignUpRequest, SignupResponse



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

    if user.account_status != 'active':
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = 'Your account is not active. Please wait for an HR admin to approve it.'
        )

    return TokenResponse(
        access_token= create_access_token(user.id)
    )

@router.get('/me', response_model= CurrentUserResponse)
def get_me( current_user: Annotated[User, Depends(get_current_user)] ):
    return current_user


@router.post("/signup", response_model= SignupResponse, status_code=201)
def signup(
    request: SignUpRequest,
    db: Annotated[Session, Depends(get_db)]
):
    account_status = "active" if request.role == 'employee' else 'pending'

    user = User(
        email = str(request.email).lower(),
        password_hash = hash_password(request.password),
        role = request.role,
        account_status = account_status
    )

    db.add(user)

    try:
        db.commit()
        db.refresh(user)
    
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code = 409,
            detail= "email already exists."
        )
    
    if account_status == "active":
        message = "Account created. You can log in."
    else:
        message = 'Account created. Awaiting HR admin approval.'

    return SignupResponse(
        id = user.id,
        email=user.email,
        role = user.role,
        account_status= user.account_status,
        message = message
    )