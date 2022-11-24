#!/bin/bash
# export IMAGE_NAME=smartacc_preproc_tx   
echo "ENTRYPOINT $IMAGE_NAME"

# alembic
# alembic upgrade head

uvicorn ${IMAGE_NAME}.main:app --host 0.0.0.0 --port 5555