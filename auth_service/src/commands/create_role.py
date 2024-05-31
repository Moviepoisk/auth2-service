from asyncio import run as aiorun

import typer
from sqlalchemy import exc
from src.commands.base import role_service
from src.models.role import RoleCRUD


app = typer.Typer()


async def create_role(name: str) -> None:
    if await role_service.get_by_name(role_name=name):
        typer.secho(message=f"Role '{name}' already exists", fg=typer.colors.MAGENTA)
        return

    typer.secho(message=f"Creating role: '{name}' ...", fg=typer.colors.BLUE)

    role_data = RoleCRUD(name=f"{name}")

    try:
        await role_service.create(role_data=role_data)
    except exc.SQLAlchemyError as e:
        typer.secho(message=f"There is an SQLAlchemyError error: {e}", fg=typer.colors.RED)
    except Exception as e:
        typer.secho(message=f"There is an error: {e}", fg=typer.colors.RED)
    else:
        typer.secho(message=f"Role '{name}' created.", fg=typer.colors.GREEN)


@app.command()
def main(name: str = typer.Option(..., help="The role of the user")):
    aiorun(create_role(name=name))


if __name__ == "__main__":
    typer.run(main)
