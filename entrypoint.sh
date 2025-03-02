#!/bin/bash
set -e

echo "Starting service: $SERVICE_TYPE in environment: $ENVIRONMENT"
echo "Build info: SHA=$COMMIT_SHA, Date=$BUILD_DATE"

if [ "$SERVICE_TYPE" = "data_fetcher" ]; then
    echo "Running data fetcher service..."
    exec python data_fetcher/src/main.py
else
    echo "Running API service..."
    exec uvicorn api.src.v1.main:app --host 0.0.0.0 --port 8000 --reload
fi 