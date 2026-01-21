"""Tests for the wait command."""

from __future__ import annotations

import time
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from dtctl.cli import app
from dtctl.commands.wait import WaitCondition, evaluate_condition


class TestEvaluateCondition:
    """Tests for the condition evaluation logic."""

    def test_count_eq_true(self):
        """Test count equals condition when true."""
        records = [{"a": 1}, {"a": 2}, {"a": 3}]
        assert evaluate_condition(records, WaitCondition.COUNT_EQ, 3) is True

    def test_count_eq_false(self):
        """Test count equals condition when false."""
        records = [{"a": 1}, {"a": 2}]
        assert evaluate_condition(records, WaitCondition.COUNT_EQ, 3) is False

    def test_count_gte_true(self):
        """Test count >= condition when true."""
        records = [{"a": 1}, {"a": 2}, {"a": 3}]
        assert evaluate_condition(records, WaitCondition.COUNT_GTE, 3) is True
        assert evaluate_condition(records, WaitCondition.COUNT_GTE, 2) is True

    def test_count_gte_false(self):
        """Test count >= condition when false."""
        records = [{"a": 1}, {"a": 2}]
        assert evaluate_condition(records, WaitCondition.COUNT_GTE, 3) is False

    def test_count_gt_true(self):
        """Test count > condition when true."""
        records = [{"a": 1}, {"a": 2}, {"a": 3}]
        assert evaluate_condition(records, WaitCondition.COUNT_GT, 2) is True

    def test_count_gt_false(self):
        """Test count > condition when false."""
        records = [{"a": 1}, {"a": 2}]
        assert evaluate_condition(records, WaitCondition.COUNT_GT, 2) is False

    def test_count_lte_true(self):
        """Test count <= condition when true."""
        records = [{"a": 1}, {"a": 2}]
        assert evaluate_condition(records, WaitCondition.COUNT_LTE, 3) is True
        assert evaluate_condition(records, WaitCondition.COUNT_LTE, 2) is True

    def test_count_lte_false(self):
        """Test count <= condition when false."""
        records = [{"a": 1}, {"a": 2}, {"a": 3}]
        assert evaluate_condition(records, WaitCondition.COUNT_LTE, 2) is False

    def test_count_lt_true(self):
        """Test count < condition when true."""
        records = [{"a": 1}, {"a": 2}]
        assert evaluate_condition(records, WaitCondition.COUNT_LT, 3) is True

    def test_count_lt_false(self):
        """Test count < condition when false."""
        records = [{"a": 1}, {"a": 2}, {"a": 3}]
        assert evaluate_condition(records, WaitCondition.COUNT_LT, 3) is False

    def test_any_true(self):
        """Test any condition when true."""
        records = [{"a": 1}]
        assert evaluate_condition(records, WaitCondition.ANY, 0) is True

    def test_any_false(self):
        """Test any condition when false."""
        records = []
        assert evaluate_condition(records, WaitCondition.ANY, 0) is False

    def test_none_true(self):
        """Test none condition when true."""
        records = []
        assert evaluate_condition(records, WaitCondition.NONE, 0) is True

    def test_none_false(self):
        """Test none condition when false."""
        records = [{"a": 1}]
        assert evaluate_condition(records, WaitCondition.NONE, 0) is False


class TestWaitCommand:
    """Tests for the wait CLI command."""

    def test_wait_requires_query_or_file(self, cli_runner: CliRunner):
        """Test that wait command requires either query or file."""
        result = cli_runner.invoke(app, ["wait"])
        assert result.exit_code != 0
        assert "required" in result.output.lower() or "Error" in result.output

    def test_wait_file_not_found(self, cli_runner: CliRunner):
        """Test error when query file doesn't exist."""
        result = cli_runner.invoke(app, ["wait", "-f", "/nonexistent/file.dql"])
        assert result.exit_code != 0
        assert "not found" in result.output.lower()

    @patch("dtctl.commands.wait.load_config")
    @patch("dtctl.commands.wait.create_client_from_config")
    def test_wait_success_on_first_attempt(
        self,
        mock_create_client,
        mock_load_config,
        cli_runner: CliRunner,
        mock_config,
        sample_query_result,
    ):
        """Test wait succeeds when condition met on first attempt."""
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_create_client.return_value = mock_client

        # Mock QueryHandler - patch at the source module
        with patch("dtctl.resources.query.QueryHandler") as MockHandler:
            mock_handler = MagicMock()
            mock_handler.execute.return_value = sample_query_result
            MockHandler.return_value = mock_handler

            result = cli_runner.invoke(
                app, ["wait", "--condition", "any", "fetch logs | limit 10"]
            )

            assert result.exit_code == 0
            assert "Success" in result.output or "success" in result.output.lower()

    @patch("dtctl.commands.wait.load_config")
    @patch("dtctl.commands.wait.create_client_from_config")
    @patch("dtctl.commands.wait.time.sleep")
    def test_wait_timeout(
        self,
        mock_sleep,
        mock_create_client,
        mock_load_config,
        cli_runner: CliRunner,
        mock_config,
        sample_empty_query_result,
    ):
        """Test wait times out when condition never met."""
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_create_client.return_value = mock_client

        # Mock QueryHandler to always return empty results
        with patch("dtctl.resources.query.QueryHandler") as MockHandler:
            mock_handler = MagicMock()
            mock_handler.execute.return_value = sample_empty_query_result
            MockHandler.return_value = mock_handler

            result = cli_runner.invoke(
                app,
                [
                    "wait",
                    "--condition",
                    "any",
                    "--timeout",
                    "1",
                    "--interval",
                    "0.1",
                    "fetch logs | limit 10",
                ],
            )

            # Exit code 1 = timeout
            assert result.exit_code == 1
            assert "Timeout" in result.output or "timeout" in result.output.lower()

    @patch("dtctl.commands.wait.load_config")
    @patch("dtctl.commands.wait.create_client_from_config")
    def test_wait_query_error(
        self,
        mock_create_client,
        mock_load_config,
        cli_runner: CliRunner,
        mock_config,
    ):
        """Test wait handles query errors."""
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_create_client.return_value = mock_client

        # Mock QueryHandler to return failed query
        with patch("dtctl.resources.query.QueryHandler") as MockHandler:
            mock_handler = MagicMock()
            mock_handler.execute.return_value = {
                "state": "FAILED",
                "error": {"message": "Invalid query syntax"},
            }
            MockHandler.return_value = mock_handler

            result = cli_runner.invoke(
                app, ["wait", "--condition", "any", "invalid query"]
            )

            # Exit code 3 = error
            assert result.exit_code == 3
            assert "failed" in result.output.lower()

    @patch("dtctl.commands.wait.load_config")
    @patch("dtctl.commands.wait.create_client_from_config")
    def test_wait_count_condition(
        self,
        mock_create_client,
        mock_load_config,
        cli_runner: CliRunner,
        mock_config,
    ):
        """Test wait with count condition."""
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_create_client.return_value = mock_client

        # Return exactly 5 records
        with patch("dtctl.resources.query.QueryHandler") as MockHandler:
            mock_handler = MagicMock()
            mock_handler.execute.return_value = {
                "state": "SUCCEEDED",
                "result": {
                    "records": [{"a": i} for i in range(5)],
                    "metadata": {"totalCount": 5},
                },
            }
            MockHandler.return_value = mock_handler

            result = cli_runner.invoke(
                app,
                [
                    "wait",
                    "--condition",
                    "count",
                    "--count",
                    "5",
                    "fetch logs",
                ],
            )

            assert result.exit_code == 0

    @patch("dtctl.commands.wait.load_config")
    @patch("dtctl.commands.wait.create_client_from_config")
    def test_wait_quiet_mode(
        self,
        mock_create_client,
        mock_load_config,
        cli_runner: CliRunner,
        mock_config,
        sample_query_result,
    ):
        """Test wait with quiet mode suppresses progress output."""
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_create_client.return_value = mock_client

        with patch("dtctl.resources.query.QueryHandler") as MockHandler:
            mock_handler = MagicMock()
            mock_handler.execute.return_value = sample_query_result
            MockHandler.return_value = mock_handler

            result = cli_runner.invoke(
                app, ["wait", "--condition", "any", "--quiet", "fetch logs"]
            )

            assert result.exit_code == 0
            # In quiet mode, should have minimal output
            assert "Attempt" not in result.output

    @patch("dtctl.commands.wait.load_config")
    @patch("dtctl.commands.wait.create_client_from_config")
    @patch("dtctl.commands.wait.time.sleep")
    def test_wait_max_attempts(
        self,
        mock_sleep,
        mock_create_client,
        mock_load_config,
        cli_runner: CliRunner,
        mock_config,
        sample_empty_query_result,
    ):
        """Test wait with max attempts limit."""
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_create_client.return_value = mock_client

        with patch("dtctl.resources.query.QueryHandler") as MockHandler:
            mock_handler = MagicMock()
            mock_handler.execute.return_value = sample_empty_query_result
            MockHandler.return_value = mock_handler

            result = cli_runner.invoke(
                app,
                [
                    "wait",
                    "--condition",
                    "any",
                    "--max-attempts",
                    "3",
                    "--timeout",
                    "300",
                    "fetch logs",
                ],
            )

            # Exit code 2 = max attempts exceeded
            assert result.exit_code == 2
            assert mock_handler.execute.call_count == 3


class TestWaitConditionEnum:
    """Tests for WaitCondition enum."""

    def test_condition_values(self):
        """Test that all conditions have correct string values."""
        assert WaitCondition.COUNT_EQ.value == "count"
        assert WaitCondition.COUNT_GTE.value == "count-gte"
        assert WaitCondition.COUNT_GT.value == "count-gt"
        assert WaitCondition.COUNT_LTE.value == "count-lte"
        assert WaitCondition.COUNT_LT.value == "count-lt"
        assert WaitCondition.ANY.value == "any"
        assert WaitCondition.NONE.value == "none"
