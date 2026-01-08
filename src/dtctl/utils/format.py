"""Format conversion utilities for YAML/JSON handling."""

from __future__ import annotations

import json
from typing import Any

import yaml


def detect_format(content: str) -> str:
    """Detect if content is JSON or YAML.

    Args:
        content: String content to analyze

    Returns:
        "json" or "yaml"
    """
    content = content.strip()
    if content.startswith("{") or content.startswith("["):
        return "json"
    return "yaml"


def parse_content(content: str) -> dict[str, Any] | list[Any]:
    """Parse content as either JSON or YAML.

    Args:
        content: String content to parse

    Returns:
        Parsed data structure

    Raises:
        ValueError: If content cannot be parsed
    """
    fmt = detect_format(content)
    try:
        if fmt == "json":
            return json.loads(content)
        else:
            return yaml.safe_load(content)
    except (json.JSONDecodeError, yaml.YAMLError) as e:
        raise ValueError(f"Failed to parse {fmt.upper()}: {e}") from e


def to_json(data: Any, indent: int = 2) -> str:
    """Convert data to JSON string.

    Args:
        data: Data to convert
        indent: Indentation level

    Returns:
        JSON string
    """
    return json.dumps(data, indent=indent, default=str)


def to_yaml(data: Any) -> str:
    """Convert data to YAML string.

    Args:
        data: Data to convert

    Returns:
        YAML string
    """
    return yaml.dump(data, default_flow_style=False, sort_keys=False)


def yaml_to_json(yaml_content: str) -> str:
    """Convert YAML content to JSON.

    Args:
        yaml_content: YAML string

    Returns:
        JSON string
    """
    data = yaml.safe_load(yaml_content)
    return to_json(data)


def json_to_yaml(json_content: str) -> str:
    """Convert JSON content to YAML.

    Args:
        json_content: JSON string

    Returns:
        YAML string
    """
    data = json.loads(json_content)
    return to_yaml(data)
