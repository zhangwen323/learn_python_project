"""HTML page routes — uses DB/models directly."""

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from starlette.templating import _TemplateResponse as TemplateResponse

from ..database import get_db
from ..models import User, Post, Comment
from ..services.auth import hash_password, verify_password, create_access_token, decode_access_token
from ..templating import env

router = APIRouter(tags=["pages"])


def _render(name: str, request: Request, **kw) -> TemplateResponse:
    tpl = env.get_template(name)
    return TemplateResponse(tpl, {"request": request, **kw})


async def _resolve_user(request: Request, db: AsyncSession) -> tuple[object, str] | None:
    token = request.cookies.get("token")
    if not token:
        return None
    payload = decode_access_token(token)
    if not payload:
        return None
    result = await db.execute(select(User).where(User.id == int(payload["sub"])))
    user = result.scalar_one_or_none()
    return (user, user.username) if user else None


def _post_to_dict(post: Post) -> dict:
    return {
        "id": post.id, "title": post.title, "slug": post.slug,
        "content": post.content, "published": post.published,
        "created_at": str(post.created_at) if post.created_at else "",
        "updated_at": str(post.updated_at) if post.updated_at else "",
        "author": {"id": post.author.id, "username": post.author.username} if post.author else None,
        "tags": [t.name for t in post.tags] if post.tags else [],
    }


# ── Auth pages ──

@router.get("/accounts/login/", response_class=HTMLResponse)
async def login_page(request: Request):
    return _render("login.html", request)


@router.post("/accounts/login/", response_class=HTMLResponse)
async def login_submit(request: Request, email: str = Form(...), password: str = Form(...),
                       db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.password_hash):
        return _render("login.html", request, error="Invalid email or password.")

    token = create_access_token({"sub": str(user.id)})
    resp = RedirectResponse("/", status_code=303)
    resp.set_cookie("token", token, httponly=True, max_age=1800)
    return resp


@router.get("/accounts/register/", response_class=HTMLResponse)
async def register_page(request: Request):
    return _render("register.html", request)


@router.post("/accounts/register/", response_class=HTMLResponse)
async def register_submit(request: Request, username: str = Form(...), email: str = Form(...),
                          password: str = Form(...), db: AsyncSession = Depends(get_db)):
    existing = await db.execute(
        select(User).where((User.username == username) | (User.email == email))
    )
    if existing.scalar_one_or_none():
        return _render("register.html", request, error="Username or email already taken.")

    user = User(username=username, email=email, password_hash=hash_password(password))
    db.add(user)
    await db.commit()
    token = create_access_token({"sub": str(user.id)})
    resp = RedirectResponse("/", status_code=303)
    resp.set_cookie("token", token, httponly=True, max_age=1800)
    return resp


@router.get("/accounts/logout/")
async def logout():
    resp = RedirectResponse("/", status_code=303)
    resp.delete_cookie("token")
    return resp


# ── Post pages ──

@router.get("/", response_class=HTMLResponse)
async def post_list(request: Request, page: int = 1, db: AsyncSession = Depends(get_db)):
    u = await _resolve_user(request, db)
    size = 10
    total = (await db.execute(select(func.count()).select_from(Post).where(Post.published == True))).scalar() or 0

    q = (select(Post).options(joinedload(Post.author), joinedload(Post.tags))
         .where(Post.published == True).order_by(Post.created_at.desc())
         .offset((page - 1) * size).limit(size))
    posts = (await db.execute(q)).unique().scalars().all()

    return _render("post_list.html", request,
        username=u[1] if u else None,
        posts=[_post_to_dict(p) for p in posts],
        total=total, page=page,
        total_pages=max(1, (total + size - 1) // size),
    )


@router.get("/post/new/", response_class=HTMLResponse)
async def post_create_page(request: Request, db: AsyncSession = Depends(get_db)):
    u = await _resolve_user(request, db)
    if not u:
        return RedirectResponse("/accounts/login/", status_code=303)
    return _render("post_form.html", request, username=u[1], post=None)


@router.post("/post/new/", response_class=HTMLResponse)
async def post_create_submit(request: Request, title: str = Form(...), content: str = Form(""),
                             published: str = Form("false"), db: AsyncSession = Depends(get_db)):
    u = await _resolve_user(request, db)
    if not u:
        return RedirectResponse("/accounts/login/", status_code=303)
    slug = title.lower().replace(" ", "-").replace(".", "").replace(",", "")[:200]
    db.add(Post(title=title, slug=slug, content=content,
                published=(published == "true"), author_id=u[0].id))
    await db.commit()
    return RedirectResponse(f"/post/{slug}/", status_code=303)


@router.get("/post/{slug}/edit/", response_class=HTMLResponse)
async def post_edit_page(request: Request, slug: str, db: AsyncSession = Depends(get_db)):
    u = await _resolve_user(request, db)
    if not u:
        return RedirectResponse("/accounts/login/", status_code=303)
    result = await db.execute(
        select(Post).options(joinedload(Post.author), joinedload(Post.tags)).where(Post.slug == slug)
    )
    post = result.unique().scalar_one_or_none()
    if not post or post.author_id != u[0].id:
        return RedirectResponse("/", status_code=303)
    return _render("post_form.html", request, username=u[1], post=_post_to_dict(post))


@router.post("/post/{slug}/edit/", response_class=HTMLResponse)
async def post_edit_submit(request: Request, slug: str, title: str = Form(...), content: str = Form(""),
                           published: str = Form("false"), db: AsyncSession = Depends(get_db)):
    u = await _resolve_user(request, db)
    if not u:
        return RedirectResponse("/accounts/login/", status_code=303)
    result = await db.execute(select(Post).where(Post.slug == slug))
    post = result.scalar_one_or_none()
    if not post or post.author_id != u[0].id:
        return _render("post_form.html", request, post={"title": title, "content": content},
                       error="Not authorized.")
    post.title = title
    post.slug = title.lower().replace(" ", "-").replace(".", "").replace(",", "")[:200]
    post.content = content
    post.published = (published == "true")
    await db.commit()
    return RedirectResponse(f"/post/{post.slug}/", status_code=303)


@router.post("/post/{slug}/delete/")
async def post_delete(request: Request, slug: str, db: AsyncSession = Depends(get_db)):
    u = await _resolve_user(request, db)
    if not u:
        return RedirectResponse("/accounts/login/", status_code=303)
    result = await db.execute(select(Post).where(Post.slug == slug))
    post = result.scalar_one_or_none()
    if post and post.author_id == u[0].id:
        await db.delete(post)
        await db.commit()
    return RedirectResponse("/", status_code=303)


@router.post("/post/{slug}/comment/")
async def comment_create(request: Request, slug: str, content: str = Form(...),
                         db: AsyncSession = Depends(get_db)):
    u = await _resolve_user(request, db)
    if not u:
        return RedirectResponse("/accounts/login/", status_code=303)
    result = await db.execute(select(Post).where(Post.slug == slug))
    post = result.scalar_one_or_none()
    if post:
        db.add(Comment(content=content, post_id=post.id, author_id=u[0].id))
        await db.commit()
    return RedirectResponse(f"/post/{slug}/", status_code=303)


# ── Post detail (catch-all: must be last among /post/ routes) ──

@router.get("/post/{slug}/", response_class=HTMLResponse)
async def post_detail(request: Request, slug: str, db: AsyncSession = Depends(get_db)):
    u = await _resolve_user(request, db)
    result = await db.execute(
        select(Post).options(joinedload(Post.author), joinedload(Post.tags)).where(Post.slug == slug)
    )
    post = result.unique().scalar_one_or_none()
    if not post:
        return _render("post_detail.html", request, post=None)

    cr = await db.execute(
        select(Comment).options(joinedload(Comment.author))
        .where(Comment.post_id == post.id).order_by(Comment.created_at.asc())
    )
    comments = [{"content": c.content, "created_at": str(c.created_at)[:10],
                  "author": {"username": c.author.username if c.author else "Unknown"}}
                for c in cr.unique().scalars().all()]

    return _render("post_detail.html", request,
        username=u[1] if u else None,
        is_author=(u and post.author and u[0].id == post.author.id),
        post=_post_to_dict(post), comments=comments,
    )
