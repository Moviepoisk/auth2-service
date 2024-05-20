from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from src.api.v1.utils import has_permission
from src.models.response import ResponseModel
from src.models.role import RoleCRUD, RoleEnum, RoleInDB
from src.services.role import RoleService, get_role_service
from src.services.user import UserService, get_user_service

router = APIRouter(prefix="/roles", tags=["roles"])


@router.post(
    "/",
    response_model=RoleInDB,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(has_permission(roles=[RoleEnum.admin], access_level=5))],
)
async def create_role(
    role_data: RoleCRUD,
    role_service: RoleService = Depends(get_role_service),
) -> RoleInDB:
    """Endpoint to Create a role."""
    if await role_service.get_by_name(role_name=role_data.name):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Role already exists",
        )

    try:
        return await role_service.create(role_data=role_data)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
        )


@router.get(
    "/",
    response_model=list[RoleInDB],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(has_permission(roles=[RoleEnum.admin, RoleEnum.staff], access_level=1))],
)
async def get_roles(
    role_service: RoleService = Depends(get_role_service),
) -> list[RoleInDB]:
    """Endpoint to Read roles."""
    try:
        return await role_service.get_list()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
        )


@router.put(
    "/{role_id}",
    response_model=RoleInDB,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(has_permission(roles=[RoleEnum.admin], access_level=5))],
)
async def update_role(
    role_id: UUID,
    role_data: RoleCRUD,
    role_service: RoleService = Depends(get_role_service),
) -> RoleInDB:
    """Endpoint to Update a role."""
    if not (role := await role_service.get_by_id(role_id=role_id)):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Role does not exist",
        )

    try:
        return await role_service.update(role=role, role_data=role_data)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
        )


@router.delete(
    "/{role_id}",
    response_model=RoleInDB,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(has_permission(roles=[RoleEnum.admin], access_level=5))],
)
async def delete_role(
    role_id: UUID,
    role_service: RoleService = Depends(get_role_service),
) -> RoleInDB:
    """Endpoint to Delete a role."""
    if not (role := await role_service.get_by_id(role_id=role_id)):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Role does not exist",
        )

    try:
        return await role_service.delete(role=role)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
        )


@router.post(
    "/{role_id}/users/",
    response_model=ResponseModel,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(has_permission(roles=[RoleEnum.admin], access_level=5))],
)
async def assign_role(
    role_id: UUID,
    user_id: UUID,
    role_service: RoleService = Depends(get_role_service),
    user_service: UserService = Depends(get_user_service),
) -> ResponseModel:
    """Endpoint to Assign a role to user."""
    if not (role := await role_service.get_by_id(role_id)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )
    if not (user := await user_service.get_by_id(user_id)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if role_id in await role_service.get_user_roles_ids(user_id=user_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Role already assigned to the user",
        )

    try:
        await role_service.assign_role(role=role, user=user)
        return ResponseModel(detail="Role successfully assigned")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
        )


@router.delete(
    "/{role_id}/users/",
    response_model=ResponseModel,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(has_permission(roles=[RoleEnum.admin], access_level=5))],
)
async def revoke_role(
    role_id: UUID,
    user_id: UUID,
    role_service: RoleService = Depends(get_role_service),
    user_service: UserService = Depends(get_user_service),
) -> ResponseModel:
    """Endpoint to Revoke a role from user."""
    if not (role := await role_service.get_by_id(role_id)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )
    if not (user := await user_service.get_by_id(user_id)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if role_id not in await role_service.get_user_roles_ids(user_id=user_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Role already revoked from the user",
        )

    try:
        await role_service.revoke_role(role=role, user=user)
        return ResponseModel(detail="Role successfully revoked")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
        )
