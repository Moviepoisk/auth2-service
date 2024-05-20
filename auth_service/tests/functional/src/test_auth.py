import uuid
from http import HTTPStatus

import pytest
from tests.functional.settings import test_settings


@pytest.mark.asyncio
async def test_login(session):
    create_user_data = {
        "email": f"test_user{str(uuid.uuid4())[:40]}@test.com",
        "password": "StrongPass123",
        "first_name": "John",
        "last_name": "Doe",
    }
    async with session.post(f"{test_settings.service_url}/api/v1/users/signup", json=create_user_data) as response:
        assert response.status == HTTPStatus.CREATED

    async with session.post(
        f"{test_settings.service_url}/api/v1/auth/login",
        json={
            "email": create_user_data["email"],
            "password": create_user_data["password"],
        },
    ) as response:
        assert response.status == HTTPStatus.OK
        assert "access_token_cookie" in response.cookies
        assert "refresh_token_cookie" in response.cookies


@pytest.mark.asyncio
async def test_logout(session):
    create_user_data = {
        "login": f"test_user{str(uuid.uuid4())}",
        "password": "StrongPass123",
        "first_name": "John",
        "last_name": "Doe",
    }
    async with session.post(f"{test_settings.service_url}/api/v1/users/signup", json=create_user_data) as response:
        assert response.status == HTTPStatus.CREATED

    async with session.post(f"{test_settings.service_url}/api/v1/auth/logout") as response:
        assert response.status == HTTPStatus.OK
        assert "access_token_cookie" not in response.cookies
        assert "refresh_token_cookie" not in response.cookies


@pytest.mark.parametrize(
    "login_data",
    [
        {},
        {"email": ""},
        {"password": "StrongPass123"},
    ],
)
@pytest.mark.asyncio
async def test_login_invalid_data(login_data, session):
    async with session.post(
        f"{test_settings.service_url}/api/v1/auth/login",
        json=login_data,
    ) as response:
        assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_login_invalid_creds(session):
    user_email = f"test_user{str(uuid.uuid4())[:40]}@test.com"
    user_pass = "StrongPass123"
    create_user_data = {
        "email": user_email,
        "password": user_pass,
        "first_name": "John",
        "last_name": "Doe",
    }
    async with session.post(f"{test_settings.service_url}/api/v1/users/signup", json=create_user_data) as response:
        assert response.status == HTTPStatus.CREATED

    async with session.post(
        f"{test_settings.service_url}/api/v1/auth/login",
        json={"email": user_email, "password": "wrong_pass"},
    ) as response:
        assert response.status == HTTPStatus.UNAUTHORIZED

    async with session.post(
        f"{test_settings.service_url}/api/v1/auth/login",
        json={"email": f"{user_email}_wrong", "password": user_pass},
    ) as response:
        assert response.status == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio
async def test_revoke_access_token(session):
    create_user_data = {
        "email": f"test_user{str(uuid.uuid4())[:40]}@test.com",
        "password": "StrongPass123",
        "first_name": "John",
        "last_name": "Doe",
    }
    async with session.post(f"{test_settings.service_url}/api/v1/users/signup", json=create_user_data) as response:
        assert response.status == HTTPStatus.CREATED

    async with session.post(
        f"{test_settings.service_url}/api/v1/auth/login",
        json={
            "email": create_user_data["email"],
            "password": create_user_data["password"],
        },
    ) as response:
        assert response.status == HTTPStatus.OK
        assert "access_token_cookie" in response.cookies
        assert "refresh_token_cookie" in response.cookies

    access_token_cookie = response.cookies["access_token_cookie"]

    async with session.delete(
        f"{test_settings.service_url}/api/v1/auth/access-revoke",
        cookies={"access_token_cookie": access_token_cookie},
    ) as response:
        assert response.status == HTTPStatus.NO_CONTENT

    async with session.get(
        f"{test_settings.service_url}/api/v1/users/history",
        cookies={"access_token_cookie": access_token_cookie},
    ) as response:
        assert response.status == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio
async def test_revoke_refresh_token(session):
    create_user_data = {
        "email": f"test_user{str(uuid.uuid4())[:40]}@test.com",
        "password": "StrongPass123",
        "first_name": "John",
        "last_name": "Doe",
    }
    async with session.post(f"{test_settings.service_url}/api/v1/users/signup", json=create_user_data) as response:
        assert response.status == HTTPStatus.CREATED

    async with session.post(
        f"{test_settings.service_url}/api/v1/auth/login",
        json={
            "email": create_user_data["email"],
            "password": create_user_data["password"],
        },
    ) as response:
        assert response.status == HTTPStatus.OK
        assert "access_token_cookie" in response.cookies
        assert "refresh_token_cookie" in response.cookies

    refresh_token_cookie = response.cookies["refresh_token_cookie"]

    async with session.delete(
        f"{test_settings.service_url}/api/v1/auth/refresh-revoke",
        cookies={"refresh_token_cookie": refresh_token_cookie},
    ) as response:
        assert response.status == HTTPStatus.NO_CONTENT

    async with session.post(
        f"{test_settings.service_url}/api/v1/auth/refresh",
        cookies={"refresh_token_cookie": refresh_token_cookie},
    ) as response:
        assert response.status == HTTPStatus.UNAUTHORIZED
