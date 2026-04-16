"""Analyzer resource handler.

Manages Davis AI analyzers.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from dtctl.resources.base import ResourceHandler


class Analyzer(BaseModel):
    """Analyzer resource model."""

    name: str = ""
    description: str = ""
    version: str = ""

    model_config = {"populate_by_name": True}


class AnalyzerHandler(ResourceHandler[Analyzer]):
    """Handler for analyzer operations."""

    @property
    def resource_name(self) -> str:
        return "analyzer"

    @property
    def api_path(self) -> str:
        return "/platform/davis/analyzer/v1/analyzers"

    def list(self, **params: Any) -> list[dict[str, Any]]:
        """List analyzers.

        Returns:
            List of analyzer dictionaries
        """
        response = self.client.get(self.api_path, params=params)
        data = response.json()
        return data.get("analyzers", [])

    def get(self, analyzer_name: str) -> dict[str, Any]:
        """Get an analyzer by name.

        Args:
            analyzer_name: Analyzer name

        Returns:
            Analyzer dictionary
        """
        response = self.client.get(f"{self.api_path}/{analyzer_name}")
        return response.json()

    def execute(
        self,
        analyzer_name: str,
        input_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute an analyzer.

        Args:
            analyzer_name: Analyzer name
            input_data: Input data for the analyzer

        Returns:
            Analyzer result
        """
        response = self.client.post(
            f"{self.api_path}/{analyzer_name}/execute",
            json=input_data,
        )
        return response.json()
