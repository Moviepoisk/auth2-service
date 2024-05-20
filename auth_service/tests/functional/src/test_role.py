import uuid
from http import HTTPStatus

import pytest
from tests.functional.settings import test_settings


@pytest.mark.asyncio
async def test_create(session):
    url = f"{test_settings.service_url}/api/v1/roles/"
    create_role_data = {"name": f"test_role_{str(uuid.uuid4())}"}
    async with session.post(url, json=create_role_data) as response:
        assert response.status == HTTPStatus.CREATED
        body = await response.json()
        assert "name" in body


@pytest.mark.asyncio
async def test_get(session):
    pass
    # TODO add after default roles endpoint is added


@pytest.mark.asyncio
async def test_update(session):
    pass
    # TODO add after default roles endpoint is added


@pytest.mark.asyncio
async def test_delete(session):
    pass
    # TODO add after default roles endpoint is added


@pytest.mark.asyncio
async def test_assign(session):
    pass
    # TODO add after default roles and default user endpoints are added


@pytest.mark.asyncio
async def test_revoke(session):
    pass
    # TODO add after default roles and default user endpoints are added
