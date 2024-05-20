from typing import Annotated

from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.auth_jwt import AuthJWTBearer
from fastapi import APIRouter, Depends, Header, HTTPException, status
from src.core.config.base import base_auth_jwt_settings
from src.models.role import RoleInDB
from src.models.user import UserInDB, UserLogin, UserLoginHistoryCreate, UserResponse
from src.services.redis import RedisService, get_redis_service
from src.services.user import UserService, get_user_service

router = APIRouter(prefix="/auth", tags=["auth"])

auth_dep = AuthJWTBearer()


@router.post("/login", response_model=UserInDB, status_code=status.HTTP_200_OK)
async def login(
    user_login: UserLogin,
    user_agent: Annotated[str | None, Header()] = None,
    x_real_ip: Annotated[str | None, Header()] = None,
    authorize: AuthJWT = Depends(auth_dep),
    user_service: UserService = Depends(get_user_service),
    redis_service: RedisService = Depends(get_redis_service),
) -> UserInDB:
    user = await user_service.get_by_email(user_login.email)
    if not user or not user.check_password(user_login.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    user_roles = [str(RoleInDB.model_validate(role)) for role in user.roles]

    access_token = await authorize.create_access_token(
        subject=user_login.email, user_claims={"roles": user_roles, "access_level": user.access_level}
    )
    refresh_token = await authorize.create_refresh_token(subject=user_login.email)

    await redis_service.set_refresh_token(email=user_login.email, refresh_token=refresh_token)

    await authorize.set_access_cookies(access_token)
    await authorize.set_refresh_cookies(refresh_token)

    login_history_data = UserLoginHistoryCreate(
        user_id=user.id,
        ip=x_real_ip,
        user_agent=user_agent,
    )
    await user_service.create_history_record(user_login_history=login_history_data)

    return UserInDB.model_validate(user)


@router.post("/logout", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def logout(
    authorize: AuthJWT = Depends(auth_dep), redis_service: RedisService = Depends(get_redis_service)
) -> UserResponse:
    await authorize.jwt_refresh_token_required()

    raw_jwt = await authorize.get_raw_jwt()

    for token_name in ["access", "refresh"]:
        await redis_service.revoke_token(
            login=raw_jwt["sub"],
            token_name=token_name,
            token_value=raw_jwt["jti"],
            ttl=base_auth_jwt_settings.access_expires_time,
        )

    await authorize.unset_access_cookies()
    await authorize.unset_refresh_cookies()

    return UserResponse(msg="User has been logged out.")


@router.post("/refresh", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def refresh(
    authorize: AuthJWT = Depends(auth_dep),
    redis_service: RedisService = Depends(get_redis_service),
) -> UserResponse:
    await authorize.jwt_refresh_token_required()

    current_user = await authorize.get_jwt_subject()
    user_roles = (await authorize.get_raw_jwt()).get("roles")
    user_access_level = (await authorize.get_raw_jwt()).get("access_level")

    new_access_token = await authorize.create_access_token(
        subject=current_user, user_claims={"roles": user_roles, "access_level": user_access_level}
    )
    new_refresh_token = await authorize.create_refresh_token(subject=current_user)

    await redis_service.set_refresh_token(email=current_user, refresh_token=new_refresh_token)

    await authorize.set_access_cookies(new_access_token)
    await authorize.set_refresh_cookies(new_refresh_token)
    return UserResponse(msg="Tokens have been refreshed")


@router.delete("/access-revoke", status_code=status.HTTP_204_NO_CONTENT)
async def access_revoke(
    authorize: AuthJWT = Depends(auth_dep), redis_service: RedisService = Depends(get_redis_service)
) -> None:
    await authorize.jwt_required()

    raw_jwt = await authorize.get_raw_jwt()
    await redis_service.revoke_token(
        email=raw_jwt["sub"],
        token_name="access",
        token_value=raw_jwt["jti"],
        ttl=base_auth_jwt_settings.access_expires_time,
    )


@router.delete("/refresh-revoke", status_code=status.HTTP_204_NO_CONTENT)
async def refresh_revoke(
    authorize: AuthJWT = Depends(auth_dep), redis_service: RedisService = Depends(get_redis_service)
) -> None:
    await authorize.jwt_refresh_token_required()

    raw_jwt = await authorize.get_raw_jwt()
    await redis_service.revoke_token(
        email=raw_jwt["sub"],
        token_name="refresh",
        token_value=raw_jwt["jti"],
        ttl=base_auth_jwt_settings.access_expires_time,
    )
