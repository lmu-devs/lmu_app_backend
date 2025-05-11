from pathlib import Path
from typing import Optional, Union

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

    def query(self, query: str, variables: dict = None) -> dict:
        """
        Execute a GraphQL query against the Directus API.

        Args:
            query (str): The GraphQL query string
            variables (dict, optional): Variables for the GraphQL query

        Returns:
            dict: The JSON response from the API
        """
        response = self._client.post("/graphql", json={"query": query, "variables": variables or {}})
        response.raise_for_status()
        return response.json()

    def execute_query_file(self, query_file_path: Union[str, Path], variables: dict = None) -> dict:
        """
        Execute a GraphQL query from a file against the Directus API.

        Args:
            query_file_path (Union[str, Path]): Path to the GraphQL query file
            variables (dict, optional): Variables for the GraphQL query

        Returns:
            dict: The JSON response from the API

        Raises:
            FileNotFoundError: If the query file doesn't exist
            IOError: If there's an error reading the file
        """
        query_path = Path(query_file_path)
        try:
            with open(query_path, "r") as file:
                query_string = file.read()
            return self.query(query_string, variables)
        except FileNotFoundError:
            raise FileNotFoundError(f"GraphQL query file not found: {query_file_path}")
        except IOError as e:
            raise IOError(f"Error reading GraphQL query file: {e}")

    def close(self):
        """Close the HTTP client connection."""
        if self._client:
            self._client.close()
            self._client = None
