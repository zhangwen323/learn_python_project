"""Pydantic schemas for posts."""

from datetime import datetime
from pydantic import BaseModel
from .user import UserResponse


class PostCreate(BaseModel):
    title: str
    content: str = ""
    published: bool = False
    category_id: int | None = None
    tag_ids: list[int] = []


class PostUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    published: bool | None = None
    category_id: int | None = None
    tag_ids: list[int] | None = None


class PostResponse(BaseModel):
    id: int
    title: str
    slug: str
    content: str
    published: bool
    created_at: datetime
    updated_at: datetime
    author: UserResponse
    category_id: int | None = None
    tags: list[str] = []

    model_config = {"from_attributes": True}


class PostListResponse(BaseModel):
    items: list[PostResponse]
    total: int
    page: int
    size: int
