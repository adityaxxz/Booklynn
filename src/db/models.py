from sqlmodel import SQLModel, Field, Column, Relationship, null, table
import uuid, enum
from datetime import datetime
from sqlalchemy import Enum, String, DateTime, ForeignKey, func
from typing import List, Optional

#created db model, with user_accounts, books, reviews table

class User(SQLModel, table=True):
    __tablename__: str = "user_accounts"

    uid: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        unique=True,
        nullable=False,
        index=True,
        description="Unique identifier for the user account"
    )

    username: str
    first_name: str = Field(nullable=True)
    email: str = Field(unique=True, index=True)

    role: str = Field(
        sa_column=Column(String, nullable=False, server_default="user")
    )
    is_verified: bool = Field(default=False)
    password_hash: str
    created_at: datetime = Field(default=func.now())
    updated_at: datetime = Field(default=func.now())

    books: List["Book"] = Relationship(back_populates="user", sa_relationship_kwargs={"lazy":"selectin"})
    reviews: List["Review"] = Relationship(back_populates="user", sa_relationship_kwargs={"lazy": "selectin"})

    def __repr__(self) -> str:
        return f"<User {self.username}>"



class LanguageEnum(enum.Enum):
    English="English"
    Other="Other"

class Book(SQLModel, table=True):
    __tablename__: str = "books"

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


    user_uid: Optional[uuid.UUID] = Field(
        default=None,
        sa_column=Column(String(36), ForeignKey("user_accounts.uid"), nullable=True),
    )

    created_at: datetime = Field(sa_column=Column(DateTime, default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(DateTime, default=datetime.now))

    user: Optional[User] = Relationship(back_populates="books")
    reviews: List["Review"] = Relationship(back_populates="book", sa_relationship_kwargs={"lazy": "selectin"})


    def __repr__(self) -> str:
        return f"<Book {self.title}>"


class Review(SQLModel, table=True):
    __tablename__: str = "reviews"

    uid: uuid.UUID = Field(sa_column=Column(String(36), nullable=False, primary_key=True, default=lambda: str(uuid.uuid4())))
    rating: int = Field(lt=6)

    review_text : str = Field(sa_column=Column(String(100), nullable=False))

    user_uid: Optional[str] = Field(
        default=None,
        sa_column=Column(String(36), ForeignKey("user_accounts.uid"), nullable=True),
    )
    book_uid: Optional[str] = Field(
        default=None,
        sa_column=Column(String(36), ForeignKey("books.uid"), nullable=True),
    )

    created_at: datetime = Field(sa_column=Column(DateTime, default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(DateTime, default=datetime.now))

    user: Optional[User] = Relationship(back_populates="reviews")
    book: Optional[Book] = Relationship(back_populates="reviews")

    def __repr__(self):
        return f"<Review for book {self.book_uid} by user {self.user_uid}>"




