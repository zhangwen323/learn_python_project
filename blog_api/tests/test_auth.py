"""Tests for auth endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register(async_client: AsyncClient):
    r = await async_client.post("/api/auth/register", json={
        "username": "bob",
        "email": "bob@test.com",
        "password": "secret123",
    })
    assert r.status_code == 201
    data = r.json()
    assert data["username"] == "bob"
    assert data["email"] == "bob@test.com"
    assert "password" not in data


@pytest.mark.asyncio
async def test_register_duplicate_username(async_client: AsyncClient):
    await async_client.post("/api/auth/register", json={
        "username": "bob", "email": "bob1@test.com", "password": "secret123",
    })
    r = await async_client.post("/api/auth/register", json={
        "username": "bob", "email": "bob2@test.com", "password": "secret123",
    })
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_register_duplicate_email(async_client: AsyncClient):
    await async_client.post("/api/auth/register", json={
        "username": "alice", "email": "alice@test.com", "password": "secret123",
    })
    r = await async_client.post("/api/auth/register", json={
        "username": "alice2", "email": "alice@test.com", "password": "secret123",
    })
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_login_success(async_client: AsyncClient):
    await async_client.post("/api/auth/register", json={
        "username": "charlie", "email": "charlie@test.com", "password": "secret123",
    })
    r = await async_client.post("/api/auth/login", json={
        "email": "charlie@test.com", "password": "secret123",
    })
    assert r.status_code == 200
    assert "access_token" in r.json()


@pytest.mark.asyncio
async def test_login_wrong_password(async_client: AsyncClient):
    await async_client.post("/api/auth/register", json={
        "username": "dave", "email": "dave@test.com", "password": "secret123",
    })
    r = await async_client.post("/api/auth/login", json={
        "email": "dave@test.com", "password": "wrong",
    })
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(async_client: AsyncClient):
    r = await async_client.post("/api/auth/login", json={
        "email": "noone@test.com", "password": "secret123",
    })
    assert r.status_code == 401
