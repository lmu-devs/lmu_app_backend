from pathlib import Path
from typing import Optional, Union
import logging

import httpx

from shared.src.core.settings import get_settings
from shared.src.core.exceptions import APIException
from shared.src.core.logging import get_service_logger

logger = get_service_logger(__name__)


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
            
                    # Log request details
            # logger.info("Making GraphQL request:")
            # logger.info(f"URL: {self._client.base_url}/graphql")
            # logger.info(f"Headers: {self._client.headers}")
            # logger.info(f"Payload: {payload}")
            
            try:
                response = self._client.post("/graphql", json=payload)
                
                # Log response details
                # logger.info(f"Response status: {response.status_code}")
                # logger.info(f"Response headers: {response.headers}")
                # logger.info(f"Response body: {response.text}")
                
                # Check for HTTP errors
                if response.status_code >= 400:
                    raise APIException(
                        status_code=response.status_code,
                        detail=f"GraphQL request failed: {response.text}",
                        error_code="GRAPHQL_ERROR",
                        extra={
                            "query": query[:200],
                            "variables": variables,
                            "operation": operation_name,
                            "response": response.text
                        }
                    )
                
                # Parse response
                json_response = response.json()
                
                # Check for GraphQL errors
                if "errors" in json_response:
                    error_messages = [error.get("message", "Unknown GraphQL error") for error in json_response["errors"]]
                    error_detail = "; ".join(error_messages)
                    # logger.error(f"GraphQL Error: {error_detail}")
                    # logger.error(f"Query: {query[:200]}...")
                    # logger.error(f"Variables: {variables}")
                    # logger.error(f"Operation: {operation_name}")
                    raise APIException(
                        status_code=400,
                        detail=f"GraphQL Error: {error_detail}",
                        error_code="GRAPHQL_ERROR",
                        extra={
                            "query": query[:200],
                            "variables": variables,
                            "operation": operation_name
                        }
                    )
                
                return json_response
            
            except httpx.HTTPStatusError as e:
                # Log the detailed error response
                error_detail = e.response.text if e.response else "No response text"
                # logger.error(f"GraphQL Error: {e}")
                # logger.error(f"Error Response: {error_detail}")
                # logger.error(f"Query: {query[:200]}...")
                # logger.error(f"Variables: {variables}")
                # logger.error(f"Operation: {operation_name}")
                
                raise APIException(
                    status_code=e.response.status_code,
                    detail=f"GraphQL request failed: {error_detail}",
                    error_code="GRAPHQL_REQUEST_ERROR",
                    extra={
                        "query": query[:200],
                        "variables": variables,
                        "operation": operation_name
                    }
                )

    def execute_query_file(self, query_file_path: Union[str, Path], variables: dict = None, operation_name: str = None) -> dict:
        query_path = Path(query_file_path)
        # logger.info(f"Reading GraphQL query from: {query_path} (absolute: {query_path.absolute()})")
        
        try:
            with open(query_path, "r") as file:
                query_string = file.read()
                # logger.info(f"Successfully read query file. Length: {len(query_string)} chars")
                # logger.info(f"Query content: {query_string[:200]}...")  # Log first 200 chars
        except Exception as e:
            logger.error(f"Failed to read query file: {e}")
            raise
            
        return self.query(query_string, variables, operation_name)

    def close(self):
        """Close the HTTP client connection."""
        if self._client:
            self._client.close()
            self._client = None
