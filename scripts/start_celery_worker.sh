#!/bin/bash

set -o errexit
set -o nounset

celery -A fastapi_2fa.tasks.celery_conf worker --loglevel=info