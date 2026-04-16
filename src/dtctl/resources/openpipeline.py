"""OpenPipeline resource handler.

Manages Dynatrace OpenPipeline configurations.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from dtctl.resources.base import ResourceHandler


class OpenPipeline(BaseModel):
    """OpenPipeline resource model."""

    id: str = ""
    name: str = ""
    enabled: bool = True

    model_config = {"populate_by_name": True}


class OpenPipelineHandler(ResourceHandler[OpenPipeline]):
    """Handler for OpenPipeline operations."""

    @property
    def resource_name(self) -> str:
        return "openpipeline"

    @property
    def api_path(self) -> str:
        return "/platform/openpipeline/v1/configurations"

    def list(self, **params: Any) -> list[dict[str, Any]]:
        """List pipeline configurations.

        Returns:
            List of pipeline dictionaries
        """
        response = self.client.get(self.api_path, params=params)
        data = response.json()
        return data.get("pipelines", [])

    def get(self, pipeline_id: str) -> dict[str, Any]:
        """Get a pipeline configuration by ID.

        Args:
            pipeline_id: Pipeline ID

        Returns:
            Pipeline dictionary
        """
        response = self.client.get(f"{self.api_path}/{pipeline_id}")
        return response.json()

    def update(self, pipeline_id: str, data: dict[str, Any]) -> dict[str, Any]:
        """Update a pipeline configuration.

        Args:
            pipeline_id: Pipeline ID
            data: Updated configuration

        Returns:
            Updated pipeline
        """
        response = self.client.put(f"{self.api_path}/{pipeline_id}", json=data)
        return response.json()
