import uuid
from http import HTTPStatus

import pytest
from tests.functional.settings import test_settings


@pytest.mark.asyncio
async def test_signup(session):
    url = f"{test_settings.service_url}/api/v1/users/signup"
    create_user_data = {
        "email": f"test_user{str(uuid.uuid4())[:40]}@test.com",
        "password": "StrongPass123",
        "first_name": "John",
        "last_name": "Doe",
    }
    async with session.post(url, json=create_user_data) as response:
        assert response.status == HTTPStatus.CREATED
        body = await response.json()
        assert "id" in body
        assert "first_name" in body
        assert "last_name" in body


@pytest.mark.asyncio
async def test_signup_with_the_same_login(session):
    url = f"{test_settings.service_url}/api/v1/users/signup"
    email = f"test_user{str(uuid.uuid4())[:40]}@test.com"
    create_user_data = {
        "email": email,
        "password": "StrongPass123",
        "first_name": "John",
        "last_name": "Doe",
    }
    async with session.post(url, json=create_user_data) as response:
        assert response.status == HTTPStatus.CREATED

    async with session.post(url, json=create_user_data) as response:
        assert response.status == HTTPStatus.CONFLICT


@pytest.mark.parametrize(
    "create_user_data",
    [
        {},
        {"email": "test_failed"},
        {"email": "", "password": "StrongPass123"},
        {"email": "abc", "password": "StrongPass123"},
        {"password": "StrongPass123"},
        {"email": "test_failed", "password": ""},
        {"email": "test_failed", "password": "1234567"},
    ],
)
@pytest.mark.asyncio
async def test_signup_required_invalid_data(create_user_data, session):
    url = f"{test_settings.service_url}/api/v1/users/signup"

    async with session.post(url, json=create_user_data) as response:
        assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_login_history(session):
    url = f"{test_settings.service_url}/api/v1/users/signup"
    create_user_data = {
        "email": f"test_user{str(uuid.uuid4())[:40]}@test.com",
        "password": "StrongPass123",
        "first_name": "John",
        "last_name": "Doe",
    }
    async with session.post(url, json=create_user_data) as response:
        assert response.status == HTTPStatus.CREATED
        await response.json()

    url = f"{test_settings.service_url}/api/v1/auth/login"
    login_data = {
        "email": create_user_data["email"],
        "password": create_user_data["password"],
    }
    async with session.post(url, json=login_data) as response:
        assert response.status == HTTPStatus.OK
        await response.json()
        access_token = response.cookies["access_token_cookie"]

    async with session.get(
        f"{test_settings.service_url}/api/v1/users/history",
        cookies={"access_token_cookie": access_token},
    ) as response:
        assert response.status == HTTPStatus.OK
        body = await response.json()
        assert body
        assert len(body["items"]) == 1


@pytest.mark.skip("cookies are saved from previous tests")
@pytest.mark.asyncio
async def test_login_history__unauthorized(session):
    url = f"{test_settings.service_url}/api/v1/users/signup"
    create_user_data = {
        "email": f"test_user{str(uuid.uuid4())[:40]}@test.com",
        "password": "StrongPass123",
        "first_name": "John",
        "last_name": "Doe",
    }
    async with session.post(url, json=create_user_data) as response:
        assert response.status == HTTPStatus.CREATED
        await response.json()

    async with session.get(
        f"{test_settings.service_url}/api/v1/users/history",
    ) as response:
        assert response.status == HTTPStatus.FORBIDDEN


@pytest.mark.asyncio
async def test_change_credentials(session):
    url = f"{test_settings.service_url}/api/v1/users/signup"
    create_user_data = {
        "email": f"test_user{str(uuid.uuid4())[:40]}@test.com",
        "password": "StrongPass123",
        "first_name": "John",
        "last_name": "Doe",
    }

    await session.post(url, json=create_user_data)

    url = f"{test_settings.service_url}/api/v1/auth/login"
    login_data = {
        "email": create_user_data["email"],
        "password": create_user_data["password"],
    }
    async with session.post(url, json=login_data) as response:
        login_data = await response.json()
        access_token = response.cookies["access_token_cookie"]

    url = f"{test_settings.service_url}/api/v1/users/{login_data['id']}/creds"
    update_credentials_data = {
        "old_password": create_user_data["password"],
        "new_password": "StrongPass1234",
    }
    async with session.patch(
        url, json=update_credentials_data, cookies={"access_token_cookie": access_token}
    ) as response:
        assert response.status == HTTPStatus.OK
        await response.json()


@pytest.mark.asyncio
async def test_change_credentials__unauthorized(session):
    url = f"{test_settings.service_url}/api/v1/users/signup"
    create_user_data = {
        "email": f"test_user{str(uuid.uuid4())[:40]}@test.com",
        "password": "StrongPass123",
        "first_name": "John",
        "last_name": "Doe",
    }

    async with session.post(url, json=create_user_data) as response:
        user_data = await response.json()

    url = f"{test_settings.service_url}/api/v1/users/{user_data['id']}/creds"
    update_credentials_data = {
        "old_password": create_user_data["password"],
        "new_password": "StrongPass1234",
    }
    async with session.patch(url, json=update_credentials_data) as response:
        assert response.status == HTTPStatus.FORBIDDEN


@pytest.mark.asyncio
async def test_change_credentials__wrong_password(session):
    url = f"{test_settings.service_url}/api/v1/users/signup"
    create_user_data = {
        "email": f"test_user{str(uuid.uuid4())[:40]}@test.com",
        "password": "StrongPass123",
        "first_name": "John",
        "last_name": "Doe",
    }

    await session.post(url, json=create_user_data)

    url = f"{test_settings.service_url}/api/v1/auth/login"
    login_data = {
        "email": create_user_data["email"],
        "password": create_user_data["password"],
    }
    async with session.post(url, json=login_data) as response:
        login_data = await response.json()
        access_token = response.cookies["access_token_cookie"]

    url = f"{test_settings.service_url}/api/v1/users/{login_data['id']}/creds"
    update_credentials_data = {
        "old_password": "WrongPass123",
        "new_password": "StrongPass1234",
    }
    async with session.patch(
        url, json=update_credentials_data, cookies={"access_token_cookie": access_token}
    ) as response:
        assert response.status == HTTPStatus.BAD_REQUEST


@pytest.mark.asyncio
async def test_change_credentials__same_password(session):
    url = f"{test_settings.service_url}/api/v1/users/signup"
    create_user_data = {
        "email": f"test_user{str(uuid.uuid4())[:40]}@test.com",
        "password": "StrongPass123",
        "first_name": "John",
        "last_name": "Doe",
    }

    await session.post(url, json=create_user_data)

    url = f"{test_settings.service_url}/api/v1/auth/login"
    login_data = {
        "email": create_user_data["email"],
        "password": create_user_data["password"],
    }
    async with session.post(url, json=login_data) as response:
        login_data = await response.json()
        access_token = response.cookies["access_token_cookie"]

    url = f"{test_settings.service_url}/api/v1/users/{login_data['id']}/creds"
    update_credentials_data = {
        "old_password": create_user_data["password"],
        "new_password": create_user_data["password"],
    }
    async with session.patch(
        url, json=update_credentials_data, cookies={"access_token_cookie": access_token}
    ) as response:
        assert response.status == HTTPStatus.BAD_REQUEST


@pytest.mark.asyncio
async def test_change_credentials__another_user(session):
    signup_url = f"{test_settings.service_url}/api/v1/users/signup"
    create_user_data = {
        "email": f"test_user{str(uuid.uuid4())[:40]}@test.com",
        "password": "StrongPass123",
        "first_name": "John",
        "last_name": "Doe",
    }

    await session.post(signup_url, json=create_user_data)

    url = f"{test_settings.service_url}/api/v1/auth/login"
    login_data = {
        "email": create_user_data["email"],
        "password": create_user_data["password"],
    }
    async with session.post(url, json=login_data) as response:
        await response.json()
        access_token = response.cookies["access_token_cookie"]

    create_another_user_data = {
        "email": f"test_user{str(uuid.uuid4())[:40]}@test.com",
        "password": "StrongPass123",
        "first_name": "Tom",
        "last_name": "Brown",
    }
    async with session.post(signup_url, json=create_another_user_data) as response:
        another_user_data = await response.json()

    url = f"{test_settings.service_url}/api/v1/users/{another_user_data['id']}/creds"
    update_credentials_data = {
        "old_password": create_user_data["password"],
        "new_password": "StrongPass1234",
    }
    async with session.patch(
        url, json=update_credentials_data, cookies={"access_token_cookie": access_token}
    ) as response:
        assert response.status == HTTPStatus.FORBIDDEN


@pytest.mark.asyncio
async def test_change_credentials__user_not_found(session):
    signup_url = f"{test_settings.service_url}/api/v1/users/signup"
    create_user_data = {
        "email": f"test_user{str(uuid.uuid4())[:40]}@test.com",
        "password": "StrongPass123",
        "first_name": "John",
        "last_name": "Doe",
    }

    await session.post(signup_url, json=create_user_data)

    url = f"{test_settings.service_url}/api/v1/auth/login"
    login_data = {
        "email": create_user_data["email"],
        "password": create_user_data["password"],
    }
    async with session.post(url, json=login_data) as response:
        await response.json()
        access_token = response.cookies["access_token_cookie"]

    url = f"{test_settings.service_url}/api/v1/users/{uuid.uuid4()}/creds"
    update_credentials_data = {
        "old_password": create_user_data["password"],
        "new_password": "StrongPass1234",
    }
    async with session.patch(
        url, json=update_credentials_data, cookies={"access_token_cookie": access_token}
    ) as response:
        assert response.status == HTTPStatus.NOT_FOUND
