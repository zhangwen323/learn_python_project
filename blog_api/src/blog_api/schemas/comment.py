"""Pydantic schemas for comments."""

from datetime import datetime
from pydantic import BaseModel
from .user import UserResponse


class CommentCreate(BaseModel):
    content: str


class CommentResponse(BaseModel):
    id: int
    content: str
    created_at: datetime
    author: UserResponse

    model_config = {"from_attributes": True}
