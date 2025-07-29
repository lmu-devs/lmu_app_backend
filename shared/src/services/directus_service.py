from pathlib import Path
from typing import Optional, Union
import logging

import httpx

from shared.src.core.settings import get_settings


class DirectusService:
    _instance: Optional["DirectusService"] = None
    _client: Optional[httpx.Client] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._client is None:
            settings = get_settings()
            self._client = httpx.Client(
                base_url=settings.DIRECTUS_BASE_URL,
                headers={
                    "Authorization": f"Bearer {settings.DIRECTUS_ACCESS_TOKEN}",
                    "Content-Type": "application/json",
                },
            )

    def query(self, query: str, variables: dict = None, operation_name: str = None) -> dict:
        payload = {"query": query, "variables": variables or {}}
        if operation_name:
            payload["operationName"] = operation_name
        
        try:
            response = self._client.post("/graphql", json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            # Log the detailed error response
            error_detail = e.response.text if e.response else "No response text"
            logging.error(f"GraphQL Error: {e}")
            logging.error(f"Error Response: {error_detail}")
            logging.error(f"Query: {query[:200]}...")  # Log first 200 chars of query
            logging.error(f"Variables: {variables}")
            logging.error(f"Operation: {operation_name}")
            raise

    def execute_query_file(self, query_file_path: Union[str, Path], variables: dict = None, operation_name: str = None) -> dict:
        query_path = Path(query_file_path)
        with open(query_path, "r") as file:
            query_string = file.read()
        return self.query(query_string, variables, operation_name)

    def close(self):
        """Close the HTTP client connection."""
        if self._client:
            self._client.close()
            self._client = None
