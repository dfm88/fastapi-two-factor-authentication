# Import all the models, so that models.py won't crash on queries
from fastapi_2fa.db.base_class import Base  # noqa
from fastapi_2fa.models.users import User  # noqa