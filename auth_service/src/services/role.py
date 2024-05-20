import logging
from uuid import UUID

from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from redis.asyncio import Redis
from sqlalchemy import and_, delete, exc, insert, select, update
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import selectinload
from src.core.dependencies import get_pg_connection, get_redis
from src.models.db import User
from src.models.db.role import Role, association_table
from src.models.role import RoleCRUD, RoleInDB
from src.services.base import BaseService


class RoleService(BaseService):
    async def get_user_roles_ids(self, user_id: UUID) -> list[RoleCRUD]:
        async with self.get_session() as session:
            async with session.begin():
                query = await session.execute(select(User).options(selectinload(User.roles)).where(User.id == user_id))
                user = query.scalars().first()
                if user:
                    roles = user.roles
                    return [role.id for role in roles]
                else:
                    return []

    async def get_by_id(self, role_id: UUID) -> Role | None:
        async with self.get_session() as session:
            async with session.begin():
                try:
                    return (await session.scalars(select(Role).where(Role.id == role_id))).first()
                except exc.SQLAlchemyError:
                    logging.error("Could not fetch role with role_id = '{}'".format(role_id), exc_info=True)

    async def get_by_name(self, role_name: str) -> Role | None:
        async with self.get_session() as session:
            async with session.begin():
                try:
                    return (await session.scalars(select(Role).where(Role.name == role_name))).first()
                except exc.SQLAlchemyError:
                    logging.error("Could not fetch role with role_name = '{}'".format(role_name), exc_info=True)

    async def get_list(self) -> list[RoleInDB] | None:
        async with self.get_session() as session:
            async with session.begin():
                try:
                    roles = (await session.scalars(select(Role))).all()
                    return [RoleInDB(id=role.id, name=role.name) for role in roles]
                except exc.SQLAlchemyError:
                    logging.error("Could not fetch list of roles", exc_info=True)
                    raise

    async def create(self, role_data: RoleCRUD) -> RoleInDB:
        async with self.get_session() as session:
            async with session.begin():
                try:
                    role_dto = jsonable_encoder(role_data)
                    role = Role(**role_dto)
                    session.add(role)
                    await session.commit()
                    return role
                except exc.SQLAlchemyError:
                    await session.rollback()
                    logging.error("Could not create a role with name '{}'".format(role_data.name), exc_info=True)
                    raise

    async def update(self, role: Role, role_data: RoleCRUD) -> RoleInDB:
        async with self.get_session() as session:
            async with session.begin():
                try:
                    await session.execute(update(Role).where(Role.id == role.id).values(name=role_data.name))
                    await session.commit()
                    return role
                except exc.SQLAlchemyError:
                    await session.rollback()
                    logging.error("Could not update a role with name '{}'".format(role_data.name), exc_info=True)
                    raise

    async def delete(self, role: Role) -> RoleInDB:
        async with self.get_session() as session:
            async with session.begin():
                try:
                    await session.execute(delete(association_table).where(association_table.c.role_id == role.id))
                    await session.delete(role)
                    await session.commit()
                    return role
                except exc.SQLAlchemyError:
                    await session.rollback()
                    logging.error("Could not delete a role with name '{}'".format(role.name), exc_info=True)
                    raise

    async def assign_role(self, role: Role, user: User) -> None:
        async with self.get_session() as session:
            async with session.begin():
                try:
                    await session.execute(insert(association_table).values(role_id=role.id, user_id=user.id))
                    await session.commit()
                except exc.SQLAlchemyError:
                    await session.rollback()
                    logging.error(
                        "Could not assign a role '{}' to a user '{}'".format(role.name, user.email), exc_info=True
                    )
                    raise

    async def revoke_role(self, role: Role, user: User) -> None:
        async with self.get_session() as session:
            async with session.begin():
                try:
                    await session.execute(
                        delete(association_table).where(
                            and_(association_table.c.role_id == role.id, association_table.c.user_id == user.id)
                        )
                    )
                    await session.commit()
                except exc.SQLAlchemyError:
                    await session.rollback()
                    logging.error(
                        "Could not revoke a role '{}' from a user '{}'".format(role.name, user.email), exc_info=True
                    )
                    raise


def get_role_service(
    pg_connection: AsyncEngine = Depends(get_pg_connection),
    redis: Redis | None = Depends(get_redis),
) -> RoleService:
    """Get RoleService instance."""
    return RoleService(pg_connection=pg_connection, redis=redis)
