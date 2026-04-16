"""App resource handler.

Manages Dynatrace App Engine applications.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from dtctl.client import APIError
from dtctl.resources.base import ResourceHandler


class App(BaseModel):
    """App resource model."""

    id: str = ""
    name: str = ""
    version: str = ""
    status: str = ""
    description: str = ""

    model_config = {"populate_by_name": True}


class AppHandler(ResourceHandler[App]):
    """Handler for app operations."""

    @property
    def resource_name(self) -> str:
        return "app"

    @property
    def api_path(self) -> str:
        return "/platform/app-engine/registry/v1/apps"

    def list(self, **params: Any) -> list[dict[str, Any]]:
        """List installed apps.

        Returns:
            List of app dictionaries
        """
        response = self.client.get(self.api_path, params=params)
        data = response.json()
        return data.get("apps", [])

    def get(self, app_id: str) -> dict[str, Any]:
        """Get an app by ID.

        Args:
            app_id: App ID

        Returns:
            App dictionary
        """
        response = self.client.get(f"{self.api_path}/{app_id}")
        return response.json()

    def install(self, app_id: str, version: str | None = None) -> dict[str, Any]:
        """Install an app.

        Args:
            app_id: App ID
            version: Optional specific version

        Returns:
            Installation result
        """
        data: dict[str, Any] = {"appId": app_id}
        if version:
            data["version"] = version

        response = self.client.post(f"{self.api_path}/install", json=data)
        return response.json()

    def uninstall(self, app_id: str) -> bool:
        """Uninstall an app.

        Args:
            app_id: App ID

        Returns:
            True if uninstalled successfully
        """
        try:
            self.client.delete(f"{self.api_path}/{app_id}")
            return True
        except APIError:
            return False

    def list_sdk_versions(self) -> list[dict[str, Any]]:
        """List available SDK versions.

        Returns:
            List of SDK version dictionaries
        """
        response = self.client.get("/platform/app-engine/sdk/v1/versions")
        data = response.json()
        return data.get("versions", [])
