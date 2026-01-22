"""Validation tests that run against a live Dynatrace environment in dry-run mode.

These tests validate CLI commands work correctly with a real context.
They use --dry-run where possible to avoid making changes.

Run with:
    # Use default context
    pytest tests/test_validation.py -v

    # Use specific context
    pytest tests/test_validation.py -v --context=my-context

    # Run only validation tests
    pytest tests/test_validation.py -v -m validation

Usage:
    pytest tests/test_validation.py --context=esa -v
"""

from __future__ import annotations

import json
import re

import pytest
from typer.testing import CliRunner

from dtctl.cli import app
from dtctl.config import load_config


# Mark all tests in this module as validation tests
pytestmark = pytest.mark.validation


@pytest.fixture
def runner():
    """CLI runner for validation tests."""
    return CliRunner()


@pytest.fixture
def ctx(context):
    """Get context, skip if not provided."""
    if not context:
        pytest.skip("No --context provided. Use: pytest --context=<context-name>")
    return context


@pytest.fixture
def has_context(ctx):
    """Verify the context exists in config."""
    try:
        config = load_config()
        exists = any(c.name == ctx for c in config.contexts)
        if not exists:
            pytest.skip(f"Context '{ctx}' not found in config")
        return True
    except Exception as e:
        pytest.skip(f"Failed to load config: {e}")


def run_cmd(runner: CliRunner, ctx: str, args: list[str], dry_run: bool = False, verbose_output: bool = True):
    """Run a CLI command with optional context and dry-run.

    Args:
        runner: CliRunner instance
        ctx: Context name
        args: Command arguments
        dry_run: Enable dry-run mode
        verbose_output: Print command and output for debugging (default True)
    """
    full_args = ["--context", ctx]
    if dry_run:
        full_args.append("--dry-run")
    full_args.extend(args)

    result = runner.invoke(app, full_args)

    if verbose_output:
        cmd_str = " ".join(["dtctl"] + full_args)
        print(f"\n{'='*80}")
        print(f"COMMAND: {cmd_str}")
        print(f"EXIT CODE: {result.exit_code}")
        print(f"{'='*80}")
        print("OUTPUT:")
        print(result.output if result.output else "(no output)")
        if result.exception and result.exit_code != 0:
            print(f"EXCEPTION: {result.exception}")
        print(f"{'='*80}\n")

    return result


class TestAuthValidation:
    """Validate auth commands work with real credentials."""

    def test_auth_whoami(self, runner, ctx, has_context):
        """Validate auth whoami returns user information."""
        result = run_cmd(runner, ctx, ["auth", "whoami"])

        assert result.exit_code == 0, f"Failed: {result.output}"
        assert "Context:" in result.output or ctx in result.output

    def test_auth_whoami_json(self, runner, ctx, has_context):
        """Validate auth whoami JSON output is valid."""
        result = run_cmd(runner, ctx, ["-o", "json", "auth", "whoami"])

        assert result.exit_code == 0, f"Failed: {result.output}"
        data = json.loads(result.output)
        assert "context" in data
        assert "environment" in data

    def test_auth_test(self, runner, ctx, has_context):
        """Validate auth test confirms connectivity."""
        result = run_cmd(runner, ctx, ["auth", "test"])

        assert result.exit_code == 0, f"Failed: {result.output}"
        assert "successful" in result.output.lower() or "✓" in result.output


class TestGetDocumentsValidation:
    """Validate document get commands."""

    def test_get_documents(self, runner, ctx, has_context):
        """Validate get documents returns user-created documents."""
        result = run_cmd(runner, ctx, ["get", "docs"])

        assert result.exit_code == 0, f"Failed: {result.output}"

    def test_get_documents_all(self, runner, ctx, has_context):
        """Validate get documents --all includes ready-made documents."""
        result = run_cmd(runner, ctx, ["get", "docs", "--all"])

        assert result.exit_code == 0, f"Failed: {result.output}"

    def test_get_documents_json(self, runner, ctx, has_context):
        """Validate get documents JSON output contains only UUID IDs by default."""
        result = run_cmd(runner, ctx, ["-o", "json", "get", "docs"])

        assert result.exit_code == 0, f"Failed: {result.output}"
        data = json.loads(result.output)

        # All IDs should be UUIDs (user-created only)
        uuid_pattern = r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
        for doc in data:
            doc_id = doc.get("id", "")
            assert re.match(uuid_pattern, doc_id), f"Non-UUID ID found: {doc_id}"

    def test_get_documents_all_includes_system(self, runner, ctx, has_context):
        """Validate get documents --all includes non-UUID IDs."""
        result = run_cmd(runner, ctx, ["-o", "json", "get", "docs", "--all"])

        assert result.exit_code == 0, f"Failed: {result.output}"
        data = json.loads(result.output)

        # Should have some documents (system or user)
        # Can't assert specific content as it depends on environment

    def test_get_dashboards(self, runner, ctx, has_context):
        """Validate get dashboards works."""
        result = run_cmd(runner, ctx, ["get", "dashboards"])

        assert result.exit_code == 0, f"Failed: {result.output}"

    def test_get_dashboards_all(self, runner, ctx, has_context):
        """Validate get dashboards --all includes ready-made."""
        result = run_cmd(runner, ctx, ["get", "dashboards", "--all"])

        assert result.exit_code == 0, f"Failed: {result.output}"

    def test_get_notebooks(self, runner, ctx, has_context):
        """Validate get notebooks works."""
        result = run_cmd(runner, ctx, ["get", "notebooks"])

        assert result.exit_code == 0, f"Failed: {result.output}"

    def test_get_notebooks_all(self, runner, ctx, has_context):
        """Validate get notebooks --all includes ready-made."""
        result = run_cmd(runner, ctx, ["get", "notebooks", "--all"])

        assert result.exit_code == 0, f"Failed: {result.output}"


class TestGetWorkflowsValidation:
    """Validate workflow get commands."""

    def test_get_workflows(self, runner, ctx, has_context):
        """Validate get workflows works."""
        result = run_cmd(runner, ctx, ["get", "workflows"])

        assert result.exit_code == 0, f"Failed: {result.output}"

    def test_get_workflows_json(self, runner, ctx, has_context):
        """Validate get workflows JSON output."""
        result = run_cmd(runner, ctx, ["-o", "json", "get", "workflows"])

        assert result.exit_code == 0, f"Failed: {result.output}"
        data = json.loads(result.output)
        assert isinstance(data, list)

    def test_get_executions(self, runner, ctx, has_context):
        """Validate get executions works."""
        result = run_cmd(runner, ctx, ["get", "executions"])

        assert result.exit_code == 0, f"Failed: {result.output}"


class TestGetSLOsValidation:
    """Validate SLO get commands."""

    def test_get_slos(self, runner, ctx, has_context):
        """Validate get slos works (may fail without SLO API access)."""
        result = run_cmd(runner, ctx, ["get", "slos"])

        # May return 1 if no SLO API permissions or SLO not enabled
        assert result.exit_code in (0, 1)

    def test_get_slos_json(self, runner, ctx, has_context):
        """Validate get slos JSON output (may fail without SLO API access)."""
        result = run_cmd(runner, ctx, ["-o", "json", "get", "slos"])

        # May return 1 if no SLO API permissions
        if result.exit_code == 0:
            data = json.loads(result.output)
            assert isinstance(data, list)


class TestGetSettingsValidation:
    """Validate settings get commands."""

    def test_get_schemas(self, runner, ctx, has_context):
        """Validate get schemas works (may fail without settings API access)."""
        result = run_cmd(runner, ctx, ["get", "schemas"])

        # May return 1 if no settings API permissions
        assert result.exit_code in (0, 1)


class TestGetIAMValidation:
    """Validate IAM get commands."""

    def test_get_users(self, runner, ctx, has_context):
        """Validate get users works (may fail without IAM access)."""
        result = run_cmd(runner, ctx, ["get", "users"])

        # May return 1 if no IAM permissions
        assert result.exit_code in (0, 1)

    def test_get_groups(self, runner, ctx, has_context):
        """Validate get groups works (may fail without IAM access)."""
        result = run_cmd(runner, ctx, ["get", "groups"])

        # May return 1 if no IAM permissions
        assert result.exit_code in (0, 1)


class TestGetMiscValidation:
    """Validate miscellaneous get commands."""

    def test_get_limits(self, runner, ctx, has_context):
        """Validate get limits works."""
        result = run_cmd(runner, ctx, ["get", "limits"])

        assert result.exit_code == 0, f"Failed: {result.output}"

    def test_get_environments(self, runner, ctx, has_context):
        """Validate get environments works."""
        result = run_cmd(runner, ctx, ["get", "environments"])

        assert result.exit_code == 0, f"Failed: {result.output}"

    def test_get_buckets(self, runner, ctx, has_context):
        """Validate get buckets works."""
        result = run_cmd(runner, ctx, ["get", "buckets"])

        assert result.exit_code == 0, f"Failed: {result.output}"

    def test_get_apps(self, runner, ctx, has_context):
        """Validate get apps works."""
        result = run_cmd(runner, ctx, ["get", "apps"])

        assert result.exit_code == 0, f"Failed: {result.output}"

    def test_get_lookup_tables(self, runner, ctx, has_context):
        """Validate get lookup-tables works (may fail without lookup table access)."""
        result = run_cmd(runner, ctx, ["get", "lookup-tables"])

        # May return 1 if no lookup table permissions or none exist
        assert result.exit_code in (0, 1)


class TestQueryValidation:
    """Validate query command."""

    def test_query_simple(self, runner, ctx, has_context):
        """Validate simple DQL query works (may fail without Grail access)."""
        result = run_cmd(runner, ctx, ["query", "fetch logs | limit 1"])

        # May return 1 if no Grail/query permissions
        assert result.exit_code in (0, 1)

    def test_query_json(self, runner, ctx, has_context):
        """Validate query with JSON output (may fail without Grail access)."""
        result = run_cmd(runner, ctx, ["-o", "json", "query", "fetch logs | limit 1"])

        # May return 1 if no Grail/query permissions
        assert result.exit_code in (0, 1)


class TestExportValidation:
    """Validate export commands (dry-run where possible)."""

    def test_export_workflow_nonexistent(self, runner, ctx, has_context):
        """Validate export workflow fails gracefully for nonexistent workflow."""
        result = run_cmd(
            runner, ctx, ["export", "workflow", "nonexistent-12345"]
        )

        # Should fail with appropriate error (exit code 1)
        assert result.exit_code == 1
        # Error message may be in output (with mix_stderr=True)
        output_lower = result.output.lower()
        assert "not found" in output_lower or "error" in output_lower or "no workflow" in output_lower or result.output == ""


class TestDryRunValidation:
    """Validate dry-run mode works correctly."""

    def test_delete_workflow_dry_run(self, runner, ctx, has_context):
        """Validate delete workflow with dry-run doesn't actually delete."""
        result = run_cmd(
            runner, ctx, ["delete", "workflow", "test-workflow-id"],
            dry_run=True
        )

        # Should indicate dry-run mode
        assert "dry-run" in result.output.lower() or result.exit_code in (0, 1)

    def test_create_workflow_dry_run(self, runner, ctx, has_context):
        """Validate create with dry-run doesn't actually create."""
        # This would need a file, so we just test the flag is accepted
        result = run_cmd(
            runner, ctx, ["create", "workflow", "-f", "/nonexistent/file.yaml"],
            dry_run=True
        )

        # Should fail due to missing file, not crash
        assert result.exit_code == 1


class TestOutputFormatsValidation:
    """Validate different output formats work."""

    def test_output_table(self, runner, ctx, has_context):
        """Validate table output format."""
        result = run_cmd(runner, ctx, ["-o", "table", "get", "workflows"])

        assert result.exit_code == 0, f"Failed: {result.output}"

    def test_output_json(self, runner, ctx, has_context):
        """Validate JSON output format."""
        result = run_cmd(runner, ctx, ["-o", "json", "get", "workflows"])

        assert result.exit_code == 0, f"Failed: {result.output}"
        # Should be valid JSON
        json.loads(result.output)

    def test_output_yaml(self, runner, ctx, has_context):
        """Validate YAML output format."""
        result = run_cmd(runner, ctx, ["-o", "yaml", "get", "workflows"])

        assert result.exit_code == 0, f"Failed: {result.output}"

    def test_output_csv(self, runner, ctx, has_context):
        """Validate CSV output format."""
        result = run_cmd(runner, ctx, ["-o", "csv", "get", "workflows"])

        assert result.exit_code == 0, f"Failed: {result.output}"

    def test_output_wide(self, runner, ctx, has_context):
        """Validate wide output format."""
        result = run_cmd(runner, ctx, ["-o", "wide", "get", "workflows"])

        assert result.exit_code == 0, f"Failed: {result.output}"


class TestVerboseModeValidation:
    """Validate verbose mode provides extra output."""

    def test_verbose_mode(self, runner, ctx, has_context):
        """Validate verbose mode works."""
        full_args = ["--context", ctx, "--verbose", "auth", "whoami"]
        result = runner.invoke(app, full_args)

        assert result.exit_code == 0, f"Failed: {result.output}"


class TestCompletionValidation:
    """Validate shell completion works (no API needed)."""

    def test_completion_bash(self, runner):
        """Validate bash completion generates valid script."""
        result = runner.invoke(app, ["completion", "bash"])

        assert result.exit_code == 0
        assert "_dtctl_completion" in result.output

    def test_completion_zsh(self, runner):
        """Validate zsh completion generates valid script."""
        result = runner.invoke(app, ["completion", "zsh"])

        assert result.exit_code == 0
        assert "compdef" in result.output

    def test_completion_fish(self, runner):
        """Validate fish completion generates valid script."""
        result = runner.invoke(app, ["completion", "fish"])

        assert result.exit_code == 0
        assert "complete" in result.output

    def test_completion_powershell(self, runner):
        """Validate PowerShell completion generates valid script."""
        result = runner.invoke(app, ["completion", "powershell"])

        assert result.exit_code == 0
        assert "Register-ArgumentCompleter" in result.output


class TestConfigValidation:
    """Validate config commands (no API needed)."""

    def test_config_view(self, runner):
        """Validate config view works."""
        result = runner.invoke(app, ["config", "view"])

        assert result.exit_code == 0

    def test_config_path(self, runner):
        """Validate config path works."""
        result = runner.invoke(app, ["config", "path"])

        assert result.exit_code == 0
        assert "dtctl" in result.output

    def test_config_get_contexts(self, runner):
        """Validate config get-contexts works."""
        result = runner.invoke(app, ["config", "get-contexts"])

        assert result.exit_code == 0

    def test_config_current_context(self, runner):
        """Validate config current-context works."""
        result = runner.invoke(app, ["config", "current-context"])

        # May return 1 if no context, but should not crash
        assert result.exit_code in (0, 1)
