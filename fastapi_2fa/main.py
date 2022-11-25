import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from fastapi_2fa.api.endpoints.api_v1.router import router
from fastapi_2fa.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)


app.include_router(router=router, prefix=settings.API_V1_STR)


# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get('/')
async def main():
    return "APp is running"


if __name__ == '__main__':
    debug = True
    uvicorn.run(
        "fastapi_2fa.main:app",
        host='0.0.0.0',
        port=5555,
        reload=debug,
        use_colors=True,
    )
