from asyncio import run as aiorun

import typer
from sqlalchemy import exc
from src.commands.base import role_service, user_service


app = typer.Typer()


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


@app.command()
def main(
    email: str = typer.Option(..., help="The email of the user"),
    role: str = typer.Option(..., help="The role of the user"),
):
    aiorun(assign_role(user_email=email, role_name=role))


if __name__ == "__main__":
    typer.run(main)
