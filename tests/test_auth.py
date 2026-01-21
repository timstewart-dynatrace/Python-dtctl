"""Tests for the auth command."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from dtctl.cli import app


class TestAuthWhoami:
    """Tests for auth whoami command."""

    @patch("dtctl.commands.auth.load_config")
    @patch("dtctl.commands.auth.create_client_from_config")
    def test_whoami_success(
        self,
        mock_create_client,
        mock_load_config,
        cli_runner: CliRunner,
        mock_config,
        sample_user,
    ):
        """Test whoami returns user info successfully."""
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = sample_user
        mock_client.get.return_value = mock_response
        mock_create_client.return_value = mock_client

        result = cli_runner.invoke(app, ["auth", "whoami"])

        assert result.exit_code == 0
        assert "test" in result.output  # context name
        assert "test.apps.dynatrace.com" in result.output  # environment

    @patch("dtctl.commands.auth.load_config")
    @patch("dtctl.commands.auth.create_client_from_config")
    def test_whoami_shows_user_info(
        self,
        mock_create_client,
        mock_load_config,
        cli_runner: CliRunner,
        mock_config,
        sample_user,
    ):
        """Test whoami shows user details when available."""
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = sample_user
        mock_client.get.return_value = mock_response
        mock_create_client.return_value = mock_client

        result = cli_runner.invoke(app, ["auth", "whoami"])

        assert result.exit_code == 0
        # Should contain user info
        assert "user@example.com" in result.output or "Test User" in result.output

    @patch("dtctl.commands.auth.load_config")
    @patch("dtctl.commands.auth.create_client_from_config")
    def test_whoami_json_output(
        self,
        mock_create_client,
        mock_load_config,
        cli_runner: CliRunner,
        mock_config,
        sample_user,
    ):
        """Test whoami with JSON output."""
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = sample_user
        mock_client.get.return_value = mock_response
        mock_create_client.return_value = mock_client

        result = cli_runner.invoke(app, ["auth", "whoami", "-o", "json"])

        assert result.exit_code == 0
        # Output should be valid JSON
        import json
        data = json.loads(result.output)
        assert "context" in data
        assert "environment" in data

    @patch("dtctl.commands.auth.load_config")
    @patch("dtctl.commands.auth.create_client_from_config")
    def test_whoami_api_error_fallback(
        self,
        mock_create_client,
        mock_load_config,
        cli_runner: CliRunner,
        mock_config,
    ):
        """Test whoami handles API errors gracefully."""
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_client.get.side_effect = Exception("API Error")
        mock_create_client.return_value = mock_client

        result = cli_runner.invoke(app, ["auth", "whoami"])

        # Should still succeed but with limited info
        assert result.exit_code == 0
        assert "test" in result.output  # context name should still be shown

    @patch("dtctl.commands.auth.load_config")
    def test_whoami_no_context(
        self,
        mock_load_config,
        cli_runner: CliRunner,
    ):
        """Test whoami when no context is configured."""
        from dtctl.config import Config

        mock_load_config.return_value = Config()  # Empty config

        result = cli_runner.invoke(app, ["auth", "whoami"])

        # Should fail with exit code 1
        assert result.exit_code == 1


class TestAuthTest:
    """Tests for auth test command."""

    @patch("dtctl.commands.auth.load_config")
    @patch("dtctl.commands.auth.create_client_from_config")
    def test_auth_test_success(
        self,
        mock_create_client,
        mock_load_config,
        cli_runner: CliRunner,
        mock_config,
    ):
        """Test auth test succeeds when API is accessible."""
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"limits": []}
        mock_client.get.return_value = mock_response
        mock_create_client.return_value = mock_client

        result = cli_runner.invoke(app, ["auth", "test"])

        assert result.exit_code == 0
        assert "successful" in result.output.lower() or "✓" in result.output

    @patch("dtctl.commands.auth.load_config")
    @patch("dtctl.commands.auth.create_client_from_config")
    def test_auth_test_failure(
        self,
        mock_create_client,
        mock_load_config,
        cli_runner: CliRunner,
        mock_config,
    ):
        """Test auth test fails when API is not accessible."""
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_client.get.side_effect = Exception("Authentication failed")
        mock_create_client.return_value = mock_client

        result = cli_runner.invoke(app, ["auth", "test"])

        assert result.exit_code == 1
        assert "failed" in result.output.lower() or "✗" in result.output

    @patch("dtctl.commands.auth.load_config")
    @patch("dtctl.commands.auth.create_client_from_config")
    def test_auth_test_json_output_success(
        self,
        mock_create_client,
        mock_load_config,
        cli_runner: CliRunner,
        mock_config,
    ):
        """Test auth test with JSON output."""
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"limits": []}
        mock_client.get.return_value = mock_response
        mock_create_client.return_value = mock_client

        result = cli_runner.invoke(app, ["auth", "test", "-o", "json"])

        assert result.exit_code == 0
        # For JSON mode, successful message should appear
        assert "success" in result.output.lower()

    @patch("dtctl.commands.auth.load_config")
    @patch("dtctl.commands.auth.create_client_from_config")
    def test_auth_test_failure_output(
        self,
        mock_create_client,
        mock_load_config,
        cli_runner: CliRunner,
        mock_config,
    ):
        """Test auth test failure output."""
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_client.get.side_effect = Exception("Auth failed")
        mock_create_client.return_value = mock_client

        result = cli_runner.invoke(app, ["auth", "test", "-o", "json"])

        assert result.exit_code == 1
        # Should indicate failure
        assert "failed" in result.output.lower()

    @patch("dtctl.commands.auth.load_config")
    def test_auth_test_no_context(
        self,
        mock_load_config,
        cli_runner: CliRunner,
    ):
        """Test auth test when no context is configured."""
        from dtctl.config import Config

        mock_load_config.return_value = Config()  # Empty config

        result = cli_runner.invoke(app, ["auth", "test"])

        assert result.exit_code == 1


class TestAuthWithOAuth:
    """Tests for auth commands with OAuth authentication."""

    @patch("dtctl.commands.auth.load_config")
    @patch("dtctl.commands.auth.create_client_from_config")
    def test_whoami_oauth_context(
        self,
        mock_create_client,
        mock_load_config,
        cli_runner: CliRunner,
    ):
        """Test whoami shows OAuth info when using OAuth context."""
        from dtctl.config import Config, Context, NamedContext

        oauth_config = Config(
            current_context="oauth-test",
            contexts=[
                NamedContext(
                    name="oauth-test",
                    context=Context(
                        environment="https://test.apps.dynatrace.com",
                        oauth_client_id="my-client-id",
                        oauth_client_secret="my-secret",
                        oauth_resource_urn="urn:dtenvironment:abc123",
                    ),
                ),
            ],
        )
        mock_load_config.return_value = oauth_config

        mock_client = MagicMock()
        mock_client.get.side_effect = Exception("API Error")  # API call fails
        mock_create_client.return_value = mock_client

        result = cli_runner.invoke(app, ["auth", "whoami"])

        assert result.exit_code == 0
        assert "oauth2" in result.output.lower() or "OAuth" in result.output
        # Should show client ID when using OAuth
        assert "my-client-id" in result.output or "Client ID" in result.output
