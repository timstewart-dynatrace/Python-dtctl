"""Pytest configuration and shared fixtures for dtctl tests."""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from dtctl.cli import app
from dtctl.client import Client
from dtctl.config import Config, Context, NamedContext, NamedToken


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--context",
        action="store",
        default=None,
        help="Dynatrace context to use for integration tests",
    )


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (require live API)"
    )
    config.addinivalue_line(
        "markers", "validation: marks tests as validation tests (run with --context)"
    )


@pytest.fixture
def context(request):
    """Get the context from command line option."""
    return request.config.getoption("--context")


@pytest.fixture
def cli_runner() -> CliRunner:
    """Create a CLI runner for testing commands."""
    return CliRunner()


@pytest.fixture
def mock_config() -> Config:
    """Create a mock configuration for testing."""
    return Config(
        current_context="test",
        contexts=[
            NamedContext(
                name="test",
                context=Context(
                    environment="https://test.apps.dynatrace.com",
                    token_ref="test-token",
                ),
            ),
            NamedContext(
                name="prod",
                context=Context(
                    environment="https://prod.apps.dynatrace.com",
                    token_ref="prod-token",
                ),
            ),
        ],
        tokens=[
            NamedToken(name="test-token", token="dt0c01.test-token"),
            NamedToken(name="prod-token", token="dt0c01.prod-token"),
        ],
    )


@pytest.fixture
def mock_client() -> MagicMock:
    """Create a mock HTTP client."""
    client = MagicMock(spec=Client)

    # Default response
    mock_response = MagicMock()
    mock_response.json.return_value = {}
    mock_response.text = ""
    mock_response.is_error = False
    mock_response.status_code = 200

    client.get.return_value = mock_response
    client.post.return_value = mock_response
    client.put.return_value = mock_response
    client.delete.return_value = mock_response

    return client


@pytest.fixture
def patch_config(mock_config: Config):
    """Patch load_config to return mock config."""
    with patch("dtctl.config.load_config", return_value=mock_config):
        yield mock_config


@pytest.fixture
def patch_client(mock_client: MagicMock):
    """Patch create_client_from_config to return mock client."""
    with patch("dtctl.client.create_client_from_config", return_value=mock_client):
        yield mock_client


class MockResponse:
    """Mock HTTP response for testing."""

    def __init__(
        self,
        data: Any = None,
        status_code: int = 200,
        text: str = "",
    ):
        self._data = data
        self.status_code = status_code
        self.text = text or (json.dumps(data) if data else "")
        self.is_error = status_code >= 400

    def json(self) -> Any:
        return self._data


# Sample data fixtures for various resources

@pytest.fixture
def sample_workflow() -> dict[str, Any]:
    """Sample workflow data."""
    return {
        "id": "wf-12345",
        "title": "Test Workflow",
        "description": "A test workflow",
        "owner": "user@example.com",
        "isDeployed": True,
        "isPrivate": False,
        "schemaVersion": 3,
        "tasks": {},
        "trigger": {},
    }


@pytest.fixture
def sample_workflow_versions() -> dict[str, Any]:
    """Sample workflow versions data."""
    return {
        "results": [
            {
                "id": "v1",
                "version": 1,
                "modifiedAt": "2024-01-01T00:00:00Z",
                "modifiedBy": "user@example.com",
            },
            {
                "id": "v2",
                "version": 2,
                "modifiedAt": "2024-01-02T00:00:00Z",
                "modifiedBy": "user@example.com",
            },
        ]
    }


@pytest.fixture
def sample_execution() -> dict[str, Any]:
    """Sample execution data."""
    return {
        "id": "exec-12345",
        "workflow": "wf-12345",
        "state": "SUCCESS",
        "startedAt": "2024-01-01T00:00:00Z",
        "endedAt": "2024-01-01T00:01:00Z",
        "triggerType": "MANUAL",
    }


@pytest.fixture
def sample_dashboard() -> dict[str, Any]:
    """Sample dashboard data."""
    return {
        "id": "dash-12345",
        "name": "Test Dashboard",
        "type": "dashboard",
        "owner": "user@example.com",
        "isPrivate": True,
        "version": 1,
    }


@pytest.fixture
def sample_dashboard_snapshots() -> dict[str, Any]:
    """Sample dashboard snapshots data."""
    return {
        "snapshots": [
            {
                "id": "snap-1",
                "createdAt": "2024-01-01T00:00:00Z",
                "description": "Initial snapshot",
            },
            {
                "id": "snap-2",
                "createdAt": "2024-01-02T00:00:00Z",
                "description": "Updated snapshot",
            },
        ]
    }


@pytest.fixture
def sample_query_result() -> dict[str, Any]:
    """Sample DQL query result."""
    return {
        "state": "SUCCEEDED",
        "result": {
            "records": [
                {"timestamp": "2024-01-01T00:00:00Z", "message": "Test log 1"},
                {"timestamp": "2024-01-01T00:01:00Z", "message": "Test log 2"},
            ],
            "metadata": {
                "totalCount": 2,
            },
        },
    }


@pytest.fixture
def sample_empty_query_result() -> dict[str, Any]:
    """Sample empty DQL query result."""
    return {
        "state": "SUCCEEDED",
        "result": {
            "records": [],
            "metadata": {
                "totalCount": 0,
            },
        },
    }


@pytest.fixture
def sample_user() -> dict[str, Any]:
    """Sample user data."""
    return {
        "uid": "user-12345",
        "email": "user@example.com",
        "name": "Test User",
        "groups": ["group-1", "group-2"],
    }


@pytest.fixture
def sample_lookup_table() -> dict[str, Any]:
    """Sample lookup table data."""
    return {
        "id": "lt-12345",
        "name": "Test Lookup Table",
        "description": "A test lookup table",
        "owner": "user@example.com",
        "rowCount": 100,
        "columns": [
            {"name": "key", "type": "string"},
            {"name": "value", "type": "string"},
        ],
    }


@pytest.fixture
def sample_lookup_table_list() -> dict[str, Any]:
    """Sample lookup table list data."""
    return {
        "tables": [
            {
                "id": "lt-12345",
                "name": "Table 1",
                "description": "First table",
                "rowCount": 100,
            },
            {
                "id": "lt-67890",
                "name": "Table 2",
                "description": "Second table",
                "rowCount": 50,
            },
        ]
    }


@pytest.fixture
def sample_lookup_table_data() -> dict[str, Any]:
    """Sample lookup table rows data."""
    return {
        "rows": [
            {"key": "k1", "value": "v1"},
            {"key": "k2", "value": "v2"},
            {"key": "k3", "value": "v3"},
        ]
    }


@pytest.fixture
def sample_limits() -> dict[str, Any]:
    """Sample account limits data."""
    return {
        "limits": [
            {"name": "Workflows", "current": 50, "max": 100, "unit": "count"},
            {"name": "Dashboards", "current": 25, "max": 500, "unit": "count"},
        ]
    }
