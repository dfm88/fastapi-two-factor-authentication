from celery import Celery

from fastapi_2fa.core.config import settings

celery = Celery('my_celery', config_source=settings, namespace='CELERY')
