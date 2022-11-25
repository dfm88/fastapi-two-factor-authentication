from fastapi import APIRouter

from fastapi_2fa.api.endpoints.api_v1 import auth, users

router = APIRouter()

# users
router.include_router(users.user_router, prefix="/users", tags=["users"])

# auth
router.include_router(auth.auth_router, prefix="/auth", tags=["auth"])
