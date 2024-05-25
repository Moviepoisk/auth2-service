from types import coroutine

from async_fastapi_jwt_auth import AuthJWT
from fastapi import Depends, HTTPException, status

from src.core.dependencies import get_redis
from src.models.role import RoleEnum


@AuthJWT.token_in_denylist_loader
async def check_if_token_in_denylist(decrypted_token: dict) -> bool:
    redis = await get_redis()
    jti = decrypted_token["jti"]
    return bool(await redis.get(f"{decrypted_token['sub']}:revoke:{decrypted_token['type']}:{jti}"))


def has_permission(roles: list[RoleEnum], access_level: int) -> coroutine:
    async def check_role(authorize: AuthJWT = Depends()) -> None:
        await authorize.jwt_required()
        user_data = await authorize.get_raw_jwt()
        user_roles = user_data.get("roles")
        user_level = user_data.get("access_level")

        if not any(role in [role.value for role in roles] for role in user_roles):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not allowed for this action.")

        if user_level < access_level:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User does not have the required level.")

    return check_role
