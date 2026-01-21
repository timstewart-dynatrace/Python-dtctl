"""Base class for resource handlers.

Provides common functionality for all resource handlers including
CRUD operations and error handling.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

from dtctl.client import Client, APIError


T = TypeVar("T", bound=BaseModel)


class ResourceHandler(ABC, Generic[T]):
    """Base class for resource handlers."""

    def __init__(self, client: Client):
        self.client = client

    @property
    @abstractmethod
    def resource_name(self) -> str:
        """Human-readable resource name (e.g., 'workflow')."""
        pass

    @property
    @abstractmethod
    def api_path(self) -> str:
        """Base API path for this resource."""
        pass

    def _handle_error(self, operation: str, error: APIError) -> None:
        """Handle API errors with descriptive messages."""
        if error.status_code == 404:
            raise ValueError(f"{self.resource_name.title()} not found")
        elif error.status_code == 403:
            raise PermissionError(
                f"Permission denied for {operation} on {self.resource_name}"
            )
        elif error.status_code == 409:
            raise ValueError(f"Conflict: {self.resource_name} already exists or version mismatch")
        else:
            raise RuntimeError(f"Failed to {operation} {self.resource_name}: {error}")


class CRUDHandler(ResourceHandler[T]):
    """Handler with standard CRUD operations."""

    @property
    def list_key(self) -> str:
        """Key in response containing the list of items."""
        return "results"

    @property
    def id_field(self) -> str:
        """Field name for the resource ID."""
        return "id"

    @property
    def pagination_key(self) -> str:
        """Query parameter key for pagination cursor.

        Override in subclass if API uses different key (e.g., 'page-key').
        """
        return "nextPageKey"

    @property
    def supports_pagination(self) -> bool:
        """Whether this resource supports pagination.

        Override in subclass to disable pagination for APIs that don't support it.
        """
        return True

    def list(self, **params: Any) -> list[dict[str, Any]]:
        """List all resources with automatic pagination.

        Args:
            **params: Query parameters for filtering

        Returns:
            List of resource dictionaries
        """
        try:
            all_results: list[dict[str, Any]] = []
            next_page_key: str | None = None

            while True:
                # Build request params
                if next_page_key:
                    # For subsequent pages, include original params along with page key
                    if self.pagination_key == "page-key":
                        request_params = {**params, "page-key": next_page_key}
                    else:
                        request_params = {**params, "nextPageKey": next_page_key}
                else:
                    request_params = params

                response = self.client.get(self.api_path, params=request_params)
                data = response.json()

                # Handle paginated responses
                if isinstance(data, dict):
                    results = data.get(self.list_key, [])
                    all_results.extend(results)

                    # Check for next page (try both common patterns)
                    if self.supports_pagination:
                        next_page_key = data.get("nextPageKey") or data.get("next_page_key")
                        if not next_page_key:
                            break
                    else:
                        break
                else:
                    # Response is a list directly
                    all_results.extend(data)
                    break

            return all_results

        except APIError as e:
            self._handle_error("list", e)
            return []

    def get(self, resource_id: str) -> dict[str, Any]:
        """Get a single resource by ID.

        Args:
            resource_id: Resource identifier

        Returns:
            Resource dictionary
        """
        try:
            response = self.client.get(f"{self.api_path}/{resource_id}")
            return response.json()
        except APIError as e:
            self._handle_error("get", e)
            return {}

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new resource.

        Args:
            data: Resource data

        Returns:
            Created resource dictionary
        """
        try:
            response = self.client.post(self.api_path, json=data)
            return response.json()
        except APIError as e:
            self._handle_error("create", e)
            return {}

    def update(self, resource_id: str, data: dict[str, Any]) -> dict[str, Any]:
        """Update an existing resource.

        Args:
            resource_id: Resource identifier
            data: Updated resource data

        Returns:
            Updated resource dictionary
        """
        try:
            response = self.client.put(f"{self.api_path}/{resource_id}", json=data)
            return response.json()
        except APIError as e:
            self._handle_error("update", e)
            return {}

    def delete(self, resource_id: str) -> bool:
        """Delete a resource.

        Args:
            resource_id: Resource identifier

        Returns:
            True if deleted successfully
        """
        try:
            self.client.delete(f"{self.api_path}/{resource_id}")
            return True
        except APIError as e:
            self._handle_error("delete", e)
            return False

    def exists(self, resource_id: str) -> bool:
        """Check if a resource exists.

        Args:
            resource_id: Resource identifier

        Returns:
            True if resource exists
        """
        try:
            self.client.get(f"{self.api_path}/{resource_id}")
            return True
        except APIError:
            return False
