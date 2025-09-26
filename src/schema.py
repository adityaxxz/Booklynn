from pydantic import BaseModel, Field, field_validator
from typing import Annotated, Optional
import uuid
from datetime import datetime
from src.models import LanguageEnum

class Book(BaseModel):
    uid: uuid.UUID = Field(..., description="Unique identifier of the book")
    title: str = Field(..., description="Title of the book")
    author: str = Field(..., description="Author of the book")
    year: str = Field(..., description="Published year")
    language: LanguageEnum = Field(..., description="Language of the book")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    # @field_validator('language')
    # @classmethod
    # def validate_language(cls, val: str) -> str:
    #     # allowed = ["english", "other"]
    #     # val_lower = val.lower()
    #     # if val_lower not in allowed:
    #     #     raise ValueError(f"Language must be one of {allowed} (case insensitive)")
    #     # return val.strip().title()
    
class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    year: Optional[str] = None
    language: Optional[LanguageEnum] = None


class BookCreate(BaseModel):
    # This class is used to validate the request when creating a book
    title: str
    author: str
    language: LanguageEnum



