"""Bucket resource handler.

Manages Dynatrace Grail storage buckets.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from dtctl.client import APIError
from dtctl.resources.base import CRUDHandler


class Bucket(BaseModel):
    """Bucket resource model."""

    bucket_name: str = Field(default="", alias="bucketName")
    table: str = ""
    status: str = ""
    retention_days: int = Field(default=35, alias="retentionDays")
    display_name: str = Field(default="", alias="displayName")

    model_config = {"populate_by_name": True}


class BucketHandler(CRUDHandler[Bucket]):
    """Handler for bucket operations."""

    @property
    def resource_name(self) -> str:
        return "bucket"

    @property
    def api_path(self) -> str:
        return "/platform/storage/management/v1/bucket-definitions"

    @property
    def list_key(self) -> str:
        return "buckets"

    @property
    def id_field(self) -> str:
        return "bucketName"

    def list(self, **params: Any) -> list[dict[str, Any]]:
        """List buckets.

        Returns:
            List of bucket dictionaries
        """
        response = self.client.get(self.api_path, params=params)
        data = response.json()
        return data.get(self.list_key, [])

    def get(self, bucket_name: str) -> dict[str, Any]:
        """Get a bucket by name.

        Args:
            bucket_name: Bucket name

        Returns:
            Bucket dictionary
        """
        response = self.client.get(f"{self.api_path}/{bucket_name}")
        return response.json()

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new bucket.

        Args:
            data: Bucket definition

        Returns:
            Created bucket
        """
        response = self.client.post(self.api_path, json=data)
        return response.json()

    def update(self, bucket_name: str, data: dict[str, Any]) -> dict[str, Any]:
        """Update a bucket.

        Args:
            bucket_name: Bucket name
            data: Updated bucket definition

        Returns:
            Updated bucket
        """
        response = self.client.put(f"{self.api_path}/{bucket_name}", json=data)
        return response.json()

    def delete(self, bucket_name: str) -> bool:
        """Delete a bucket.

        Args:
            bucket_name: Bucket name

        Returns:
            True if deleted successfully
        """
        try:
            self.client.delete(f"{self.api_path}/{bucket_name}")
            return True
        except APIError:
            return False
