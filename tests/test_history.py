"""Tests for the history command."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from dtctl.cli import app


class TestHistoryWorkflow:
    """Tests for workflow history command."""

    @patch("dtctl.commands.history.load_config")
    @patch("dtctl.commands.history.create_client_from_config")
    @patch("dtctl.commands.history.ResourceResolver")
    def test_workflow_history_success(
        self,
        mock_resolver_class,
        mock_create_client,
        mock_load_config,
        cli_runner: CliRunner,
        mock_config,
        sample_workflow_versions,
    ):
        """Test getting workflow history successfully."""
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = sample_workflow_versions
        mock_client.get.return_value = mock_response
        mock_create_client.return_value = mock_client

        mock_resolver = MagicMock()
        mock_resolver.resolve_workflow.return_value = "wf-12345"
        mock_resolver_class.return_value = mock_resolver

        result = cli_runner.invoke(app, ["history", "workflow", "my-workflow"])

        assert result.exit_code == 0
        assert "v1" in result.output or "Version" in result.output

    @patch("dtctl.commands.history.load_config")
    @patch("dtctl.commands.history.create_client_from_config")
    @patch("dtctl.commands.history.ResourceResolver")
    def test_workflow_history_no_versions(
        self,
        mock_resolver_class,
        mock_create_client,
        mock_load_config,
        cli_runner: CliRunner,
        mock_config,
    ):
        """Test workflow history when no versions exist."""
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": []}
        mock_client.get.return_value = mock_response
        mock_create_client.return_value = mock_client

        mock_resolver = MagicMock()
        mock_resolver.resolve_workflow.return_value = "wf-12345"
        mock_resolver_class.return_value = mock_resolver

        result = cli_runner.invoke(app, ["history", "workflow", "my-workflow"])

        assert result.exit_code == 0
        assert "No version history" in result.output

    @patch("dtctl.commands.history.load_config")
    @patch("dtctl.commands.history.create_client_from_config")
    @patch("dtctl.commands.history.ResourceResolver")
    def test_workflow_history_with_limit(
        self,
        mock_resolver_class,
        mock_create_client,
        mock_load_config,
        cli_runner: CliRunner,
        mock_config,
        sample_workflow_versions,
    ):
        """Test workflow history with custom limit."""
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = sample_workflow_versions
        mock_client.get.return_value = mock_response
        mock_create_client.return_value = mock_client

        mock_resolver = MagicMock()
        mock_resolver.resolve_workflow.return_value = "wf-12345"
        mock_resolver_class.return_value = mock_resolver

        result = cli_runner.invoke(
            app, ["history", "workflow", "my-workflow", "--limit", "5"]
        )

        assert result.exit_code == 0
        # Verify the limit was passed to the API
        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert call_args[1]["params"]["limit"] == 5

    @patch("dtctl.commands.history.load_config")
    @patch("dtctl.commands.history.create_client_from_config")
    @patch("dtctl.commands.history.ResourceResolver")
    def test_workflow_history_json_output(
        self,
        mock_resolver_class,
        mock_create_client,
        mock_load_config,
        cli_runner: CliRunner,
        mock_config,
        sample_workflow_versions,
    ):
        """Test workflow history with JSON output."""
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = sample_workflow_versions
        mock_client.get.return_value = mock_response
        mock_create_client.return_value = mock_client

        mock_resolver = MagicMock()
        mock_resolver.resolve_workflow.return_value = "wf-12345"
        mock_resolver_class.return_value = mock_resolver

        result = cli_runner.invoke(
            app, ["history", "workflow", "my-workflow", "-o", "json"]
        )

        assert result.exit_code == 0
        # JSON output should be parseable
        import json
        data = json.loads(result.output)
        assert isinstance(data, list)


class TestHistoryDashboard:
    """Tests for dashboard history command."""

    @patch("dtctl.commands.history.load_config")
    @patch("dtctl.commands.history.create_client_from_config")
    @patch("dtctl.commands.history.ResourceResolver")
    def test_dashboard_history_success(
        self,
        mock_resolver_class,
        mock_create_client,
        mock_load_config,
        cli_runner: CliRunner,
        mock_config,
        sample_dashboard_snapshots,
    ):
        """Test getting dashboard history successfully."""
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = sample_dashboard_snapshots
        mock_client.get.return_value = mock_response
        mock_create_client.return_value = mock_client

        mock_resolver = MagicMock()
        mock_resolver.resolve_document.return_value = "dash-12345"
        mock_resolver_class.return_value = mock_resolver

        result = cli_runner.invoke(app, ["history", "dashboard", "my-dashboard"])

        assert result.exit_code == 0
        assert "snap-1" in result.output or "Snapshot" in result.output

    @patch("dtctl.commands.history.load_config")
    @patch("dtctl.commands.history.create_client_from_config")
    @patch("dtctl.commands.history.ResourceResolver")
    def test_dashboard_history_alias(
        self,
        mock_resolver_class,
        mock_create_client,
        mock_load_config,
        cli_runner: CliRunner,
        mock_config,
        sample_dashboard_snapshots,
    ):
        """Test dashboard history with 'dash' alias."""
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = sample_dashboard_snapshots
        mock_client.get.return_value = mock_response
        mock_create_client.return_value = mock_client

        mock_resolver = MagicMock()
        mock_resolver.resolve_document.return_value = "dash-12345"
        mock_resolver_class.return_value = mock_resolver

        result = cli_runner.invoke(app, ["history", "dash", "my-dashboard"])

        assert result.exit_code == 0


class TestHistoryNotebook:
    """Tests for notebook history command."""

    @patch("dtctl.commands.history.load_config")
    @patch("dtctl.commands.history.create_client_from_config")
    @patch("dtctl.commands.history.ResourceResolver")
    def test_notebook_history_success(
        self,
        mock_resolver_class,
        mock_create_client,
        mock_load_config,
        cli_runner: CliRunner,
        mock_config,
        sample_dashboard_snapshots,  # Same structure as dashboard
    ):
        """Test getting notebook history successfully."""
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = sample_dashboard_snapshots
        mock_client.get.return_value = mock_response
        mock_create_client.return_value = mock_client

        mock_resolver = MagicMock()
        mock_resolver.resolve_document.return_value = "nb-12345"
        mock_resolver_class.return_value = mock_resolver

        result = cli_runner.invoke(app, ["history", "notebook", "my-notebook"])

        assert result.exit_code == 0

    @patch("dtctl.commands.history.load_config")
    @patch("dtctl.commands.history.create_client_from_config")
    @patch("dtctl.commands.history.ResourceResolver")
    def test_notebook_history_alias(
        self,
        mock_resolver_class,
        mock_create_client,
        mock_load_config,
        cli_runner: CliRunner,
        mock_config,
        sample_dashboard_snapshots,
    ):
        """Test notebook history with 'nb' alias."""
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = sample_dashboard_snapshots
        mock_client.get.return_value = mock_response
        mock_create_client.return_value = mock_client

        mock_resolver = MagicMock()
        mock_resolver.resolve_document.return_value = "nb-12345"
        mock_resolver_class.return_value = mock_resolver

        result = cli_runner.invoke(app, ["history", "nb", "my-notebook"])

        assert result.exit_code == 0


class TestHistoryErrors:
    """Tests for history command error handling."""

    @patch("dtctl.commands.history.load_config")
    @patch("dtctl.commands.history.create_client_from_config")
    @patch("dtctl.commands.history.ResourceResolver")
    def test_workflow_history_api_error(
        self,
        mock_resolver_class,
        mock_create_client,
        mock_load_config,
        cli_runner: CliRunner,
        mock_config,
    ):
        """Test workflow history handles API errors."""
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_client.get.side_effect = Exception("API Error")
        mock_create_client.return_value = mock_client

        mock_resolver = MagicMock()
        mock_resolver.resolve_workflow.return_value = "wf-12345"
        mock_resolver_class.return_value = mock_resolver

        result = cli_runner.invoke(app, ["history", "workflow", "my-workflow"])

        assert result.exit_code == 1
        assert "Error" in result.output
