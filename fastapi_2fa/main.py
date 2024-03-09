import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from fastapi_2fa.api.endpoints.router import router
from fastapi_2fa.core.config import settings
from fastapi_2fa.db.session import SessionLocal
from fastapi_2fa.tasks.celery_conf import celery

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)


# routers
app.include_router(router=router, prefix=settings.API_V1_STR)


@app.on_event("startup")
async def app_startup():
    # CHECK DB
    try:
        db = SessionLocal()
        await db.execute("SELECT 1")
        print("Database is connected")
    except Exception:
        raise RuntimeError("Problems reaching db")
    finally:
        await db.close()

    # CHECK CELERY BROKER
    try:
        celery.broker_connection().ensure_connection(max_retries=3)
    except Exception as ex:
        raise RuntimeError("Failed to connect to celery broker, {}".format(str(ex)))
    print('Celery broker is running')

    # CHECK CELERY WORKER
    insp = celery.control.inspect()
    availability = insp.ping()
    if not availability:
        raise RuntimeError('Celery worker is not running')
    print('Celery worker is running')


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
    return "App is running"


if __name__ == '__main__':
    debug = True
    uvicorn.run(
        "fastapi_2fa.main:app",
        host='0.0.0.0',
        port=5555,
        reload=debug,
        use_colors=True,
    )
