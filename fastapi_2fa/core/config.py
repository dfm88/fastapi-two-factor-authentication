import os
from functools import lru_cache
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from pydantic import AnyHttpUrl, BaseSettings, PostgresDsn, validator

load_dotenv(dotenv_path="./env/.env")


class BaseConfig(BaseSettings):
    API_V1_STR: str = os.environ.get("API_V1_STR")
    PROJECT_NAME: str = os.environ.get("PROJECT_NAME")

    JWT_SECRET_KEY: str = os.environ.get("JWT_SECRET_KEY")
    JWT_SECRET_KEY_REFRESH: str = os.environ.get("JWT_SECRET_KEY_REFRESH")
    PRE_TFA_SECRET_KEY: str = os.environ.get("PRE_TFA_SECRET_KEY")

    ALGORITHM = os.environ.get("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 15)
    REFRESH_TOKEN_EXPIRE_MINUTES: int = os.environ.get(
        "REFRESH_TOKEN_EXPIRE_MINUTES", 60 * 24
    )  # 24 h
    PRE_TFA_TOKEN_EXPIRE_MINUTES: int = os.environ.get(
        "PRE_TFA_TOKEN_EXPIRE_MINUTES", 2
    )

    BACKEND_CORS_ORIGINS: str | list[AnyHttpUrl] = os.environ.get(
        "BACKEND_CORS_ORIGINS", "http://localhost:5555"
    )

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
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    class Config:
        case_sensitive = True


class DevelopmentConfig(BaseConfig):
    LOGGING_LEVEL = "DEBUG"


class ProductionConfig(BaseConfig):
    LOGGING_LEVEL = "INFO"


class TestingConfig(BaseConfig):
    LOGGING_LEVEL = "DEBUG"


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
