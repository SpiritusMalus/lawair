from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if not any(c.isalpha() for c in v):
            raise ValueError("Password must contain at least one letter")
        return v


class RoleOut(BaseModel):
    id: int
    name: str
    model_config = {"from_attributes": True}


class UserOut(BaseModel):
    id: int
    email: str
    created_at: datetime
    roles: list[RoleOut]
    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str
