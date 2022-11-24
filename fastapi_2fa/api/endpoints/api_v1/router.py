from fastapi import APIRouter

from fastapi_2fa.api.endpoints.api_v1 import users

router = APIRouter()

# users
router.include_router(users.user_router, prefix="/users", tags=["users"])
