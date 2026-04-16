"""Settings resource handler.

Manages Dynatrace settings objects and schemas.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from dtctl.client import APIError, Client
from dtctl.resources.base import ResourceHandler


class SettingsObject(BaseModel):
    """Settings object model."""

    object_id: str = Field(default="", alias="objectId")
    schema_id: str = Field(default="", alias="schemaId")
    scope: str = ""
    value: dict[str, Any] = Field(default_factory=dict)
    version: str = ""

    model_config = {"populate_by_name": True}


class SettingsSchema(BaseModel):
    """Settings schema model."""

    schema_id: str = Field(alias="schemaId")
    display_name: str = Field(default="", alias="displayName")
    description: str = ""

    model_config = {"populate_by_name": True}


class SettingsHandler(ResourceHandler[SettingsObject]):
    """Handler for settings operations."""

    def __init__(self, client: Client):
        super().__init__(client)
        self._schemas_path = "/api/v2/settings/schemas"
        self._objects_path = "/api/v2/settings/objects"

    @property
    def resource_name(self) -> str:
        return "settings"

    @property
    def api_path(self) -> str:
        return self._objects_path

    def list_schemas(self) -> list[dict[str, Any]]:
        """List all settings schemas with pagination.

        Returns:
            List of schema dictionaries
        """
        all_schemas: list[dict[str, Any]] = []
        next_page_key: str | None = None

        while True:
            params = {"nextPageKey": next_page_key} if next_page_key else {}
            response = self.client.get(self._schemas_path, params=params)
            data = response.json()

            items = data.get("items", [])
            all_schemas.extend(items)

            next_page_key = data.get("nextPageKey")
            if not next_page_key:
                break

        return all_schemas

    def get_schema(self, schema_id: str) -> dict[str, Any]:
        """Get a settings schema definition.

        Args:
            schema_id: Schema ID (e.g., builtin:alerting.profile)

        Returns:
            Schema definition
        """
        response = self.client.get(f"{self._schemas_path}/{schema_id}")
        return response.json()

    def list_objects(
        self,
        schema_id: str | None = None,
        scope: str | None = None,
        **params: Any,
    ) -> list[dict[str, Any]]:
        """List settings objects with pagination.

        Args:
            schema_id: Filter by schema ID
            scope: Filter by scope (e.g., environment, HOST-xxx)
            **params: Additional query parameters

        Returns:
            List of settings objects
        """
        query_params: dict[str, Any] = {}
        if schema_id:
            query_params["schemaIds"] = schema_id
        if scope:
            query_params["scopes"] = scope
        query_params.update(params)

        all_objects: list[dict[str, Any]] = []
        next_page_key: str | None = None

        while True:
            if next_page_key:
                request_params = {**query_params, "nextPageKey": next_page_key}
            else:
                request_params = query_params

            response = self.client.get(self._objects_path, params=request_params)
            data = response.json()

            items = data.get("items", [])
            all_objects.extend(items)

            next_page_key = data.get("nextPageKey")
            if not next_page_key:
                break

        return all_objects

    def get_object(self, object_id: str) -> dict[str, Any]:
        """Get a settings object by ID.

        Args:
            object_id: Settings object ID

        Returns:
            Settings object dictionary
        """
        response = self.client.get(f"{self._objects_path}/{object_id}")
        return response.json()

    def create_object(
        self,
        schema_id: str,
        scope: str,
        value: dict[str, Any],
    ) -> dict[str, Any]:
        """Create a settings object.

        Args:
            schema_id: Schema ID
            scope: Scope (e.g., environment)
            value: Settings value

        Returns:
            Created settings object
        """
        data = [
            {
                "schemaId": schema_id,
                "scope": scope,
                "value": value,
            }
        ]

        response = self.client.post(self._objects_path, json=data)
        result = response.json()

        # API returns array of results
        if isinstance(result, list) and len(result) > 0:
            return result[0]
        return result

    def update_object(
        self,
        object_id: str,
        value: dict[str, Any],
    ) -> dict[str, Any]:
        """Update a settings object.

        Args:
            object_id: Settings object ID
            value: Updated value

        Returns:
            Updated settings object
        """
        response = self.client.put(
            f"{self._objects_path}/{object_id}",
            json={"value": value},
        )
        return response.json()

    def delete_object(self, object_id: str) -> bool:
        """Delete a settings object.

        Args:
            object_id: Settings object ID

        Returns:
            True if deleted successfully
        """
        try:
            self.client.delete(f"{self._objects_path}/{object_id}")
            return True
        except APIError:
            return False
