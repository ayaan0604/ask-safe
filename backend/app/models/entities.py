from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text, CheckConstraint, ForeignKey

from sqlalchemy.orm import Mapped, mapped_column

from pgvector.sqlalchemy import Vector

from app.core.database import Base


class User(Base):
    __tablename__ = 'users'

    __table_args__ = (
        CheckConstraint(
            "role IN ('employee', 'manager', 'hr_admin')",
            name="valid_user_role",
        ),
        CheckConstraint(
            "account_status IN ('pending', 'active', 'rejected')",
            name="valid_account_status",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    email : Mapped[str] = mapped_column(
        String(255), unique= True, index= True, nullable= False
    )

    password_hash : Mapped[str] = mapped_column(
        String(255), nullable = False
    )

    role : Mapped[str] = mapped_column(
        String(20), nullable= False
    )

    account_status: Mapped[str] = mapped_column(
        String(20),
        default='active',
        nullable= False
    )

class Document(Base):
    __tablename__ = 'documents'

    __table_args = (
        CheckConstraint(
            "access_level IN ('employee', 'manager', 'hr')",
            name="valid_document_access_level",
        ),
        CheckConstraint(
            "status IN ('pending', 'processing', 'ready', 'failed')",
            name = 'valid_document_status',
        )

    )

    id : Mapped[int] = mapped_column(primary_key=True)

    filename: Mapped[str] = mapped_column(
        String(255),
        nullable = False
    )

    access_level: Mapped[str] = mapped_column(
        String(20), nullable= False
    )

    status: Mapped[str] = mapped_column(
        String(20), nullable= False
    )

    uploaded_by : Mapped[int] = mapped_column(
        ForeignKey('users.id'), nullable= False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    chunk_index: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    page_number: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    content: Mapped[str] = mapped_column(
        Text, nullable=False
    )
    embedding = mapped_column(Vector(768), nullable=False)
