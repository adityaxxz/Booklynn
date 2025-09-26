from sqlmodel import SQLModel, Field, Column
from sqlalchemy import Enum, String, DateTime
from datetime import datetime
import uuid
import enum

class LanguageEnum(enum.Enum):
    English="English"
    Other="Other"

class Book(SQLModel, table=True):
    __tablename__ = "books"

    uid:uuid.UUID = Field(
        sa_column=Column(
            String(36),  # Use String for UUID in SQLite
            primary_key=True,
            unique=True,
            nullable=False,
            default=lambda: str(uuid.uuid4())
        )
    )

    title: str
    author: str
    year: str
    language: LanguageEnum = Field(sa_column=Column(Enum(LanguageEnum), nullable=False)) #for literal

    created_at: datetime = Field(sa_column=Column(DateTime, default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(DateTime, default=datetime.now))

    def __repr__(self) -> str:
        return f"<Book {self.title}>"