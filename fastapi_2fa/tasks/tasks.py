from time import sleep

from celery import states

from fastapi_2fa.tasks.celery_conf import celery


@celery.task(
        bind=True,
        autoretry_for=(Exception,),
        retry_backoff=True,
        retry_kwargs={"max_retries": 5},
)
def send_email_task(self, email: dict) -> dict:

    self.update_state(
        state=states.PENDING,
        meta={'state': 'Sending email..'}
    )
    print('Sending email..')
    sleep(2)
    print('\nEmail sent:\n')
    self.update_state(
        state=states.PENDING,
        meta={'state': '..Email sent'}
    )
    print(email)
    return email
