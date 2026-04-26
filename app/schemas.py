from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, EmailStr, field_validator

from app.models import UserRole


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: UserRole = UserRole.client

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Minimum 8 characters")
        if not any(c.isdigit() for c in v):
            raise ValueError("Must contain at least one digit")
        if not any(c.isalpha() for c in v):
            raise ValueError("Must contain at least one letter")
        return v

    @field_validator("role")
    @classmethod
    def no_admin_self_register(cls, v: UserRole) -> UserRole:
        if v == UserRole.admin:
            raise ValueError("Cannot self-register as admin")
        return v


class UserOut(BaseModel):
    id: int
    email: str
    role: UserRole
    is_active: bool
    is_email_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class VerifyEmailRequest(BaseModel):
    token: str


class ResendVerificationRequest(BaseModel):
    email: EmailStr


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Minimum 8 characters")
        if not any(c.isdigit() for c in v):
            raise ValueError("Must contain at least one digit")
        if not any(c.isalpha() for c in v):
            raise ValueError("Must contain at least one letter")
        return v



# ---------------------------------------------------------------------------
# Services
# ---------------------------------------------------------------------------

class ServiceCreate(BaseModel):
    title: str
    description: str | None = None
    price: Decimal
    duration_minutes: int | None = None

    @field_validator("price")
    @classmethod
    def positive_price(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Price must be > 0")
        return v


class ServiceUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    price: Decimal | None = None
    duration_minutes: int | None = None
    is_active: bool | None = None


class ServiceOut(BaseModel):
    id: int
    title: str
    description: str | None = None
    price: float
    duration_minutes: int | None = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Lawyer catalog (public)
# ---------------------------------------------------------------------------

class LawyerCard(BaseModel):
    profile_id: int
    first_name: str
    last_name: str
    bio: str | None = None
    experience_years: int = 0
    rating: float = 0.0
    reviews_count: int = 0
    is_verified: bool = False
    service_count: int = 0
    min_price: float | None = None


class LawyerPublicProfile(BaseModel):
    profile_id: int
    first_name: str
    last_name: str
    middle_name: str | None = None
    bio: str | None = None
    experience_years: int = 0
    rating: float = 0.0
    reviews_count: int = 0
    is_verified: bool = False
    services: list[ServiceOut] = []


class LawyerSearchResult(BaseModel):
    items: list[LawyerCard]
    total: int
    page: int
    page_size: int


class ProfileOut(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    middle_name: str | None = None
    phone: str | None = None
    bio: str | None = None
    experience_years: int | None = None
    bar_number: str | None = None
    is_verified: bool | None = None
    rating: float | None = None
    reviews_count: int | None = None


class ProfileUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    middle_name: str | None = None
    phone: str | None = None
    bio: str | None = None
    experience_years: int | None = None
    bar_number: str | None = None

    @field_validator("experience_years")
    @classmethod
    def non_negative(cls, v: int | None) -> int | None:
        if v is not None and v < 0:
            raise ValueError("Experience years must be >= 0")
        return v


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Minimum 8 characters")
        if not any(c.isdigit() for c in v):
            raise ValueError("Must contain at least one digit")
        if not any(c.isalpha() for c in v):
            raise ValueError("Must contain at least one letter")
        return v


# ---------------------------------------------------------------------------
# Deals
# ---------------------------------------------------------------------------

class DealCreate(BaseModel):
    lawyer_profile_id: int
    service_id: int | None = None
    description: str | None = None
    amount: Decimal


class DealOut(BaseModel):
    id: int
    lawyer_profile_id: int
    client_profile_id: int
    service_id: int | None
    status: str
    amount: float
    platform_fee: float
    description: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DealDetail(DealOut):
    lawyer_first_name: str
    lawyer_last_name: str
    client_first_name: str | None
    client_last_name: str | None
    service_title: str | None
