FROM python:3.12-slim

# Set build arguments
ARG BUILD_ENV=development
ARG COMMIT_SHA=unknown
ARG BUILD_DATE=unknown

# Set environment variables
ENV ENVIRONMENT=${BUILD_ENV}
ENV COMMIT_SHA=${COMMIT_SHA}
ENV BUILD_DATE=${BUILD_DATE}

WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./shared /app/shared
COPY ./api /app/api
COPY ./data_fetcher /app/data_fetcher
COPY ./alembic /app/alembic
COPY ./alembic.ini /app/alembic.ini

# Default to API service
ENV SERVICE_TYPE=api

# Entrypoint script to determine which service to run
COPY docker/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"] 