"""Template engine for variable substitution in manifests and queries.

Supports Jinja2-style template syntax with --set key=value CLI flags.
Example: {{ variable }} or {{ var | default("value") }}
"""

from __future__ import annotations

import re
from typing import Any

from jinja2 import BaseLoader, Environment, UndefinedError


def parse_set_values(set_values: list[str]) -> dict[str, str]:
    """Parse --set key=value arguments into a dictionary.

    Args:
        set_values: List of "key=value" strings

    Returns:
        Dictionary of key-value pairs

    Raises:
        ValueError: If a value doesn't contain '='
    """
    result: dict[str, str] = {}
    for item in set_values:
        if "=" not in item:
            raise ValueError(f"Invalid --set format: '{item}'. Expected 'key=value'")
        key, value = item.split("=", 1)
        result[key.strip()] = value.strip()
    return result


def render_template(template_str: str, variables: dict[str, Any]) -> str:
    """Render a template string with the given variables.

    Args:
        template_str: Template string with {{ variable }} placeholders
        variables: Dictionary of variables to substitute

    Returns:
        Rendered string

    Raises:
        ValueError: If a required variable is missing
    """
    env = Environment(loader=BaseLoader())

    # Add default filter
    def default_filter(value: Any, default_value: Any = "") -> Any:
        if value is None or (isinstance(value, str) and not value):
            return default_value
        return value

    env.filters["default"] = default_filter

    try:
        template = env.from_string(template_str)
        return template.render(**variables)
    except UndefinedError as e:
        raise ValueError(f"Template variable not defined: {e}") from e


def render_dict(data: dict[str, Any], variables: dict[str, Any]) -> dict[str, Any]:
    """Recursively render all string values in a dictionary.

    Args:
        data: Dictionary with potential template strings
        variables: Variables for substitution

    Returns:
        New dictionary with rendered values
    """
    result: dict[str, Any] = {}
    for key, value in data.items():
        if isinstance(value, str):
            result[key] = render_template(value, variables)
        elif isinstance(value, dict):
            result[key] = render_dict(value, variables)
        elif isinstance(value, list):
            result[key] = render_list(value, variables)
        else:
            result[key] = value
    return result


def render_list(data: list[Any], variables: dict[str, Any]) -> list[Any]:
    """Recursively render all string values in a list.

    Args:
        data: List with potential template strings
        variables: Variables for substitution

    Returns:
        New list with rendered values
    """
    result: list[Any] = []
    for item in data:
        if isinstance(item, str):
            result.append(render_template(item, variables))
        elif isinstance(item, dict):
            result.append(render_dict(item, variables))
        elif isinstance(item, list):
            result.append(render_list(item, variables))
        else:
            result.append(item)
    return result


def has_template_variables(text: str) -> bool:
    """Check if a string contains template variables.

    Args:
        text: String to check

    Returns:
        True if template variables are found
    """
    return bool(re.search(r"\{\{.*?\}\}", text))
