"""Integration tests that run against a live Dynatrace environment.

These tests require a valid configuration context. Run with:

    # Use default context
    pytest tests/test_integration.py -v

    # Use specific context
    pytest tests/test_integration.py -v --context=esa

    # Skip integration tests
    pytest tests/ -v --ignore=tests/test_integration.py

    # Or use marker
    pytest tests/ -v -m "not integration"
"""

from __future__ import annotations

import pytest
from typer.testing import CliRunner

from dtctl.cli import app
from dtctl.config import load_config


# context fixture is defined in conftest.py


@pytest.fixture
def integration_runner():
    """CLI runner for integration tests."""
    return CliRunner()


@pytest.fixture
def has_valid_context(context):
    """Check if we have a valid context configured."""
    try:
        config = load_config()
        if context:
            # Check if specified context exists
            exists = any(c.name == context for c in config.contexts)
            return exists
        # Check if any context is configured
        return config.current_context is not None
    except Exception as e:
        print(f"Error loading config: {e}")
        return False


# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


class TestAuthIntegration:
    """Integration tests for auth commands."""

    def test_auth_whoami(self, integration_runner, context, has_valid_context):
        """Test auth whoami with real credentials."""
        if not has_valid_context:
            pytest.skip("No valid context configured")

        args = ["auth", "whoami"]
        if context:
            args = ["--context", context] + args

        result = integration_runner.invoke(app, args)
        assert result.exit_code == 0
        assert "Context:" in result.output or "context" in result.output.lower()

    def test_auth_test(self, integration_runner, context, has_valid_context):
        """Test auth test with real credentials."""
        if not has_valid_context:
            pytest.skip("No valid context configured")

        args = ["auth", "test"]
        if context:
            args = ["--context", context] + args

        result = integration_runner.invoke(app, args)
        assert result.exit_code == 0
        assert "successful" in result.output.lower() or "✓" in result.output


class TestGetIntegration:
    """Integration tests for get commands."""

    def test_get_workflows(self, integration_runner, context, has_valid_context):
        """Test getting workflows list."""
        if not has_valid_context:
            pytest.skip("No valid context configured")

        args = ["get", "workflows"]
        if context:
            args = ["--context", context] + args

        result = integration_runner.invoke(app, args)
        # Should succeed even if no workflows exist
        assert result.exit_code == 0

    def test_get_dashboards(self, integration_runner, context, has_valid_context):
        """Test getting dashboards list."""
        if not has_valid_context:
            pytest.skip("No valid context configured")

        args = ["get", "dashboards"]
        if context:
            args = ["--context", context] + args

        result = integration_runner.invoke(app, args)
        assert result.exit_code == 0

    def test_get_slos(self, integration_runner, context, has_valid_context):
        """Test getting SLOs list."""
        if not has_valid_context:
            pytest.skip("No valid context configured")

        args = ["get", "slos"]
        if context:
            args = ["--context", context] + args

        result = integration_runner.invoke(app, args)
        assert result.exit_code == 0

    def test_get_limits(self, integration_runner, context, has_valid_context):
        """Test getting account limits."""
        if not has_valid_context:
            pytest.skip("No valid context configured")

        args = ["get", "limits"]
        if context:
            args = ["--context", context] + args

        result = integration_runner.invoke(app, args)
        assert result.exit_code == 0

    def test_get_users(self, integration_runner, context, has_valid_context):
        """Test getting users list."""
        if not has_valid_context:
            pytest.skip("No valid context configured")

        args = ["get", "users"]
        if context:
            args = ["--context", context] + args

        result = integration_runner.invoke(app, args)
        # May fail if no IAM access, but shouldn't crash
        assert result.exit_code in (0, 1)

    def test_get_lookup_tables(self, integration_runner, context, has_valid_context):
        """Test getting lookup tables list."""
        if not has_valid_context:
            pytest.skip("No valid context configured")

        args = ["get", "lookup-tables"]
        if context:
            args = ["--context", context] + args

        result = integration_runner.invoke(app, args)
        assert result.exit_code == 0


class TestQueryIntegration:
    """Integration tests for query command."""

    def test_simple_query(self, integration_runner, context, has_valid_context):
        """Test running a simple DQL query."""
        if not has_valid_context:
            pytest.skip("No valid context configured")

        args = ["query", "fetch logs | limit 5"]
        if context:
            args = ["--context", context] + args

        result = integration_runner.invoke(app, args)
        # Query should succeed (may return 0 results)
        assert result.exit_code == 0

    def test_query_json_output(self, integration_runner, context, has_valid_context):
        """Test query with JSON output."""
        if not has_valid_context:
            pytest.skip("No valid context configured")

        args = ["-o", "json", "query", "fetch logs | limit 1"]
        if context:
            args = ["--context", context] + args

        result = integration_runner.invoke(app, args)
        assert result.exit_code == 0


class TestConfigIntegration:
    """Integration tests for config commands."""

    def test_config_view(self, integration_runner):
        """Test viewing config."""
        result = integration_runner.invoke(app, ["config", "view"])
        assert result.exit_code == 0

    def test_config_get_contexts(self, integration_runner):
        """Test listing contexts."""
        result = integration_runner.invoke(app, ["config", "get-contexts"])
        assert result.exit_code == 0

    def test_config_current_context(self, integration_runner):
        """Test showing current context."""
        result = integration_runner.invoke(app, ["config", "current-context"])
        # May return 1 if no context set, but shouldn't crash
        assert result.exit_code in (0, 1)

    def test_config_path(self, integration_runner):
        """Test showing config path."""
        result = integration_runner.invoke(app, ["config", "path"])
        assert result.exit_code == 0
        assert ".config" in result.output or "dtctl" in result.output


class TestHistoryIntegration:
    """Integration tests for history command."""

    def test_workflow_history_nonexistent(self, integration_runner, context, has_valid_context):
        """Test workflow history for nonexistent workflow."""
        if not has_valid_context:
            pytest.skip("No valid context configured")

        args = ["history", "workflow", "nonexistent-workflow-id-12345"]
        if context:
            args = ["--context", context] + args

        result = integration_runner.invoke(app, args)
        # Should fail gracefully with exit code 1
        assert result.exit_code == 1


class TestCompletionIntegration:
    """Integration tests for completion command (no auth needed)."""

    def test_completion_bash(self, integration_runner):
        """Test bash completion generation."""
        result = integration_runner.invoke(app, ["completion", "bash"])
        assert result.exit_code == 0
        assert "_dtctl_completion" in result.output

    def test_completion_zsh(self, integration_runner):
        """Test zsh completion generation."""
        result = integration_runner.invoke(app, ["completion", "zsh"])
        assert result.exit_code == 0
        assert "compdef" in result.output

    def test_completion_fish(self, integration_runner):
        """Test fish completion generation."""
        result = integration_runner.invoke(app, ["completion", "fish"])
        assert result.exit_code == 0
        assert "complete" in result.output

    def test_completion_powershell(self, integration_runner):
        """Test PowerShell completion generation."""
        result = integration_runner.invoke(app, ["completion", "powershell"])
        assert result.exit_code == 0
        assert "Register-ArgumentCompleter" in result.output
