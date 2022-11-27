import os
from functools import lru_cache
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from pydantic import (AnyHttpUrl, BaseSettings, EmailStr, Field, PostgresDsn,
                      validator)

load_dotenv(dotenv_path="./env/.env")


class BaseConfig(BaseSettings):
    API_V1_STR: str = os.environ.get("API_V1_STR")
    PROJECT_NAME: str = os.environ.get("PROJECT_NAME")

    FAKE_EMAIL_SENDER: EmailStr = os.environ.get("FAKE_EMAIL_SENDER")

    # # JWT
    JWT_SECRET_KEY: str = os.environ.get("JWT_SECRET_KEY")
    JWT_SECRET_KEY_REFRESH: str = os.environ.get("JWT_SECRET_KEY_REFRESH")
    PRE_TFA_SECRET_KEY: str = os.environ.get("PRE_TFA_SECRET_KEY")
    ALGORITHM: str = os.environ.get("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 15)
    REFRESH_TOKEN_EXPIRE_MINUTES: int = os.environ.get(
        "REFRESH_TOKEN_EXPIRE_MINUTES", 60 * 24
    )  # 24 h

    # # 2 FACTOR AUTHENTICATION
    FERNET_KEY_TFA_TOKEN: str = os.environ.get("FERNET_KEY_TFA_TOKEN")
    PRE_TFA_TOKEN_EXPIRE_MINUTES: int = os.environ.get(
        "PRE_TFA_TOKEN_EXPIRE_MINUTES", 2
    )
    TFA_BACKUP_TOKENS_NR: int = os.environ.get("TFA_BACKUP_TOKENS_NR")
    TFA_TOKEN_LENGTH: int = os.environ.get("TFA_TOKEN_LENGTH")
    TOTP_ISSUER_NAME: str = os.environ.get("TOTP_ISSUER_NAME")
    # default tolerance = 30 sec
    # this number is multiplied for 30 sec to increas it.
    # -->MAX = 10 => 5 minutes
    TOTP_TOKEN_TOLERANCE: int = Field(
        default=os.environ.get("TOTP_TOKEN_TOLERANCE", 2),
        gt=0,
        le=10
    )

    # # CORS
    BACKEND_CORS_ORIGINS: AnyHttpUrl | list[AnyHttpUrl] = os.environ.get(
        "BACKEND_CORS_ORIGINS", "http://localhost:5555"
    )

    # # DB
    SQLALCHEMY_DATABASE_URI: str = os.environ.get("SQLALCHEMY_DATABASE_URI")

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if v is None:
            raise ValueError(v)
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_HOST"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    # # CELERY
    CELERY_BROKER_URL: str = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/0")
    result_backend: str = os.environ.get("result_backend", "redis://redis:6379/0")
    CELERY_WORKER_PREFETCH_MULTIPLIER = 1
    # Celery ACK the queue only when task is completed
    CELERY_TASK_ACKS_LATE = True
    imports = ("fastapi_2fa.tasks.tasks",)
    task_serializer = "pickle"
    accept_content = ('pickle', 'json',)

    class Config:
        case_sensitive = True


class DevelopmentConfig(BaseConfig):
    LOGGING_LEVEL = "DEBUG"


class ProductionConfig(BaseConfig):
    LOGGING_LEVEL = "INFO"


class TestingConfig(BaseConfig):
    # define new attributes with respect to BaseConfig
    DATABASE_CONNECT_DICT: dict = {"check_same_thread": False}
    LOGGING_LEVEL = 'DEBUG'
    SQLALCHEMY_DATABASE_TEST_SYNC_URI: str = "sqlite:///tests/test_db.db"

    # celery test config
    task_always_eager = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # override attributes of BaseConfig
        # https://fastapi.tiangolo.com/advanced/testing-database/
        self.SQLALCHEMY_DATABASE_URI: str = "sqlite+aiosqlite:///tests/test_db.db"


@lru_cache()
def get_settings():
    config_cls_dict = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig,
    }

    config_name = os.environ.get("FASTAPI_CONFIG", "development")
    print("Running app in **%s** mode" % config_name)
    config_cls = config_cls_dict[config_name]
    return config_cls()


settings = get_settings()
