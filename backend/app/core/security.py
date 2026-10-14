from datetime import datetime, timedelta, timezone

import jwt 
from pwdlib import PasswordHash

from app.core.config import settings


password_hasher = PasswordHash.recommended()

ALGORITHM = 'HS256'


def hash_password(password: str)-> str:
    return password_hasher.hash(password)


def verify_password(plain_pwd: str, hash: str)->bool:
    return password_hasher.verify(plain_pwd, hash)


def create_access_token(user_id: int) -> str:


    now = datetime.now(timezone.utc)

    payload = {
        'sub' : str(user_id),
        'iat' : now,
        'exp' : now+ timedelta(
            minutes= settings.access_token_expire_minutes
        )
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm= ALGORITHM
    )

def decode_access_token(token: str)-> dict:
    return jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms= [ALGORITHM]
    )