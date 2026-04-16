"""Limits resource handler.

Retrieves account limits, quotas, and usage information from Dynatrace.
"""

from __future__ import annotations

from typing import Any

from dtctl.client import APIError, Client


class LimitsHandler:
    """Handler for retrieving account limits and quotas."""

    def __init__(self, client: Client):
        self.client = client

    def get_limits(self) -> list[dict[str, Any]]:
        """Get account limits and quotas.

        Returns a list of limit information including:
        - API rate limits
        - Resource quotas (workflows, dashboards, etc.)
        - DEM units
        - Host units

        Returns:
            List of limit dictionaries with name, current, max, and unit fields
        """
        limits = []

        # Try to get various limits from different endpoints
        # These endpoints may vary based on Dynatrace version/tier

        # Get automation/workflow limits
        try:
            response = self.client.get("/platform/automation/v1/workflows")
            data = response.json()
            total_count = data.get("totalCount", len(data.get("results", [])))
            limits.append(
                {
                    "name": "Workflows",
                    "current": total_count,
                    "max": None,  # API doesn't expose max
                    "unit": "workflows",
                    "percentage": None,
                }
            )
        except APIError:
            pass

        # Get document limits (dashboards/notebooks)
        try:
            response = self.client.get("/platform/document/v1/documents")
            data = response.json()
            docs = data.get("documents", [])
            dashboards = len([d for d in docs if d.get("type") == "dashboard"])
            notebooks = len([d for d in docs if d.get("type") == "notebook"])
            limits.append(
                {
                    "name": "Dashboards",
                    "current": dashboards,
                    "max": None,
                    "unit": "dashboards",
                    "percentage": None,
                }
            )
            limits.append(
                {
                    "name": "Notebooks",
                    "current": notebooks,
                    "max": None,
                    "unit": "notebooks",
                    "percentage": None,
                }
            )
        except APIError:
            pass

        # Get SLO limits
        try:
            response = self.client.get("/platform/classic/environment-api/v2/slo")
            data = response.json()
            total_count = data.get("totalCount", len(data.get("slo", [])))
            limits.append(
                {
                    "name": "SLOs",
                    "current": total_count,
                    "max": None,
                    "unit": "slos",
                    "percentage": None,
                }
            )
        except APIError:
            pass

        # Get bucket information
        try:
            response = self.client.get("/platform/storage/management/v1/bucket-definitions")
            data = response.json()
            buckets = data.get("buckets", [])
            limits.append(
                {
                    "name": "Grail Buckets",
                    "current": len(buckets),
                    "max": None,
                    "unit": "buckets",
                    "percentage": None,
                }
            )
        except APIError:
            pass

        # Get app limits
        try:
            response = self.client.get("/platform/classic/environment-api/v2/hub/apps/installed")
            data = response.json()
            apps = data.get("apps", [])
            limits.append(
                {
                    "name": "Installed Apps",
                    "current": len(apps),
                    "max": None,
                    "unit": "apps",
                    "percentage": None,
                }
            )
        except APIError:
            pass

        # Try to get environment limits/quotas if available
        try:
            response = self.client.get("/platform/classic/environment-api/v2/limits")
            data = response.json()
            for limit in data.get("limits", []):
                limit_max = limit.get("limit")
                limit_current = limit.get("current", 0)
                percentage = None
                if limit_max and limit_max > 0:
                    percentage = (limit_current / limit_max) * 100
                limits.append(
                    {
                        "name": limit.get("name", limit.get("type", "Unknown")),
                        "current": limit_current,
                        "max": limit_max,
                        "unit": limit.get("unit", ""),
                        "percentage": percentage,
                    }
                )
        except APIError:
            pass

        # Try to get consumption/usage info
        try:
            response = self.client.get("/platform/classic/environment-api/v2/consumption/overview")
            data = response.json()
            for item in data.get("items", []):
                limits.append(
                    {
                        "name": item.get("name", "Unknown"),
                        "current": item.get("consumed", 0),
                        "max": item.get("quota"),
                        "unit": item.get("unit", ""),
                        "percentage": item.get("percentageConsumed"),
                    }
                )
        except APIError:
            pass

        return limits

    def get_rate_limits(self) -> dict[str, Any]:
        """Get API rate limit information.

        Returns rate limit headers from a sample API call.

        Returns:
            Dictionary with rate limit information
        """
        try:
            response = self.client.get("/platform/automation/v1/workflows", params={"limit": 1})
            headers = response.headers

            return {
                "limit": headers.get("X-RateLimit-Limit"),
                "remaining": headers.get("X-RateLimit-Remaining"),
                "reset": headers.get("X-RateLimit-Reset"),
            }
        except APIError:
            return {}
