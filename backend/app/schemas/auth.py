from pydantic import BaseModel, EmailStr, ConfigDict, Field
from typing import Literal

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'

class CurrentUserResponse(BaseModel):
    id: int 
    email: EmailStr
    role: str

    model_config = ConfigDict(from_attributes= True)

class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    role: Literal['employee', 'manager', 'hr_admin']

class SignupResponse(BaseModel):
    id : int 
    email: EmailStr
    role: str
    account_status : str 
    message: str 

    model_config = ConfigDict(from_attributes=True)