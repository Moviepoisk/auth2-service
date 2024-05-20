import logging
from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from pydantic import BaseModel
from redis.asyncio import Redis
from sqlalchemy import exc
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from src.core.dependencies import get_pg_connection, get_redis
from src.models.db.user import User, UserLoginHistory
from src.models.user import UserCreate, UserInDB, UserLoginHistoryCreate, UserLoginHistoryInDB
from src.services.base import BaseService
from starlette import status


class UserService(BaseService):
    @staticmethod
    async def _check_model_exists_by_id(session: AsyncSession, model: type[BaseModel], model_id: UUID) -> bool:
        query = await session.execute(select(model).where(model.id == model_id))
        return bool(query.unique().fetchone())

    @staticmethod
    async def _check_user_exists(session: AsyncSession, email: str) -> bool:
        query = await session.execute(select(User).where(User.email == email))  # noqa
        return bool(query.unique().fetchone())

    async def _get_user(self, session: AsyncSession, email: str) -> User:
        query = await session.execute(select(User).where(User.email == email))  # noqa
        return query.scalar()

    async def get_by_email(self, user_email: str) -> User | None:
        async with self.get_session() as session:
            async with session.begin():
                try:
                    return (
                        await session.scalars(
                            select(User).where(User.email == user_email).options(selectinload(User.roles))  # noqa
                        )
                    ).first()
                except exc.SQLAlchemyError:
                    logging.error("Something went wrong", exc_info=True)
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Something went wrong",
                    )

    async def get_user_login_history(self, email: str) -> Page[UserLoginHistoryInDB]:
        async with self.get_session() as session:
            async with session.begin():
                return await paginate(session, select(UserLoginHistory).join(User).filter(User.email == email))

    async def get_by_id(self, user_id: UUID) -> User | None:
        async with self.get_session() as session:
            async with session.begin():
                try:
                    return (await session.scalars(select(User).where(User.id == user_id))).first()
                except exc.SQLAlchemyError:
                    logging.error("Something went wrong", exc_info=True)
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Something went wrong",
                    )

    async def create(self, user_create: UserCreate) -> UserInDB | None:
        async with self.get_session() as session:
            async with session.begin():
                try:
                    user_dto = jsonable_encoder(user_create)
                    user = User(**user_dto)
                    session.add(user)
                    await session.commit()
                    return user
                except exc.SQLAlchemyError:
                    await session.rollback()
                    logging.error("Something went wrong", exc_info=True)
                    raise

    async def create_history_record(self, user_login_history: UserLoginHistoryCreate) -> None:
        async with self.get_session() as session:
            async with session.begin():
                try:
                    user_login_history_dto = jsonable_encoder(user_login_history)
                    history = UserLoginHistory(**user_login_history_dto)
                    session.add(history)
                    await session.commit()
                except exc.SQLAlchemyError:
                    await session.rollback()
                    logging.error("Unable to add login history record", exc_info=True)
                    raise

    async def update_credentials(self, user: User, new_password: str) -> UserInDB:
        async with self.get_session() as session:
            async with session.begin():
                try:
                    user.set_password(new_password)
                    session.add(user)
                    await session.commit()
                    return UserInDB.model_validate(user)
                except exc.SQLAlchemyError:
                    await session.rollback()
                    logging.error("Something went wrong", exc_info=True)
                    raise


def get_user_service(
    pg_connection: AsyncEngine = Depends(get_pg_connection),
    redis: Redis | None = Depends(get_redis),
) -> UserService:
    """Get UserService instance."""
    return UserService(pg_connection=pg_connection, redis=redis)
