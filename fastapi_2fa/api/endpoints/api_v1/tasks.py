from celery.result import AsyncResult
from fastapi import APIRouter

from fastapi_2fa.core.config import settings
from fastapi_2fa.core.utils import Email
from fastapi_2fa.tasks.tasks import send_email_task

tasks_router = APIRouter()


@tasks_router.get(
    "/test-celery",
    description="endpoint to test celery send mail function"
)
async def testcelery():
    """
    Test celery
    """
    email_ob = Email(
        to_=[settings.FAKE_EMAIL_SENDER],
        from_=settings.FAKE_EMAIL_SENDER,
        text_="Prova messaggio con Celery"
    )
    task = send_email_task.apply_async(kwargs={'email': email_ob.to_json()})
    task_id = task.task_id
    return {'task_id': task_id}


@tasks_router.get(
    "/taskstatus",
    description="endpoint to retrieve task status"
)
async def taskstatus(task_id):
    task = AsyncResult(task_id)
    if isinstance(task.result, Exception):
        task_result = str(task.result)
    else:
        task_result = task.result

    response = {
        'state': task.state,
        'result': task_result,
    }

    return response
