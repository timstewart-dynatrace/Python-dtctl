"""Output formatting for dtctl.

Supports multiple output formats:
- table: ASCII tables (default)
- wide: Extended table with more columns
- json: JSON output
- yaml: YAML output
- csv: CSV output
- plain: Machine-readable output (no colors/formatting)
"""

from __future__ import annotations

import csv
import io
import json
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Sequence

import yaml
from rich.console import Console
from rich.table import Table


class OutputFormat(str, Enum):
    """Supported output formats."""

    TABLE = "table"
    WIDE = "wide"
    JSON = "json"
    YAML = "yaml"
    CSV = "csv"
    PLAIN = "plain"


class Formatter(ABC):
    """Base class for output formatters."""

    @abstractmethod
    def format(self, data: Any, columns: list[Column] | None = None) -> str:
        """Format data for output."""
        pass


class Column:
    """Column definition for table output."""

    def __init__(
        self,
        key: str,
        header: str,
        wide_only: bool = False,
        formatter: Any | None = None,
    ):
        self.key = key
        self.header = header
        self.wide_only = wide_only
        self.formatter = formatter or (lambda x: str(x) if x is not None else "")

    def get_value(self, row: dict[str, Any]) -> str:
        """Extract and format value from a row."""
        value = row.get(self.key)
        return self.formatter(value)


class TableFormatter(Formatter):
    """Format data as ASCII table using Rich."""

    def __init__(self, wide: bool = False, plain: bool = False):
        self.wide = wide
        self.plain = plain
        self.console = Console(force_terminal=not plain, no_color=plain)

    def format(self, data: Any, columns: list[Column] | None = None) -> str:
        """Format data as a table."""
        if not data:
            return "No resources found."

        # Handle single item
        if isinstance(data, dict):
            data = [data]

        if not columns:
            # Auto-generate columns from first row
            if data:
                columns = [Column(k, k.upper()) for k in data[0].keys()]
            else:
                return "No resources found."

        # Filter columns based on wide mode
        visible_columns = [c for c in columns if not c.wide_only or self.wide]

        table = Table(show_header=True, header_style="bold")

        for col in visible_columns:
            table.add_column(col.header)

        for row in data:
            values = [col.get_value(row) for col in visible_columns]
            table.add_row(*values)

        # Capture table output as string
        with io.StringIO() as buf:
            console = Console(file=buf, force_terminal=not self.plain, no_color=self.plain)
            console.print(table)
            return buf.getvalue()


class JSONFormatter(Formatter):
    """Format data as JSON."""

    def __init__(self, indent: int = 2):
        self.indent = indent

    def format(self, data: Any, columns: list[Column] | None = None) -> str:
        """Format data as indented JSON."""
        return json.dumps(data, indent=self.indent, default=str)


class YAMLFormatter(Formatter):
    """Format data as YAML."""

    def format(self, data: Any, columns: list[Column] | None = None) -> str:
        """Format data as YAML."""
        return yaml.dump(data, default_flow_style=False, sort_keys=False)


class CSVFormatter(Formatter):
    """Format data as CSV."""

    def format(self, data: Any, columns: list[Column] | None = None) -> str:
        """Format data as CSV."""
        if not data:
            return ""

        if isinstance(data, dict):
            data = [data]

        if not columns and data:
            columns = [Column(k, k) for k in data[0].keys()]

        output = io.StringIO()
        if columns:
            writer = csv.writer(output)
            writer.writerow([c.header for c in columns])
            for row in data:
                writer.writerow([c.get_value(row) for c in columns])

        return output.getvalue()


class PlainFormatter(Formatter):
    """Format data as plain text (JSON without colors)."""

    def format(self, data: Any, columns: list[Column] | None = None) -> str:
        """Format data as plain JSON for machine consumption."""
        return json.dumps(data, default=str)


class Printer:
    """Unified printer that handles all output formats."""

    def __init__(
        self,
        format: OutputFormat = OutputFormat.TABLE,
        plain: bool = False,
    ):
        self.format = format
        self.plain = plain

        # Override format if plain mode is enabled
        if plain and format == OutputFormat.TABLE:
            self.format = OutputFormat.JSON

        self._formatters: dict[OutputFormat, Formatter] = {
            OutputFormat.TABLE: TableFormatter(wide=False, plain=plain),
            OutputFormat.WIDE: TableFormatter(wide=True, plain=plain),
            OutputFormat.JSON: JSONFormatter(),
            OutputFormat.YAML: YAMLFormatter(),
            OutputFormat.CSV: CSVFormatter(),
            OutputFormat.PLAIN: PlainFormatter(),
        }

    def print(
        self,
        data: Any,
        columns: list[Column] | None = None,
    ) -> None:
        """Print data in the configured format."""
        formatter = self._formatters[self.format]
        output = formatter.format(data, columns)
        print(output)

    def format_str(
        self,
        data: Any,
        columns: list[Column] | None = None,
    ) -> str:
        """Format data and return as string."""
        formatter = self._formatters[self.format]
        return formatter.format(data, columns)


# Predefined column sets for common resources


def workflow_columns() -> list[Column]:
    """Column definitions for workflow resources."""
    return [
        Column("id", "ID"),
        Column("title", "TITLE"),
        Column("owner", "OWNER"),
        Column("isDeployed", "DEPLOYED", formatter=lambda x: "Yes" if x else "No"),
        Column("isPrivate", "PRIVATE", formatter=lambda x: "Yes" if x else "No"),
        Column("description", "DESCRIPTION", wide_only=True),
    ]


def execution_columns() -> list[Column]:
    """Column definitions for execution resources."""
    return [
        Column("id", "ID"),
        Column("workflow", "WORKFLOW"),
        Column("state", "STATE"),
        Column("startedAt", "STARTED"),
        Column("runtime", "RUNTIME"),
        Column("triggerType", "TRIGGER", wide_only=True),
    ]


def document_columns() -> list[Column]:
    """Column definitions for document resources (dashboards, notebooks)."""
    return [
        Column("id", "ID"),
        Column("name", "NAME"),
        Column("type", "TYPE"),
        Column("owner", "OWNER"),
        Column("isPrivate", "PRIVATE", formatter=lambda x: "Yes" if x else "No"),
        Column("version", "VERSION", wide_only=True),
    ]


def slo_columns() -> list[Column]:
    """Column definitions for SLO resources."""
    return [
        Column("id", "ID"),
        Column("name", "NAME"),
        Column("status", "STATUS"),
        Column("target", "TARGET", formatter=lambda x: f"{x}%" if x else ""),
        Column("evaluatedPercentage", "CURRENT", formatter=lambda x: f"{x:.2f}%" if x else ""),
        Column("description", "DESCRIPTION", wide_only=True),
    ]


def settings_columns() -> list[Column]:
    """Column definitions for settings objects."""
    return [
        Column("objectId", "OBJECT ID"),
        Column("schemaId", "SCHEMA"),
        Column("scope", "SCOPE"),
        Column("value", "VALUE", wide_only=True, formatter=lambda x: str(x)[:50] + "..." if x and len(str(x)) > 50 else str(x) if x else ""),
    ]


def bucket_columns() -> list[Column]:
    """Column definitions for bucket resources."""
    return [
        Column("bucketName", "NAME"),
        Column("table", "TABLE"),
        Column("status", "STATUS"),
        Column("retentionDays", "RETENTION"),
    ]


def app_columns() -> list[Column]:
    """Column definitions for app resources."""
    return [
        Column("id", "ID"),
        Column("name", "NAME"),
        Column("version", "VERSION"),
        Column("status", "STATUS"),
    ]


def user_columns() -> list[Column]:
    """Column definitions for user resources."""
    return [
        Column("uid", "UID"),
        Column("email", "EMAIL"),
        Column("name", "NAME"),
        Column("groups", "GROUPS", wide_only=True, formatter=lambda x: ", ".join(x) if x else ""),
    ]


def group_columns() -> list[Column]:
    """Column definitions for group resources."""
    return [
        Column("uuid", "UUID"),
        Column("name", "NAME"),
        Column("description", "DESCRIPTION"),
        Column("owner", "OWNER", wide_only=True),
    ]


def environment_columns() -> list[Column]:
    """Column definitions for environment/context resources."""
    return [
        Column("name", "NAME"),
        Column("environment", "ENVIRONMENT"),
        Column("current", "CURRENT", formatter=lambda x: "*" if x else ""),
        Column("auth_type", "AUTH TYPE"),
    ]


def limit_columns() -> list[Column]:
    """Column definitions for limit resources."""
    return [
        Column("name", "LIMIT"),
        Column("current", "CURRENT"),
        Column("max", "MAX"),
        Column("unit", "UNIT"),
        Column("percentage", "USAGE %", formatter=lambda x: f"{x:.1f}%" if x is not None else ""),
    ]


def policy_columns() -> list[Column]:
    """Column definitions for IAM policy resources."""
    return [
        Column("uuid", "UUID"),
        Column("name", "NAME"),
        Column("levelType", "LEVEL"),
        Column("levelId", "LEVEL ID", wide_only=True),
        Column("description", "DESCRIPTION", wide_only=True),
    ]


def binding_columns() -> list[Column]:
    """Column definitions for IAM binding resources."""
    return [
        Column("policyUuid", "POLICY UUID"),
        Column("groupUuid", "GROUP UUID"),
        Column("levelType", "LEVEL"),
        Column("levelId", "LEVEL ID", wide_only=True),
        Column("metadata", "METADATA", wide_only=True, formatter=lambda x: str(x)[:50] if x else ""),
    ]


def boundary_columns() -> list[Column]:
    """Column definitions for IAM boundary resources."""
    return [
        Column("policyUuid", "POLICY UUID"),
        Column("groupUuid", "GROUP UUID"),
        Column("levelType", "LEVEL"),
        Column("levelId", "LEVEL ID", wide_only=True),
    ]
