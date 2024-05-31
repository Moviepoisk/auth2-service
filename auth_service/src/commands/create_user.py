from asyncio import run as aiorun

import typer
from sqlalchemy import exc
from src.commands.base import user_service
from src.models.user import UserCreate


app = typer.Typer()


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


@app.command()
def main(
    email: str = typer.Option(..., help="The email of the user"),
    password: str = typer.Option(..., help="The password of the user"),
    first_name: str = typer.Option(..., help="The first name of the user"),
    last_name: str = typer.Option(..., help="The last name of the user"),
    access_level: int = typer.Option(..., help="The access level of the user"),
):
    aiorun(
        create_user(
            email=email, password=password, first_name=first_name, last_name=last_name, access_level=access_level
        )
    )


if __name__ == "__main__":
    typer.run(main)
