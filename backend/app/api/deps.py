from typing import Annotated

import jwt 
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.entities import User

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
        credentials: Annotated[
            HTTPAuthorizationCredentials | None,
            Depends(bearer_scheme),
        ],
        db: Annotated[Session, Depends(get_db)]
) -> User:

    unauthorized = HTTPException(
        status_code= status.HTTP_401_UNAUTHORIZED,
        detail= "Invalid or expired authentication tokne",
        headers= {'WWW-Authenticate': "Bearer"}
    )

    if credentials is None:
        print("credentials none")
        raise unauthorized

    try:
        payload = decode_access_token(credentials.credentials)
        subject = payload.get('sub')

        if not isinstance(subject, str) or not subject.isdigit():
            print("not string or digit sub")
            raise unauthorized

        user_id = int(subject)

    except (jwt.PyJWTError, ValueError):
        print("value or jwt error")
        raise unauthorized

    user = db.get(User, user_id)

    if user is None or user.account_status != "active":
        print("not active")
        raise unauthorized

    return user

def require_hr_admin(
        current_user: Annotated[User, Depends(get_current_user)]
)-> User:

    if current_user.role!= 'hr_admin':
        raise HTTPException(
            status_code= status.HTTP_403_FORBIDDEN,
            detail = "Hr admin access required"
        )

    return current_user

