from asyncio import run as aiorun

import typer
from sqlalchemy import exc
from src.commands.base import role_service, user_service

users_roles = [
    {"user_email": "admin@mail.com", "role_name": ["admin"]},
    {"user_email": "staff@mail.com", "role_name": ["staff"]},
    {"user_email": "user@mail.com", "role_name": ["user"]},
    {"user_email": "staff_user@mail.com", "role_name": ["staff", "user"]},
]


async def assign_role(user_email: str, role_name: str) -> None:
    user = await user_service.get_by_email(user_email=user_email)
    role = await role_service.get_by_name(role_name=role_name)

    if role.id in await role_service.get_user_roles_ids(user_id=user.id):
        typer.secho(message=f"Role '{role_name}' already assigned to user '{user_email}' ...", fg=typer.colors.MAGENTA)
        return

    typer.secho(message=f"Assigning role '{role_name}' to user '{user_email}' ...", fg=typer.colors.BLUE)

    try:
        await role_service.assign_role(user=user, role=role)
    except exc.SQLAlchemyError as e:
        typer.secho(f"There is an SQLAlchemyError error: {e}", fg=typer.colors.RED)
    except Exception as e:
        typer.secho(f"There is an error: {e}", fg=typer.colors.RED)
    else:
        typer.secho(f"Role '{role_name}' assigned to user '{user_email}'.", fg=typer.colors.GREEN)


async def _main() -> None:
    for user_data in users_roles:
        for role in user_data.get("role_name"):
            await assign_role(user_email=user_data.get("user_email"), role_name=role)


def main():
    aiorun(_main())


if __name__ == "__main__":
    typer.run(main)
