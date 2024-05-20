import asyncio
import uuid

import aiohttp
import pytest_asyncio
from redis.asyncio import Redis
from tests.functional.settings import test_settings


@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def redis_client():
    redis_client = Redis(host=test_settings.redis_host, port=test_settings.redis_port)
    yield redis_client
    await redis_client.close()


@pytest_asyncio.fixture(scope="session")
async def session():
    client_session = aiohttp.ClientSession()
    yield client_session
    await client_session.close()


@pytest_asyncio.fixture()
async def test_user(session):
    url = f"{test_settings.service_url}/api/v1/auth/signup"
    create_user_data = {
        "email": f"test_user{str(uuid.uuid4())[:40]}@test.com",
        "password": "StrongPass123",
        "first_name": "John",
        "last_name": "Doe",
    }
    async with session.post(url, json=create_user_data) as response:
        body = await response.json()

    return body
