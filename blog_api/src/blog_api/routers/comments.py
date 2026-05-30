"""Comments router: nested under posts."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from ..database import get_db
from ..dependencies import get_current_user
from ..models import User, Post, Comment
from ..schemas.comment import CommentCreate, CommentResponse

router = APIRouter(prefix="/api/posts/{slug}/comments", tags=["comments"])


@router.get("", response_model=list[CommentResponse])
async def list_comments(slug: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Post).where(Post.slug == slug))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    result = await db.execute(
        select(Comment)
        .options(joinedload(Comment.author))
        .where(Comment.post_id == post.id)
        .order_by(Comment.created_at.asc())
    )
    return list(result.unique().scalars().all())


@router.post("", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    slug: str,
    data: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Post).where(Post.slug == slug))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    comment = Comment(
        content=data.content,
        post_id=post.id,
        author_id=current_user.id,
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)

    # Reload with author
    result = await db.execute(
        select(Comment)
        .options(joinedload(Comment.author))
        .where(Comment.id == comment.id)
    )
    return result.unique().scalar_one()
