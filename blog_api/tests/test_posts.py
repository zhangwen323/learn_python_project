"""Tests for post CRUD endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_post(auth_client: AsyncClient):
    r = await auth_client.post("/api/posts", json={
        "title": "My First Post", "content": "Hello, world!", "published": True,
    })
    assert r.status_code == 201
    data = r.json()
    assert data["title"] == "My First Post"
    assert data["slug"] == "my-first-post"
    assert data["author"]["username"] == "testuser"


@pytest.mark.asyncio
async def test_create_post_unauthenticated(async_client: AsyncClient):
    r = await async_client.post("/api/posts", json={
        "title": "No Auth", "content": "Should fail",
    })
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_list_posts(auth_client: AsyncClient):
    # Create 3 posts
    for i in range(3):
        await auth_client.post("/api/posts", json={
            "title": f"Post {i}", "content": f"Content {i}", "published": True,
        })

    r = await auth_client.get("/api/posts")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3


@pytest.mark.asyncio
async def test_list_posts_pagination(auth_client: AsyncClient):
    for i in range(5):
        await auth_client.post("/api/posts", json={
            "title": f"Post {i}", "content": f"Content {i}", "published": True,
        })

    r = await auth_client.get("/api/posts?page=1&size=2")
    data = r.json()
    assert len(data["items"]) == 2
    assert data["total"] == 5
    assert data["page"] == 1


@pytest.mark.asyncio
async def test_get_post_by_slug(auth_client: AsyncClient):
    r = await auth_client.post("/api/posts", json={
        "title": "Slug Test", "content": "Test", "published": True,
    })
    slug = r.json()["slug"]

    r = await auth_client.get(f"/api/posts/{slug}")
    assert r.status_code == 200
    assert r.json()["title"] == "Slug Test"


@pytest.mark.asyncio
async def test_get_post_not_found(async_client: AsyncClient):
    r = await async_client.get("/api/posts/no-such-slug")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_update_post_own(auth_client: AsyncClient):
    r = await auth_client.post("/api/posts", json={
        "title": "Original Title", "content": "Original", "published": True,
    })
    slug = r.json()["slug"]

    r = await auth_client.put(f"/api/posts/{slug}", json={"title": "Updated Title"})
    assert r.status_code == 200
    assert r.json()["title"] == "Updated Title"


@pytest.mark.asyncio
async def test_update_post_not_owner(async_client: AsyncClient):
    # Create post as user A
    await async_client.post("/api/auth/register", json={
        "username": "alice", "email": "alice@test.com", "password": "secret123",
    })
    r = await async_client.post("/api/auth/login", json={
        "email": "alice@test.com", "password": "secret123",
    })
    token_a = r.json()["access_token"]
    async_client.headers = {"Authorization": f"Bearer {token_a}"}
    r = await async_client.post("/api/posts", json={
        "title": "Alice's Post", "content": "Mine", "published": True,
    })
    slug = r.json()["slug"]

    # Register user B and try to update Alice's post
    await async_client.post("/api/auth/register", json={
        "username": "bob", "email": "bob@test.com", "password": "secret123",
    })
    r = await async_client.post("/api/auth/login", json={
        "email": "bob@test.com", "password": "secret123",
    })
    token_b = r.json()["access_token"]
    async_client.headers = {"Authorization": f"Bearer {token_b}"}

    r = await async_client.put(f"/api/posts/{slug}", json={"title": "Hacked"})
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_delete_post(auth_client: AsyncClient):
    r = await auth_client.post("/api/posts", json={
        "title": "To Delete", "content": "Delete me", "published": True,
    })
    slug = r.json()["slug"]

    r = await auth_client.delete(f"/api/posts/{slug}")
    assert r.status_code == 204

    r = await auth_client.get(f"/api/posts/{slug}")
    assert r.status_code == 404
