from fastapi import APIRouter

from fastapi_2fa.api.endpoints.api_v1 import (auth, tasks, two_factor_auth,
                                              users)

router = APIRouter()

# users
router.include_router(users.user_router, prefix="/users", tags=["users"])

# auth
router.include_router(auth.auth_router, prefix="/auth", tags=["auth"])

# tfa
router.include_router(two_factor_auth.tfa_router, prefix="/tfa", tags=["tfa"])

# tasks
router.include_router(tasks.tasks_router, prefix="/tasks", tags=["tasks"])
