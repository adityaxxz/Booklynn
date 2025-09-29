from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid


class ReviewCreateModel(BaseModel):
    rating : int = Field(lt=6)
    review_text: str


class ReviewModel(BaseModel):
    uid: uuid.UUID
    rating: int = Field(lt=6)
    review_text: str
    user_uid: Optional[uuid.UUID]
    book_uid: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime

