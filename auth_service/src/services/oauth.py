import abc
import logging
from enum import Enum

import httpx
from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy import select, exc, and_
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import selectinload

from src.models.db import User
from src.core.dependencies import get_pg_connection, get_redis
from src.core.config import oauth_settings
from src.core.config.oauth import Settings
from src.models.oauth import UserProviderData
from src.services.user import get_user_service
from src.services.role import get_role_service
from src.models.db.oauth import OAuthUser
from src.models.user import UserInDB, UserCreate
from src.services import BaseService, UserService, RoleService


class OAuthProviderEnum(str, Enum):
    YANDEX = "yandex"
    GOOGLE = "google"


def get_provider_settings(provider_name: str) -> Settings:
    return getattr(oauth_settings, provider_name)


class ABCOAuthService(abc.ABC):
    @abc.abstractmethod
    async def get_user_info(self, *args, **kwargs) -> dict | None:
        """Abstract method to fetch user data from provider."""

    @abc.abstractmethod
    async def create_oauth(self, *args, **kwargs) -> OAuthUser | None:
        """Abstract method to create oauth account for user."""


class BaseOAuthService(ABCOAuthService, BaseService):
    OAUTH_SERVICE_NAME = "base"

    def __init__(self, pg_connection: AsyncEngine, redis: Redis, role_service: RoleService, user_service: UserService):
        super().__init__(pg_connection, redis)
        self.role_service = role_service
        self.user_service = user_service
        self.provider_settings = get_provider_settings(provider_name=self.OAUTH_SERVICE_NAME)

    async def _get_user_provider_data(self, code: str) -> UserProviderData:
        """Method to compose a request data to fetch user data from provider"""
        return UserProviderData(
            code=code, client_id=self.provider_settings.client_id, client_secret=self.provider_settings.client_secret
        )

    async def get_user_info(self, code: str) -> dict | None:
        """Method to fetch user data from a provider."""
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        async with httpx.AsyncClient() as async_client:
            user_provider_data = await self._get_user_provider_data(code=code)
            response = await async_client.post(
                url=self.provider_settings.token_url, headers=headers, data=user_provider_data.model_dump()
            )
            access_token = response.json().get("access_token")
            user_info_response = await async_client.get(
                self.provider_settings.user_info_url, headers={"Authorization": "OAuth " + access_token}
            )
            print(user_info_response.json())
        return user_info_response.json()

    async def _get_oauth_user_by_id(self, oauth_id: str) -> OAuthUser | None:
        """Method to fetch user data from database."""
        async with self.get_session() as session, session.begin():
            try:
                result = await session.execute(
                    select(OAuthUser)
                    .options(selectinload(OAuthUser.user).joinedload(User.roles))
                    .where(and_(OAuthUser.oauth_id == oauth_id, OAuthUser.oauth_name == self.OAUTH_SERVICE_NAME))
                )
                return result.scalars().first()
            except exc.SQLAlchemyError:
                logging.error("Could not fetch a oauth user '{}'".format(oauth_id), exc_info=True)
                raise

    async def _create_oauth_user(self, user_id: str, oauth_id: str) -> OAuthUser | None:
        async with self.get_session() as session, session.begin():
            try:
                oauth_user = OAuthUser(user_id=user_id, oauth_id=oauth_id, oauth_name=self.OAUTH_SERVICE_NAME)
                session.add(oauth_user)
                await session.commit()
                return oauth_user
            except exc.SQLAlchemyError:
                await session.rollback()
                logging.error("Could not create an oauth user '{}'".format(oauth_user.user_id), exc_info=True)
                raise

    async def create_oauth(
        self, oauth_id: str, email: str, first_name: str | None, last_name: str | None
    ) -> UserInDB | None:
        """Method to create an oauth user in db."""
        oauth_user = await self._get_oauth_user_by_id(oauth_id=oauth_id)
        if oauth_user:
            return oauth_user.user

        user = await self.user_service.create(
            user_create=UserCreate(email=email, first_name=first_name, last_name=last_name)
        )
        role = await self.role_service.get_by_name(role_name="user")  # TODO assign default role, not by name
        await self.role_service.assign_role(role=role, user=user)

        await self._create_oauth_user(user_id=str(user.id), oauth_id=oauth_id)

        return user


class OAuthYandexService(BaseOAuthService):
    OAUTH_SERVICE_NAME = "yandex"


def get_oauth_yandex_service(
    pg_connection: AsyncEngine = Depends(get_pg_connection),
    redis: Redis | None = Depends(get_redis),
    role_service: RoleService = Depends(get_role_service),
    user_service: UserService = Depends(get_user_service),
) -> OAuthYandexService:
    return OAuthYandexService(
        pg_connection=pg_connection, redis=redis, role_service=role_service, user_service=user_service
    )
