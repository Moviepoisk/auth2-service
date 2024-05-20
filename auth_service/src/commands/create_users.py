from asyncio import run as aiorun

import typer
from sqlalchemy import exc
from src.commands.base import user_service
from src.core.config.base import superuser_credentials
from src.models.user import UserCreate

USERS = [
    {
        "email": superuser_credentials.email,
        "password": superuser_credentials.password,
        "first_name": superuser_credentials.first_name,
        "last_name": superuser_credentials.last_name,
        "access_level": superuser_credentials.access_level,
    },
    {
        "email": "staff@mail.com",
        "password": "staff_password",
        "first_name": "staff",
        "last_name": "staff",
        "access_level": 3,
    },
    {
        "email": "user@mail.com",
        "password": "user_password",
        "first_name": "user",
        "last_name": "user",
        "access_level": 1,
    },
    {
        "email": "staff_user@mail.com",
        "password": "staff_user_password",
        "first_name": "staff_user",
        "last_name": "staff_user",
        "access_level": 3,
    },
]


async def create_user(email: str, password: str, first_name: str, last_name: str, access_level: int):
    if await user_service.get_by_email(user_email=email):
        typer.secho(message=f"User '{email}' already exists", fg=typer.colors.MAGENTA)
        return

    typer.secho(message=f"Creating user: '{email}' ...", fg=typer.colors.BLUE)
    user_create = UserCreate(
        email=email, password=password, first_name=first_name, last_name=last_name, access_level=access_level
    )

    try:
        await user_service.create(user_create=user_create)
    except exc.SQLAlchemyError as e:
        typer.secho(message=f"There is an SQLAlchemyError error: {e}", fg=typer.colors.RED)
    except Exception as e:
        typer.secho(message=f"There is an error: {e}", fg=typer.colors.RED)
    else:
        typer.secho(message=f"User '{email}' created.", fg=typer.colors.GREEN)


async def _main() -> None:
    for user in USERS:
        await create_user(
            email=user.get("email"),
            password=user.get("password"),
            first_name=user.get("first_name"),
            last_name=user.get("last_name"),
            access_level=user.get("access_level"),
        )


def main():
    aiorun(_main())


if __name__ == "__main__":
    typer.run(main)
