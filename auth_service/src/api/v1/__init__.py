from fastapi import APIRouter
from src.api.v1.endpoints import auth, role, user

router = APIRouter(prefix="/v1", tags=["Version 1"])


router.include_router(user.router)
router.include_router(auth.router)
router.include_router(role.router)
