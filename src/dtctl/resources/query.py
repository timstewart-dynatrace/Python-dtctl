"""DQL Query execution handler.

Executes Dynatrace Query Language (DQL) queries against Grail storage.
"""

from __future__ import annotations

import time
from typing import Any

from dtctl.client import Client


class QueryHandler:
    """Handler for DQL query execution."""

    def __init__(self, client: Client):
        self.client = client
        self.base_path = "/platform/storage/query/v1"

    def execute(
        self,
        query: str,
        timeout_ms: int = 60000,
        max_result_records: int = 1000,
    ) -> dict[str, Any]:
        """Execute a DQL query.

        Args:
            query: DQL query string
            timeout_ms: Query timeout in milliseconds
            max_result_records: Maximum number of records to return

        Returns:
            Query result dictionary
        """
        data = {
            "query": query,
            "defaultTimeframeStart": "now-2h",
            "defaultTimeframeEnd": "now",
            "maxResultRecords": max_result_records,
        }

        response = self.client.post(
            f"{self.base_path}/query:execute",
            json=data,
            timeout=timeout_ms / 1000 + 10,  # Add buffer to HTTP timeout
        )
        result = response.json()

        # Check if query is still running
        state = result.get("state", "")
        if state == "RUNNING":
            request_token = result.get("requestToken")
            if request_token:
                return self._poll_for_result(request_token, timeout_ms)

        return result

    def _poll_for_result(
        self,
        request_token: str,
        timeout_ms: int = 60000,
    ) -> dict[str, Any]:
        """Poll for query result.

        Args:
            request_token: Token from initial query execution
            timeout_ms: Maximum time to wait

        Returns:
            Query result dictionary
        """
        start_time = time.time()
        poll_interval = 1.0

        while (time.time() - start_time) * 1000 < timeout_ms:
            response = self.client.get(
                f"{self.base_path}/query:poll",
                params={"request-token": request_token},
            )
            result = response.json()
            state = result.get("state", "")

            if state in ("SUCCEEDED", "FAILED", "CANCELLED"):
                return result

            time.sleep(poll_interval)

        raise TimeoutError(f"Query did not complete within {timeout_ms}ms")

    def execute_from_file(
        self,
        file_path: str,
        variables: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Execute a DQL query from a file.

        Args:
            file_path: Path to file containing DQL query
            variables: Template variables for substitution
            **kwargs: Additional arguments passed to execute()

        Returns:
            Query result dictionary
        """
        from dtctl.utils.template import render_template

        with open(file_path) as f:
            query = f.read()

        if variables:
            query = render_template(query, variables)

        return self.execute(query, **kwargs)
