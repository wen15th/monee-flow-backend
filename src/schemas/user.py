from pydantic import BaseModel, ConfigDict, UUID4, Field, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str  # will be hashed
    is_active: Optional[bool] = Field(default=True)


class UserRead(BaseModel):
    id: UUID4
    first_name: str
    last_name: str
    email: EmailStr
    default_display_currency: str
    is_active: Optional[bool]

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# Token returned after login
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Token payload (internal)
class TokenPayload(BaseModel):
    sub: Optional[str]  # User ID


class AuthUser(BaseModel):
    user_id: str
    expire: Optional[int] = None
