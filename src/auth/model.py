from sqlmodel import SQLModel, Field, Column
import uuid
from datetime import datetime
from sqlalchemy import func, String

#created db model, with user_accounts table

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

    def __repr__(self) -> str:
        return f"<User {self.username}>"