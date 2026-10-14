from pydantic import BaseModel, EmailStr, ConfigDict


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