from uuid import UUID

from async_fastapi_jwt_auth.auth_jwt import AuthJWT, AuthJWTBearer
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page

from src.models.user import UserCreate, UserInDB, UserLoginHistoryInDB, UserUpdateCredentials
from src.services.user import UserService, get_user_service

router = APIRouter(prefix="/users", tags=["user"])

auth_dep = AuthJWTBearer()


@router.get("/history", response_model=Page[UserLoginHistoryInDB], status_code=status.HTTP_200_OK)
async def get_user_history(
    authorize: AuthJWT = Depends(auth_dep),
    user_service: UserService = Depends(get_user_service),
) -> Page[UserLoginHistoryInDB]:
    await authorize.jwt_required()
    user_email = await authorize.get_jwt_subject()
    return await user_service.get_user_login_history(email=user_email)


@router.post("/signup", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
async def create_user(user_create: UserCreate, user_service: UserService = Depends(get_user_service)) -> UserInDB:
    if await user_service.get_by_email(user_email=user_create.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        )
    try:
        return await user_service.create(user_create=user_create)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
        )


@router.patch("/{user_id}/creds", response_model=UserInDB, status_code=status.HTTP_200_OK)
async def change_user_credentials(
    user_id: UUID,
    update_credentials: UserUpdateCredentials,
    authorize: AuthJWT = Depends(auth_dep),
    user_service: UserService = Depends(get_user_service),
) -> UserInDB:
    await authorize.jwt_required()

    user = await user_service.get_by_id(user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user_email = await authorize.get_jwt_subject()
    if user.email != user_email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can't change credentials for another user",
        )

    if not user.check_password(update_credentials.old_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid old password",
        )

    if update_credentials.old_password == update_credentials.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password should be different from the old one",
        )

    return await user_service.update_credentials(user=user, new_password=update_credentials.new_password)
