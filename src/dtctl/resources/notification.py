"""Notification resource handler.

Manages Dynatrace event notifications.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from dtctl.client import Client, APIError
from dtctl.resources.base import CRUDHandler


class Notification(BaseModel):
    """Notification resource model."""

    id: str = ""
    name: str = ""
    enabled: bool = True
    notification_type: str = Field(default="", alias="type")
    description: str = ""

    model_config = {"populate_by_name": True}


class NotificationHandler(CRUDHandler[Notification]):
    """Handler for notification operations."""

    @property
    def resource_name(self) -> str:
        return "notification"

    @property
    def api_path(self) -> str:
        return "/api/v2/notifications"

    @property
    def list_key(self) -> str:
        return "notifications"

    def list(
        self,
        enabled_only: bool = False,
        notification_type: str | None = None,
        **params: Any,
    ) -> list[dict[str, Any]]:
        """List notifications with optional filtering.

        Args:
            enabled_only: Only return enabled notifications
            notification_type: Filter by type
            **params: Additional query parameters

        Returns:
            List of notification dictionaries
        """
        query_params: dict[str, Any] = {}
        if notification_type:
            query_params["type"] = notification_type
        query_params.update(params)

        response = self.client.get(self.api_path, params=query_params)
        data = response.json()
        return data.get(self.list_key, [])

    def get(self, notification_id: str) -> dict[str, Any]:
        """Get a notification by ID.

        Args:
            notification_id: Notification ID

        Returns:
            Notification dictionary
        """
        response = self.client.get(f"{self.api_path}/{notification_id}")
        return response.json()

    def delete(self, notification_id: str) -> bool:
        """Delete a notification.

        Args:
            notification_id: Notification ID

        Returns:
            True if deleted successfully
        """
        try:
            self.client.delete(f"{self.api_path}/{notification_id}")
            return True
        except APIError:
            return False
