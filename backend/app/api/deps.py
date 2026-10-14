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
        raise unauthorized

    try:
        payload = decode_access_token(credentials.credentials)
        subject = payload.get('sub')

        if not isinstance(subject, str) or not subject.isdigit():
            raise unauthorized

        user_id = int(subject)

    except:
        raise unauthorized

    user = db.get(User, user_id)

    if user is None:
        raise unauthorized

    return user