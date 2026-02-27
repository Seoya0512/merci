import uuid
import enum

from sqlalchemy import String, Integer, ForeignKey, DateTime, Enum, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class GroupRole(str, enum.Enum):
    OWNER = "OWNER"
    MEMBER = "MEMBER"


class RecallResult(str, enum.Enum):
    REMEMBERED = "기억하심"
    VAGUE = "가물가물"
    FORGOTTEN = "낯설어하심"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    provider: Mapped[str] = mapped_column(String(20), nullable=False)
    provider_user_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    nickname: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    group_memberships: Mapped[list["GroupMember"]] = relationship(back_populates="user")
    comments: Mapped[list["Comment"]] = relationship(back_populates="user")


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    invite_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    created_by: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    members: Mapped[list["GroupMember"]] = relationship(back_populates="group")
    memories: Mapped[list["Memory"]] = relationship(back_populates="group")


class GroupMember(Base):
    __tablename__ = "group_members"

    group_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("groups.id"), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), primary_key=True)
    role: Mapped[GroupRole] = mapped_column(Enum(GroupRole), nullable=False)
    joined_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    group: Mapped["Group"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship(back_populates="group_memberships")


class Memory(Base):
    __tablename__ = "memories"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    group_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("groups.id"), nullable=False)
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    location: Mapped[str] = mapped_column(String(100), nullable=False)
    people: Mapped[str] = mapped_column(String(200), nullable=False)
    story: Mapped[str] = mapped_column(Text, nullable=False)
    voice_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    group: Mapped["Group"] = relationship(back_populates="memories")
    recall_logs: Mapped[list["RecallLog"]] = relationship(back_populates="memory")
    comments: Mapped[list["Comment"]] = relationship(back_populates="memory")


class RecallLog(Base):
    __tablename__ = "recall_logs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    memory_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("memories.id"), nullable=False)
    result: Mapped[RecallResult] = mapped_column(Enum(RecallResult), nullable=False)
    recorded_by: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), nullable=False)
    visited_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False)

    memory: Mapped["Memory"] = relationship(back_populates="recall_logs")


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    memory_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("memories.id"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    memory: Mapped["Memory"] = relationship(back_populates="comments")
    user: Mapped["User"] = relationship(back_populates="comments")
