from pydantic import BaseModel, Field
import uuid
from datetime import datetime
from typing import List, Literal
from src.schema import Book
# from src.review.schema import ReviewModel


class UserModel(BaseModel):
    uid: uuid.UUID
    username: str
    email: str
    first_name: str
    is_verified: bool
    password_hash: str = Field(exclude=True)
    created_at: datetime
    updated_at: datetime


class UserCreateModel(BaseModel):
    first_name: str =Field(max_length=25)
    username: str = Field(max_length=8)
    email: str = Field(max_length=40)
    password: str = Field(min_length=6)
    role: Literal["user", "admin"] = "user"
    

class UserLoginModel(BaseModel):
    email: str = Field(max_length=40)
    password: str = Field(min_length=5)


class UserBooksModel(UserModel):   #* subclass of UserModel
    books: List[Book]
    # reviews: List[ReviewModel]


class EmailModel(BaseModel):
    addresses : List[str]


class PasswordResetRequestModel(BaseModel):
    email: str


class PasswordResetConfirmModel(BaseModel):
    new_password: str
    confirm_new_password: str
