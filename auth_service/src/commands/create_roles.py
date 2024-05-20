from asyncio import run as aiorun

import typer
from sqlalchemy import exc
from src.commands.base import role_service
from src.core.config.base import commands_init_names
from src.models.role import RoleCRUD


async def create_role(role_name: str) -> None:
    if await role_service.get_by_name(role_name=role_name):
        typer.secho(message=f"Role '{role_name}' already exists", fg=typer.colors.MAGENTA)
        return

    typer.secho(message=f"Creating role: '{role_name}' ...", fg=typer.colors.BLUE)

    role_data = RoleCRUD(name=f"{role_name}")

    try:
        await role_service.create(role_data=role_data)
    except exc.SQLAlchemyError as e:
        typer.secho(message=f"There is an SQLAlchemyError error: {e}", fg=typer.colors.RED)
    except Exception as e:
        typer.secho(message=f"There is an error: {e}", fg=typer.colors.RED)
    else:
        typer.secho(message=f"Role '{role_name}' created.", fg=typer.colors.GREEN)


async def _main():
    for role_name in commands_init_names.default_roles:
        await create_role(role_name=role_name)


def main():
    aiorun(_main())


if __name__ == "__main__":
    typer.run(main)
