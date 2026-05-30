"""Posts router: CRUD with pagination, filtering, and ownership."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from ..database import get_db
from ..dependencies import get_current_user
from ..models import User, Post, Tag, Category
from ..schemas.post import PostCreate, PostUpdate, PostResponse, PostListResponse

router = APIRouter(prefix="/api/posts", tags=["posts"])


def _build_slug(title: str) -> str:
    """Simple slug from title: lowercase, replace spaces with hyphens."""
    return title.lower().replace(" ", "-").replace(".", "").replace(",", "")[:200]


def _post_to_response(post: Post) -> PostResponse:
    tag_names = [t.name for t in post.tags]
    return PostResponse(
        id=post.id,
        title=post.title,
        slug=post.slug,
        content=post.content,
        published=post.published,
        created_at=post.created_at,
        updated_at=post.updated_at,
        author=post.author,
        category_id=post.category_id,
        tags=tag_names,
    )


@router.get("", response_model=PostListResponse)
async def list_posts(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    search: str | None = None,
    category: str | None = None,
    tag: str | None = None,
    published: bool | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Post).options(joinedload(Post.author), joinedload(Post.tags))

    if published is not None:
        query = query.where(Post.published == published)
    if search:
        query = query.where(Post.title.contains(search) | Post.content.contains(search))
    if category:
        query = query.join(Post.category).where(Category.slug == category)
    if tag:
        query = query.join(Post.tags).where(Tag.name == tag)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # Paginate
    query = query.order_by(Post.created_at.desc()).offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    posts = result.unique().scalars().all()

    return PostListResponse(
        items=[_post_to_response(p) for p in posts],
        total=total,
        page=page,
        size=size,
    )


@router.get("/{slug}", response_model=PostResponse)
async def get_post(slug: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Post)
        .options(joinedload(Post.author), joinedload(Post.tags))
        .where(Post.slug == slug)
    )
    post = result.unique().scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return _post_to_response(post)


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    data: PostCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = Post(
        title=data.title,
        slug=_build_slug(data.title),
        content=data.content,
        published=data.published,
        category_id=data.category_id,
        author_id=current_user.id,
    )

    if data.tag_ids:
        result = await db.execute(select(Tag).where(Tag.id.in_(data.tag_ids)))
        post.tags = list(result.scalars().all())

    db.add(post)
    await db.commit()
    await db.refresh(post)

    # Reload with relationships
    result = await db.execute(
        select(Post)
        .options(joinedload(Post.author), joinedload(Post.tags))
        .where(Post.id == post.id)
    )
    return _post_to_response(result.unique().scalar_one())


@router.put("/{slug}", response_model=PostResponse)
async def update_post(
    slug: str,
    data: PostUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Post).options(joinedload(Post.tags)).where(Post.slug == slug)
    )
    post = result.unique().scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your post")

    update_data = data.model_dump(exclude_unset=True)
    tag_ids = update_data.pop("tag_ids", None)

    for field, value in update_data.items():
        if field == "title":
            setattr(post, field, value)
            post.slug = _build_slug(value)
        else:
            setattr(post, field, value)

    if tag_ids is not None:
        result = await db.execute(select(Tag).where(Tag.id.in_(tag_ids)))
        post.tags = list(result.scalars().all())

    await db.commit()
    await db.refresh(post)

    result = await db.execute(
        select(Post)
        .options(joinedload(Post.author), joinedload(Post.tags))
        .where(Post.id == post.id)
    )
    return _post_to_response(result.unique().scalar_one())


@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    slug: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Post).where(Post.slug == slug))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your post")
    await db.delete(post)
    await db.commit()
