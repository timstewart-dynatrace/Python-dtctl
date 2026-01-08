"""EdgeConnect resource handler.

Manages Dynatrace EdgeConnect configurations.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from dtctl.client import Client, APIError
from dtctl.resources.base import CRUDHandler


class EdgeConnect(BaseModel):
    """EdgeConnect resource model."""

    id: str = ""
    name: str = ""
    hostname_patterns: list[str] = Field(default_factory=list, alias="hostnamePatterns")
    oauth_client_id: str = Field(default="", alias="oauthClientId")

    model_config = {"populate_by_name": True}


class EdgeConnectHandler(CRUDHandler[EdgeConnect]):
    """Handler for EdgeConnect operations."""

    @property
    def resource_name(self) -> str:
        return "edgeconnect"

    @property
    def api_path(self) -> str:
        return "/api/v2/edgeConnect/configurations"

    @property
    def list_key(self) -> str:
        return "edgeConnectConfigurations"

    def list(self, **params: Any) -> list[dict[str, Any]]:
        """List EdgeConnect configurations.

        Returns:
            List of configuration dictionaries
        """
        response = self.client.get(self.api_path, params=params)
        data = response.json()
        return data.get(self.list_key, [])

    def get(self, config_id: str) -> dict[str, Any]:
        """Get an EdgeConnect configuration by ID.

        Args:
            config_id: Configuration ID

        Returns:
            Configuration dictionary
        """
        response = self.client.get(f"{self.api_path}/{config_id}")
        return response.json()

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create an EdgeConnect configuration.

        Args:
            data: Configuration data

        Returns:
            Created configuration
        """
        response = self.client.post(self.api_path, json=data)
        return response.json()

    def update(self, config_id: str, data: dict[str, Any]) -> dict[str, Any]:
        """Update an EdgeConnect configuration.

        Args:
            config_id: Configuration ID
            data: Updated configuration

        Returns:
            Updated configuration
        """
        response = self.client.put(f"{self.api_path}/{config_id}", json=data)
        return response.json()

    def delete(self, config_id: str) -> bool:
        """Delete an EdgeConnect configuration.

        Args:
            config_id: Configuration ID

        Returns:
            True if deleted successfully
        """
        try:
            self.client.delete(f"{self.api_path}/{config_id}")
            return True
        except APIError:
            return False
