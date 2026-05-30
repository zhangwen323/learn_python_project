"""Tests for comment endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_comment(auth_client: AsyncClient):
    r = await auth_client.post("/api/posts", json={
        "title": "Post with Comment", "content": "Content", "published": True,
    })
    slug = r.json()["slug"]

    r = await auth_client.post(f"/api/posts/{slug}/comments", json={
        "content": "Nice post!",
    })
    assert r.status_code == 201
    data = r.json()
    assert data["content"] == "Nice post!"
    assert data["author"]["username"] == "testuser"


@pytest.mark.asyncio
async def test_create_comment_unauthenticated(async_client: AsyncClient):
    await async_client.post("/api/auth/register", json={
        "username": "alice", "email": "alice@test.com", "password": "secret123",
    })
    r = await async_client.post("/api/auth/login", json={
        "email": "alice@test.com", "password": "secret123",
    })
    async_client.headers = {"Authorization": f"Bearer {r.json()['access_token']}"}

    r = await async_client.post("/api/posts", json={
        "title": "Post", "content": "Content", "published": True,
    })
    slug = r.json()["slug"]

    # Remove auth
    async_client.headers.clear()
    r = await async_client.post(f"/api/posts/{slug}/comments", json={"content": "No auth"})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_list_comments(auth_client: AsyncClient):
    r = await auth_client.post("/api/posts", json={
        "title": "Heavy Discussion", "content": "Content", "published": True,
    })
    slug = r.json()["slug"]

    for i in range(3):
        await auth_client.post(f"/api/posts/{slug}/comments", json={
            "content": f"Comment {i}",
        })

    r = await auth_client.get(f"/api/posts/{slug}/comments")
    assert r.status_code == 200
    assert len(r.json()) == 3


@pytest.mark.asyncio
async def test_comments_on_nonexistent_post(auth_client: AsyncClient):
    r = await auth_client.post("/api/posts/no-such-post/comments", json={
        "content": "Where am I?",
    })
    assert r.status_code == 404
