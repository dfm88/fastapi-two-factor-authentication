#!/bin/bash

set -o errexit
set -o nounset

celery -A fastapi_2fa.tasks.celery_conf flower --loglevel=info --port=5557