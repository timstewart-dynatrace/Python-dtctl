"""SLO (Service Level Objective) resource handler.

Manages Dynatrace SLO definitions and evaluations.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from dtctl.client import Client, APIError
from dtctl.resources.base import CRUDHandler


class SLO(BaseModel):
    """SLO resource model."""

    id: str = ""
    name: str = ""
    description: str = ""
    status: str = ""
    target: float = 0.0
    warning: float = 0.0
    evaluated_percentage: float = Field(default=0.0, alias="evaluatedPercentage")
    error_budget: float = Field(default=0.0, alias="errorBudget")
    enabled: bool = True

    model_config = {"populate_by_name": True}


class SLOHandler(CRUDHandler[SLO]):
    """Handler for SLO operations."""

    @property
    def resource_name(self) -> str:
        return "SLO"

    @property
    def api_path(self) -> str:
        return "/api/v2/slo"

    @property
    def list_key(self) -> str:
        return "slo"

    def list(
        self,
        enabled_only: bool = False,
        name_filter: str | None = None,
        **params: Any,
    ) -> list[dict[str, Any]]:
        """List SLOs with optional filtering and pagination.

        Args:
            enabled_only: Only return enabled SLOs
            name_filter: Filter by name
            **params: Additional query parameters

        Returns:
            List of SLO dictionaries
        """
        query_params: dict[str, Any] = {}
        if enabled_only:
            query_params["enabledSlos"] = "true"
        if name_filter:
            query_params["sloSelector"] = f'name("{name_filter}")'
        query_params.update(params)

        all_slos: list[dict[str, Any]] = []
        next_page_key: str | None = None

        while True:
            if next_page_key:
                request_params = {**query_params, "nextPageKey": next_page_key}
            else:
                request_params = query_params

            response = self.client.get(self.api_path, params=request_params)
            data = response.json()

            slos = data.get(self.list_key, [])
            all_slos.extend(slos)

            next_page_key = data.get("nextPageKey")
            if not next_page_key:
                break

        return all_slos

    def get(self, slo_id: str) -> dict[str, Any]:
        """Get an SLO by ID.

        Args:
            slo_id: SLO ID

        Returns:
            SLO dictionary
        """
        response = self.client.get(f"{self.api_path}/{slo_id}")
        return response.json()

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new SLO.

        Args:
            data: SLO definition

        Returns:
            Created SLO
        """
        response = self.client.post(self.api_path, json=data)
        return response.json()

    def update(self, slo_id: str, data: dict[str, Any]) -> dict[str, Any]:
        """Update an SLO.

        Args:
            slo_id: SLO ID
            data: Updated SLO definition

        Returns:
            Updated SLO
        """
        response = self.client.put(f"{self.api_path}/{slo_id}", json=data)
        return response.json()

    def delete(self, slo_id: str) -> bool:
        """Delete an SLO.

        Args:
            slo_id: SLO ID

        Returns:
            True if deleted successfully
        """
        try:
            self.client.delete(f"{self.api_path}/{slo_id}")
            return True
        except APIError:
            return False
