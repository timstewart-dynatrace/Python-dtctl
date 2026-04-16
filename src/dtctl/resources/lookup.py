"""Lookup table resource handler.

Manages Dynatrace lookup tables for data enrichment and mapping.
"""

from __future__ import annotations

import csv
import io
from typing import Any

from pydantic import BaseModel, Field

from dtctl.client import APIError
from dtctl.resources.base import CRUDHandler


class LookupTable(BaseModel):
    """Lookup table resource model."""

    id: str = ""
    name: str = ""
    description: str = ""
    owner: str = ""
    columns: list[dict[str, Any]] = Field(default_factory=list)
    row_count: int = Field(default=0, alias="rowCount")

    model_config = {"populate_by_name": True}


class LookupTableHandler(CRUDHandler[LookupTable]):
    """Handler for lookup table operations."""

    @property
    def resource_name(self) -> str:
        return "lookup-table"

    @property
    def api_path(self) -> str:
        return "/platform/storage/lookups/v1/tables"

    @property
    def list_key(self) -> str:
        return "tables"

    def list(self, **params: Any) -> list[dict[str, Any]]:
        """List lookup tables with pagination.

        Returns:
            List of lookup table dictionaries
        """
        try:
            all_tables: list[dict[str, Any]] = []
            next_page_key: str | None = None

            while True:
                if next_page_key:
                    request_params = {**params, "nextPageKey": next_page_key}
                else:
                    request_params = params

                response = self.client.get(self.api_path, params=request_params)
                data = response.json()

                tables = data.get(self.list_key, [])
                all_tables.extend(tables)

                next_page_key = data.get("nextPageKey")
                if not next_page_key:
                    break

            return all_tables
        except APIError as e:
            self._handle_error("list", e)
            return []

    def get(self, table_id: str) -> dict[str, Any]:
        """Get a lookup table by ID.

        Args:
            table_id: Table ID

        Returns:
            Lookup table dictionary
        """
        try:
            response = self.client.get(f"{self.api_path}/{table_id}")
            return response.json()
        except APIError as e:
            self._handle_error("get", e)
            return {}

    def get_data(self, table_id: str, limit: int = 1000) -> list[dict[str, Any]]:
        """Get lookup table data (rows).

        Args:
            table_id: Table ID
            limit: Maximum number of rows to return

        Returns:
            List of row dictionaries
        """
        try:
            response = self.client.get(
                f"{self.api_path}/{table_id}/data",
                params={"limit": limit},
            )
            data = response.json()
            return data.get("rows", [])
        except APIError as e:
            self._handle_error("get data", e)
            return []

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new lookup table.

        Args:
            data: Table definition including name, columns, etc.

        Returns:
            Created table dictionary
        """
        try:
            response = self.client.post(self.api_path, json=data)
            return response.json()
        except APIError as e:
            self._handle_error("create", e)
            return {}

    def create_from_csv(
        self,
        name: str,
        csv_content: str,
        description: str = "",
        delimiter: str | None = None,
        has_header: bool = True,
    ) -> dict[str, Any]:
        """Create a lookup table from CSV content.

        Args:
            name: Table name
            csv_content: CSV content as string
            description: Optional description
            delimiter: CSV delimiter (auto-detected if not provided)
            has_header: Whether CSV has a header row

        Returns:
            Created table dictionary
        """
        # Auto-detect delimiter if not provided
        if delimiter is None:
            delimiter = self._detect_delimiter(csv_content)

        # Parse CSV
        reader = csv.reader(io.StringIO(csv_content), delimiter=delimiter)
        rows = list(reader)

        if not rows:
            raise ValueError("CSV content is empty")

        # Extract columns from header or generate generic names
        if has_header:
            header = rows[0]
            data_rows = rows[1:]
        else:
            # Generate column names
            num_cols = len(rows[0]) if rows else 0
            header = [f"column{i + 1}" for i in range(num_cols)]
            data_rows = rows

        # Build column definitions
        columns = []
        for col_name in header:
            columns.append(
                {
                    "name": col_name.strip(),
                    "type": "string",  # Default to string, could be enhanced
                }
            )

        # Build table data
        table_data = {
            "name": name,
            "description": description,
            "columns": columns,
        }

        # Create the table
        table = self.create(table_data)

        if not table or "id" not in table:
            raise RuntimeError("Failed to create lookup table")

        # Upload the data
        table_id = table["id"]
        self._upload_data(table_id, header, data_rows)

        return table

    def _detect_delimiter(self, csv_content: str) -> str:
        """Auto-detect CSV delimiter.

        Args:
            csv_content: CSV content as string

        Returns:
            Detected delimiter character
        """
        # Try common delimiters
        delimiters = [",", ";", "\t", "|"]
        first_line = csv_content.split("\n")[0] if csv_content else ""

        best_delimiter = ","
        max_count = 0

        for d in delimiters:
            count = first_line.count(d)
            if count > max_count:
                max_count = count
                best_delimiter = d

        return best_delimiter

    def _upload_data(
        self,
        table_id: str,
        columns: list[str],
        rows: list[list[str]],
    ) -> None:
        """Upload data to a lookup table.

        Args:
            table_id: Table ID
            columns: Column names
            rows: List of row data
        """
        # Convert rows to records
        records = []
        for row in rows:
            record = {}
            for i, col in enumerate(columns):
                if i < len(row):
                    record[col.strip()] = row[i]
            records.append(record)

        # Upload in batches
        batch_size = 1000
        for i in range(0, len(records), batch_size):
            batch = records[i : i + batch_size]
            try:
                self.client.post(
                    f"{self.api_path}/{table_id}/data",
                    json={"rows": batch},
                )
            except APIError as e:
                self._handle_error("upload data", e)

    def update_data(
        self,
        table_id: str,
        rows: list[dict[str, Any]],
        mode: str = "append",
    ) -> bool:
        """Update lookup table data.

        Args:
            table_id: Table ID
            rows: List of row dictionaries
            mode: Update mode - 'append' or 'replace'

        Returns:
            True if successful
        """
        try:
            if mode == "replace":
                # Clear existing data first
                self.client.delete(f"{self.api_path}/{table_id}/data")

            self.client.post(
                f"{self.api_path}/{table_id}/data",
                json={"rows": rows},
            )
            return True
        except APIError as e:
            self._handle_error("update data", e)
            return False

    def delete(self, table_id: str) -> bool:
        """Delete a lookup table.

        Args:
            table_id: Table ID

        Returns:
            True if deleted successfully
        """
        try:
            self.client.delete(f"{self.api_path}/{table_id}")
            return True
        except APIError as e:
            self._handle_error("delete", e)
            return False

    def clear_data(self, table_id: str) -> bool:
        """Clear all data from a lookup table.

        Args:
            table_id: Table ID

        Returns:
            True if cleared successfully
        """
        try:
            self.client.delete(f"{self.api_path}/{table_id}/data")
            return True
        except APIError as e:
            self._handle_error("clear data", e)
            return False
