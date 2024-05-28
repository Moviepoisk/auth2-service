from typing import Annotated

from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.auth_jwt import AuthJWTBearer
from fastapi import APIRouter, HTTPException, status, Query, Depends, Header
from fastapi.responses import RedirectResponse

from services import RoleService
from services.role import get_role_service
from src.models.role import RoleInDB
from src.models.user import UserLoginHistoryCreate, UserInDB
from src.services import RedisService, UserService
from src.services.redis import get_redis_service
from src.services.user import get_user_service
from src.services.oauth import OAuthProviderEnum, get_provider_settings, OAuthYandexService, get_oauth_yandex_service


DEFAULT_ROLE = "user"  # TODO завести константы


router = APIRouter(prefix="/oauth", tags=["oauth"])


@router.post("/login")
async def login(oauth_provider: OAuthProviderEnum):
    """Endpoint to get redirected by oauth provider."""
    try:
        provider_settings = get_provider_settings(provider_name=oauth_provider.value)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"OAuth provider '{oauth_provider.value}' currently not supported.",
        )
    redirect_url = provider_settings.auth_url + provider_settings.client_id
    print(redirect_url)  # for debug
    return RedirectResponse(url=redirect_url)


auth_dep = AuthJWTBearer()


@router.post("/callback/yandex")
async def callback(
    code: str = Query(...),
    user_agent: Annotated[str | None, Header()] = None,
    x_real_ip: Annotated[str | None, Header()] = None,
    authorize: AuthJWT = Depends(auth_dep),
    user_service: UserService = Depends(get_user_service),
    role_service: RoleService = Depends(get_role_service),
    redis_service: RedisService = Depends(get_redis_service),
    yandex_service: OAuthYandexService = Depends(get_oauth_yandex_service),
):
    # TODO подумать над сокрытием некоторой логики
    user_info = await yandex_service.get_user_info(code=code)

    if oauth_user := await yandex_service._get_oauth_user_by_id(oauth_id=user_info.get("id")):
        user = oauth_user.user
        user_roles = [str(RoleInDB.model_validate(role)) for role in user.roles]
    else:
        user = await yandex_service.create_oauth(
            oauth_id=user_info.get("id"),
            email=user_info.get("emails")[0],
            first_name=user_info.get("first_name"),
            last_name=user_info.get("last_name"),
        )
        role = await role_service.get_by_name(role_name=DEFAULT_ROLE)
        await role_service.assign_role(role=role, user=user)
        user_roles = [str(RoleInDB.model_validate(role))]

    access_token = await authorize.create_access_token(
        subject=user.email, user_claims={"roles": user_roles, "access_level": user.access_level}
    )
    refresh_token = await authorize.create_refresh_token(subject=user.email)

    await redis_service.set_refresh_token(email=user.email, refresh_token=refresh_token)

    await authorize.set_access_cookies(access_token)
    await authorize.set_refresh_cookies(refresh_token)

    login_history_data = UserLoginHistoryCreate(
        user_id=user.id,
        ip=x_real_ip,
        user_agent=user_agent,
    )
    await user_service.create_history_record(user_login_history=login_history_data)

    return UserInDB.model_validate(user)
