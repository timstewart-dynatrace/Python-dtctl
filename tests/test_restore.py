"""Tests for the restore command."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from dtctl.cli import app


class TestRestoreWorkflow:
    """Tests for workflow restore command."""

    @patch("dtctl.commands.restore.load_config")
    @patch("dtctl.commands.restore.create_client_from_config")
    @patch("dtctl.commands.restore.ResourceResolver")
    def test_workflow_restore_success(
        self,
        mock_resolver_class,
        mock_create_client,
        mock_load_config,
        cli_runner: CliRunner,
        mock_config,
        sample_workflow,
    ):
        """Test restoring a workflow successfully."""
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_get_response = MagicMock()
        mock_get_response.json.return_value = sample_workflow
        mock_post_response = MagicMock()
        mock_post_response.json.return_value = sample_workflow
        mock_client.get.return_value = mock_get_response
        mock_client.post.return_value = mock_post_response
        mock_create_client.return_value = mock_client

        mock_resolver = MagicMock()
        mock_resolver.resolve_workflow.return_value = "wf-12345"
        mock_resolver_class.return_value = mock_resolver

        result = cli_runner.invoke(
            app, ["restore", "workflow", "my-workflow", "v1", "--force"]
        )

        assert result.exit_code == 0
        assert "Success" in result.output or "Restored" in result.output

    @patch("dtctl.commands.restore.load_config")
    @patch("dtctl.commands.restore.create_client_from_config")
    @patch("dtctl.commands.restore.ResourceResolver")
    def test_workflow_restore_dry_run(
        self,
        mock_resolver_class,
        mock_create_client,
        mock_load_config,
        cli_runner: CliRunner,
        mock_config,
        sample_workflow,
    ):
        """Test workflow restore with dry-run mode."""
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_get_response = MagicMock()
        mock_get_response.json.return_value = sample_workflow
        mock_client.get.return_value = mock_get_response
        mock_create_client.return_value = mock_client

        mock_resolver = MagicMock()
        mock_resolver.resolve_workflow.return_value = "wf-12345"
        mock_resolver_class.return_value = mock_resolver

        result = cli_runner.invoke(
            app, ["--dry-run", "restore", "workflow", "my-workflow", "v1"]
        )

        assert result.exit_code == 0
        assert "Dry run" in result.output
        # Should not have called restore endpoint
        mock_client.post.assert_not_called()

    @patch("dtctl.commands.restore.load_config")
    @patch("dtctl.commands.restore.create_client_from_config")
    @patch("dtctl.commands.restore.ResourceResolver")
    def test_workflow_restore_version_not_found(
        self,
        mock_resolver_class,
        mock_create_client,
        mock_load_config,
        cli_runner: CliRunner,
        mock_config,
    ):
        """Test workflow restore when version not found."""
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_client.get.side_effect = Exception("Version not found")
        mock_create_client.return_value = mock_client

        mock_resolver = MagicMock()
        mock_resolver.resolve_workflow.return_value = "wf-12345"
        mock_resolver_class.return_value = mock_resolver

        result = cli_runner.invoke(
            app, ["restore", "workflow", "my-workflow", "v999", "--force"]
        )

        assert result.exit_code == 1
        assert "Error" in result.output

    @patch("dtctl.commands.restore.load_config")
    @patch("dtctl.commands.restore.create_client_from_config")
    @patch("dtctl.commands.restore.ResourceResolver")
    def test_workflow_restore_alias(
        self,
        mock_resolver_class,
        mock_create_client,
        mock_load_config,
        cli_runner: CliRunner,
        mock_config,
        sample_workflow,
    ):
        """Test workflow restore with 'wf' alias."""
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_get_response = MagicMock()
        mock_get_response.json.return_value = sample_workflow
        mock_post_response = MagicMock()
        mock_post_response.json.return_value = sample_workflow
        mock_client.get.return_value = mock_get_response
        mock_client.post.return_value = mock_post_response
        mock_create_client.return_value = mock_client

        mock_resolver = MagicMock()
        mock_resolver.resolve_workflow.return_value = "wf-12345"
        mock_resolver_class.return_value = mock_resolver

        result = cli_runner.invoke(
            app, ["restore", "wf", "my-workflow", "v1", "--force"]
        )

        assert result.exit_code == 0


class TestRestoreDashboard:
    """Tests for dashboard restore command."""

    @patch("dtctl.commands.restore.load_config")
    @patch("dtctl.commands.restore.create_client_from_config")
    @patch("dtctl.commands.restore.ResourceResolver")
    def test_dashboard_restore_success(
        self,
        mock_resolver_class,
        mock_create_client,
        mock_load_config,
        cli_runner: CliRunner,
        mock_config,
    ):
        """Test restoring a dashboard successfully."""
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_post_response = MagicMock()
        mock_post_response.json.return_value = {}
        mock_post_response.text = "{}"
        mock_client.post.return_value = mock_post_response
        mock_create_client.return_value = mock_client

        mock_resolver = MagicMock()
        mock_resolver.resolve_document.return_value = "dash-12345"
        mock_resolver_class.return_value = mock_resolver

        result = cli_runner.invoke(
            app, ["restore", "dashboard", "my-dashboard", "snap-1", "--force"]
        )

        assert result.exit_code == 0
        assert "Success" in result.output or "Restored" in result.output

    @patch("dtctl.commands.restore.load_config")
    @patch("dtctl.commands.restore.create_client_from_config")
    @patch("dtctl.commands.restore.ResourceResolver")
    def test_dashboard_restore_creates_snapshot(
        self,
        mock_resolver_class,
        mock_create_client,
        mock_load_config,
        cli_runner: CliRunner,
        mock_config,
    ):
        """Test dashboard restore creates pre-restore snapshot by default."""
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_post_response = MagicMock()
        mock_post_response.json.return_value = {}
        mock_post_response.text = "{}"
        mock_client.post.return_value = mock_post_response
        mock_create_client.return_value = mock_client

        mock_resolver = MagicMock()
        mock_resolver.resolve_document.return_value = "dash-12345"
        mock_resolver_class.return_value = mock_resolver

        result = cli_runner.invoke(
            app, ["restore", "dashboard", "my-dashboard", "snap-1", "--force"]
        )

        assert result.exit_code == 0
        # Should have called post twice: once for snapshot, once for restore
        assert mock_client.post.call_count == 2

    @patch("dtctl.commands.restore.load_config")
    @patch("dtctl.commands.restore.create_client_from_config")
    @patch("dtctl.commands.restore.ResourceResolver")
    def test_dashboard_restore_no_snapshot(
        self,
        mock_resolver_class,
        mock_create_client,
        mock_load_config,
        cli_runner: CliRunner,
        mock_config,
    ):
        """Test dashboard restore without creating pre-restore snapshot."""
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_post_response = MagicMock()
        mock_post_response.json.return_value = {}
        mock_post_response.text = "{}"
        mock_client.post.return_value = mock_post_response
        mock_create_client.return_value = mock_client

        mock_resolver = MagicMock()
        mock_resolver.resolve_document.return_value = "dash-12345"
        mock_resolver_class.return_value = mock_resolver

        result = cli_runner.invoke(
            app,
            [
                "restore",
                "dashboard",
                "my-dashboard",
                "snap-1",
                "--force",
                "--no-create-snapshot",
            ],
        )

        assert result.exit_code == 0
        # Should have called post only once (restore only)
        assert mock_client.post.call_count == 1

    @patch("dtctl.commands.restore.load_config")
    @patch("dtctl.commands.restore.create_client_from_config")
    @patch("dtctl.commands.restore.ResourceResolver")
    def test_dashboard_restore_dry_run(
        self,
        mock_resolver_class,
        mock_create_client,
        mock_load_config,
        cli_runner: CliRunner,
        mock_config,
    ):
        """Test dashboard restore with dry-run mode."""
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_create_client.return_value = mock_client

        mock_resolver = MagicMock()
        mock_resolver.resolve_document.return_value = "dash-12345"
        mock_resolver_class.return_value = mock_resolver

        result = cli_runner.invoke(
            app, ["--dry-run", "restore", "dashboard", "my-dashboard", "snap-1"]
        )

        assert result.exit_code == 0
        assert "Dry run" in result.output
        mock_client.post.assert_not_called()


class TestRestoreNotebook:
    """Tests for notebook restore command."""

    @patch("dtctl.commands.restore.load_config")
    @patch("dtctl.commands.restore.create_client_from_config")
    @patch("dtctl.commands.restore.ResourceResolver")
    def test_notebook_restore_success(
        self,
        mock_resolver_class,
        mock_create_client,
        mock_load_config,
        cli_runner: CliRunner,
        mock_config,
    ):
        """Test restoring a notebook successfully."""
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_post_response = MagicMock()
        mock_post_response.json.return_value = {}
        mock_post_response.text = "{}"
        mock_client.post.return_value = mock_post_response
        mock_create_client.return_value = mock_client

        mock_resolver = MagicMock()
        mock_resolver.resolve_document.return_value = "nb-12345"
        mock_resolver_class.return_value = mock_resolver

        result = cli_runner.invoke(
            app, ["restore", "notebook", "my-notebook", "snap-1", "--force"]
        )

        assert result.exit_code == 0

    @patch("dtctl.commands.restore.load_config")
    @patch("dtctl.commands.restore.create_client_from_config")
    @patch("dtctl.commands.restore.ResourceResolver")
    def test_notebook_restore_alias(
        self,
        mock_resolver_class,
        mock_create_client,
        mock_load_config,
        cli_runner: CliRunner,
        mock_config,
    ):
        """Test notebook restore with 'nb' alias."""
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_post_response = MagicMock()
        mock_post_response.json.return_value = {}
        mock_post_response.text = "{}"
        mock_client.post.return_value = mock_post_response
        mock_create_client.return_value = mock_client

        mock_resolver = MagicMock()
        mock_resolver.resolve_document.return_value = "nb-12345"
        mock_resolver_class.return_value = mock_resolver

        result = cli_runner.invoke(
            app, ["restore", "nb", "my-notebook", "snap-1", "--force"]
        )

        assert result.exit_code == 0


class TestRestoreConfirmation:
    """Tests for restore command confirmation prompts."""

    @patch("dtctl.commands.restore.load_config")
    @patch("dtctl.commands.restore.create_client_from_config")
    @patch("dtctl.commands.restore.ResourceResolver")
    def test_restore_prompts_for_confirmation(
        self,
        mock_resolver_class,
        mock_create_client,
        mock_load_config,
        cli_runner: CliRunner,
        mock_config,
        sample_workflow,
    ):
        """Test that restore prompts for confirmation without --force."""
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_get_response = MagicMock()
        mock_get_response.json.return_value = sample_workflow
        mock_client.get.return_value = mock_get_response
        mock_create_client.return_value = mock_client

        mock_resolver = MagicMock()
        mock_resolver.resolve_workflow.return_value = "wf-12345"
        mock_resolver_class.return_value = mock_resolver

        # User declines confirmation
        result = cli_runner.invoke(
            app, ["restore", "workflow", "my-workflow", "v1"], input="n\n"
        )

        assert result.exit_code == 0
        assert "Cancelled" in result.output
        # Should not have called restore endpoint
        mock_client.post.assert_not_called()

    @patch("dtctl.commands.restore.load_config")
    @patch("dtctl.commands.restore.create_client_from_config")
    @patch("dtctl.commands.restore.ResourceResolver")
    def test_restore_proceeds_on_confirmation(
        self,
        mock_resolver_class,
        mock_create_client,
        mock_load_config,
        cli_runner: CliRunner,
        mock_config,
        sample_workflow,
    ):
        """Test that restore proceeds when user confirms."""
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_get_response = MagicMock()
        mock_get_response.json.return_value = sample_workflow
        mock_post_response = MagicMock()
        mock_post_response.json.return_value = sample_workflow
        mock_client.get.return_value = mock_get_response
        mock_client.post.return_value = mock_post_response
        mock_create_client.return_value = mock_client

        mock_resolver = MagicMock()
        mock_resolver.resolve_workflow.return_value = "wf-12345"
        mock_resolver_class.return_value = mock_resolver

        # User confirms
        result = cli_runner.invoke(
            app, ["restore", "workflow", "my-workflow", "v1"], input="y\n"
        )

        assert result.exit_code == 0
        assert "Success" in result.output or "Restored" in result.output
