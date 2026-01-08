"""IAM (Identity and Access Management) resource handler.

Manages Dynatrace users and groups (read-only).
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from dtctl.client import Client
from dtctl.resources.base import ResourceHandler


class User(BaseModel):
    """User resource model."""

    uid: str = ""
    email: str = ""
    name: str = ""
    groups: list[str] = Field(default_factory=list)

    model_config = {"populate_by_name": True}


class Group(BaseModel):
    """Group resource model."""

    uuid: str = ""
    name: str = ""
    description: str = ""
    owner: str = ""

    model_config = {"populate_by_name": True}


class IAMHandler(ResourceHandler[User]):
    """Handler for IAM operations (users and groups)."""

    @property
    def resource_name(self) -> str:
        return "user"

    @property
    def api_path(self) -> str:
        return "/iam/v1"

    def list_users(self, **params: Any) -> list[dict[str, Any]]:
        """List users.

        Returns:
            List of user dictionaries
        """
        response = self.client.get(f"{self.api_path}/accounts/users", params=params)
        data = response.json()
        return data.get("items", [])

    def get_user(self, user_id: str) -> dict[str, Any]:
        """Get a user by ID.

        Args:
            user_id: User ID (uid or email)

        Returns:
            User dictionary
        """
        response = self.client.get(f"{self.api_path}/accounts/users/{user_id}")
        return response.json()

    def list_groups(self, **params: Any) -> list[dict[str, Any]]:
        """List groups.

        Returns:
            List of group dictionaries
        """
        response = self.client.get(f"{self.api_path}/accounts/groups", params=params)
        data = response.json()
        return data.get("items", [])

    def get_group(self, group_id: str) -> dict[str, Any]:
        """Get a group by ID.

        Args:
            group_id: Group UUID

        Returns:
            Group dictionary
        """
        response = self.client.get(f"{self.api_path}/accounts/groups/{group_id}")
        return response.json()

    def get_group_members(self, group_id: str) -> list[dict[str, Any]]:
        """Get members of a group.

        Args:
            group_id: Group UUID

        Returns:
            List of user dictionaries
        """
        response = self.client.get(
            f"{self.api_path}/accounts/groups/{group_id}/users"
        )
        data = response.json()
        return data.get("items", [])
