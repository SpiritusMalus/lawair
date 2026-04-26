import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Column, Enum, ForeignKey, Index, Integer,
    Numeric, SmallInteger, String, Table, Text, func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from app.encryption import EncryptedString


class Base(DeclarativeBase):
    pass


# ---------------------------------------------------------------------------
# Перечисления
# ---------------------------------------------------------------------------

class UserRole(str, enum.Enum):
    admin = "admin"
    lawyer = "lawyer"
    client = "client"


class DocumentType(str, enum.Enum):
    diploma = "diploma"
    certificate = "certificate"
    bar_membership = "bar_membership"
    other = "other"


class DealStatus(str, enum.Enum):
    pending = "pending"       # ожидает подтверждения
    active = "active"         # в работе
    completed = "completed"   # завершена
    cancelled = "cancelled"   # отменена
    disputed = "disputed"     # спор


class MessageRole(str, enum.Enum):
    user = "user"
    assistant = "assistant"


# ---------------------------------------------------------------------------
# Вспомогательная таблица many-to-many: юрист ↔ область права
# ---------------------------------------------------------------------------

lawyer_specializations = Table(
    "lawyer_specializations",
    Base.metadata,
    Column("lawyer_id", Integer, ForeignKey("lawyer_profiles.id", ondelete="CASCADE"), primary_key=True),
    Column("legal_area_id", Integer, ForeignKey("legal_areas.id", ondelete="CASCADE"), primary_key=True),
)


# ---------------------------------------------------------------------------
# Справочники
# ---------------------------------------------------------------------------

class City(Base):
    __tablename__ = "cities"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    region: Mapped[str] = mapped_column(String(100), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False, default="Россия")

    lawyer_profiles: Mapped[list["LawyerProfile"]] = relationship(back_populates="city")


class BarAssociation(Base):
    """Адвокатская палата — используется для верификации юристов."""

    __tablename__ = "bar_associations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    region: Mapped[str] = mapped_column(String(100), nullable=False)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)

    lawyer_profiles: Mapped[list["LawyerProfile"]] = relationship(back_populates="bar_association")


class LegalArea(Base):
    """Область права: уголовное, гражданское, трудовое и т.д."""

    __tablename__ = "legal_areas"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)

    lawyers: Mapped[list["LawyerProfile"]] = relationship(
        secondary=lawyer_specializations, back_populates="specializations"
    )


class SubscriptionPlan(Base):
    """Тарифные планы для юристов (basic, premium)."""

    __tablename__ = "subscription_plans"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    price_monthly: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    max_services: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    is_featured_in_search: Mapped[bool] = mapped_column(default=False, nullable=False)

    subscriptions: Mapped[list["LawyerSubscription"]] = relationship(back_populates="plan")


# ---------------------------------------------------------------------------
# Пользователи
# ---------------------------------------------------------------------------

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(EncryptedString, nullable=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False, default=UserRole.client)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    is_email_verified: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), nullable=False
    )

    lawyer_profile: Mapped["LawyerProfile | None"] = relationship(back_populates="user", uselist=False)
    client_profile: Mapped["ClientProfile | None"] = relationship(back_populates="user", uselist=False)
    ai_chats: Mapped[list["AiChat"]] = relationship(back_populates="user")


class LawyerProfile(Base):
    __tablename__ = "lawyer_profiles"
    __table_args__ = (
        Index("ix_lawyer_profiles_city_verified", "city_id", "is_verified"),
        Index("ix_lawyer_profiles_rating", "rating"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    middle_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    inn: Mapped[str | None] = mapped_column(EncryptedString, nullable=True)       # зашифровано
    bar_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    bar_association_id: Mapped[int | None] = mapped_column(ForeignKey("bar_associations.id"), nullable=True)
    experience_years: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False)
    city_id: Mapped[int | None] = mapped_column(ForeignKey("cities.id"), nullable=True)
    is_verified: Mapped[bool] = mapped_column(default=False, nullable=False)
    rating: Mapped[Decimal] = mapped_column(Numeric(3, 2), default=0.0, nullable=False)
    reviews_count: Mapped[int] = mapped_column(default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="lawyer_profile")
    city: Mapped["City | None"] = relationship(back_populates="lawyer_profiles")
    bar_association: Mapped["BarAssociation | None"] = relationship(back_populates="lawyer_profiles")
    specializations: Mapped[list["LegalArea"]] = relationship(
        secondary=lawyer_specializations, back_populates="lawyers"
    )
    documents: Mapped[list["LawyerDocument"]] = relationship(back_populates="lawyer")
    services: Mapped[list["Service"]] = relationship(back_populates="lawyer")
    reviews: Mapped[list["Review"]] = relationship(back_populates="lawyer")
    deals: Mapped[list["Deal"]] = relationship(back_populates="lawyer")
    subscriptions: Mapped[list["LawyerSubscription"]] = relationship(back_populates="lawyer")


class ClientProfile(Base):
    __tablename__ = "client_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)

    user: Mapped["User"] = relationship(back_populates="client_profile")
    reviews: Mapped[list["Review"]] = relationship(back_populates="client")
    deals: Mapped[list["Deal"]] = relationship(back_populates="client")


# ---------------------------------------------------------------------------
# Документы юриста
# ---------------------------------------------------------------------------

class LawyerDocument(Base):
    __tablename__ = "lawyer_documents"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    lawyer_id: Mapped[int] = mapped_column(
        ForeignKey("lawyer_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    type: Mapped[DocumentType] = mapped_column(Enum(DocumentType), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)  # путь в MinIO
    verified_at: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)

    lawyer: Mapped["LawyerProfile"] = relationship(back_populates="documents")


# ---------------------------------------------------------------------------
# Услуги юриста
# ---------------------------------------------------------------------------

class Service(Base):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    lawyer_id: Mapped[int] = mapped_column(
        ForeignKey("lawyer_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    duration_minutes: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)

    lawyer: Mapped["LawyerProfile"] = relationship(back_populates="services")
    deals: Mapped[list["Deal"]] = relationship(back_populates="service")


# ---------------------------------------------------------------------------
# Отзывы
# ---------------------------------------------------------------------------

class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (
        Index("ix_reviews_lawyer_rating", "lawyer_id", "rating"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    lawyer_id: Mapped[int] = mapped_column(
        ForeignKey("lawyer_profiles.id", ondelete="CASCADE"), nullable=False
    )
    client_id: Mapped[int] = mapped_column(
        ForeignKey("client_profiles.id", ondelete="CASCADE"), nullable=False
    )
    rating: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # 1–5
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)

    lawyer: Mapped["LawyerProfile"] = relationship(back_populates="reviews")
    client: Mapped["ClientProfile"] = relationship(back_populates="reviews")


# ---------------------------------------------------------------------------
# Сделки
# ---------------------------------------------------------------------------

class Deal(Base):
    __tablename__ = "deals"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    lawyer_id: Mapped[int] = mapped_column(ForeignKey("lawyer_profiles.id"), nullable=False, index=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("client_profiles.id"), nullable=False, index=True)
    service_id: Mapped[int | None] = mapped_column(ForeignKey("services.id"), nullable=True)
    status: Mapped[DealStatus] = mapped_column(
        Enum(DealStatus), nullable=False, default=DealStatus.pending, index=True
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    platform_fee: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), nullable=False
    )

    lawyer: Mapped["LawyerProfile"] = relationship(back_populates="deals")
    client: Mapped["ClientProfile"] = relationship(back_populates="deals")
    service: Mapped["Service | None"] = relationship(back_populates="deals")


# ---------------------------------------------------------------------------
# Подписки юристов
# ---------------------------------------------------------------------------

class LawyerSubscription(Base):
    __tablename__ = "lawyer_subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    lawyer_id: Mapped[int] = mapped_column(
        ForeignKey("lawyer_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    plan_id: Mapped[int] = mapped_column(ForeignKey("subscription_plans.id"), nullable=False)
    started_at: Mapped[datetime] = mapped_column(nullable=False)
    expires_at: Mapped[datetime] = mapped_column(nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    lawyer: Mapped["LawyerProfile"] = relationship(back_populates="subscriptions")
    plan: Mapped["SubscriptionPlan"] = relationship(back_populates="subscriptions")


# ---------------------------------------------------------------------------
# AI-чат
# ---------------------------------------------------------------------------

class AiChat(Base):
    __tablename__ = "ai_chats"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    # Токен сессии для анонимных пользователей
    session_token: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)

    user: Mapped["User | None"] = relationship(back_populates="ai_chats")
    messages: Mapped[list["AiMessage"]] = relationship(back_populates="chat")


class AiMessage(Base):
    __tablename__ = "ai_messages"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    chat_id: Mapped[int] = mapped_column(
        ForeignKey("ai_chats.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[MessageRole] = mapped_column(Enum(MessageRole), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)

    chat: Mapped["AiChat"] = relationship(back_populates="messages")
