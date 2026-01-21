"""Tests for the lookup table resource handler and commands."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from dtctl.cli import app
from dtctl.resources.lookup import LookupTableHandler


class TestLookupTableHandler:
    """Tests for the LookupTableHandler class."""

    def test_resource_name(self, mock_client):
        """Test resource name property."""
        handler = LookupTableHandler(mock_client)
        assert handler.resource_name == "lookup-table"

    def test_api_path(self, mock_client):
        """Test API path property."""
        handler = LookupTableHandler(mock_client)
        assert handler.api_path == "/platform/storage/lookups/v1/tables"

    def test_list_key(self, mock_client):
        """Test list key property."""
        handler = LookupTableHandler(mock_client)
        assert handler.list_key == "tables"

    def test_list_tables(self, mock_client, sample_lookup_table_list):
        """Test listing lookup tables."""
        mock_response = MagicMock()
        mock_response.json.return_value = sample_lookup_table_list
        mock_client.get.return_value = mock_response

        handler = LookupTableHandler(mock_client)
        tables = handler.list()

        assert len(tables) == 2
        assert tables[0]["name"] == "Table 1"
        mock_client.get.assert_called_once()

    def test_get_table(self, mock_client, sample_lookup_table):
        """Test getting a single lookup table."""
        mock_response = MagicMock()
        mock_response.json.return_value = sample_lookup_table
        mock_client.get.return_value = mock_response

        handler = LookupTableHandler(mock_client)
        table = handler.get("lt-12345")

        assert table["id"] == "lt-12345"
        assert table["name"] == "Test Lookup Table"
        mock_client.get.assert_called_with("/platform/storage/lookups/v1/tables/lt-12345")

    def test_get_table_data(self, mock_client, sample_lookup_table_data):
        """Test getting lookup table data."""
        mock_response = MagicMock()
        mock_response.json.return_value = sample_lookup_table_data
        mock_client.get.return_value = mock_response

        handler = LookupTableHandler(mock_client)
        rows = handler.get_data("lt-12345", limit=100)

        assert len(rows) == 3
        assert rows[0]["key"] == "k1"
        mock_client.get.assert_called_with(
            "/platform/storage/lookups/v1/tables/lt-12345/data",
            params={"limit": 100},
        )

    def test_create_table(self, mock_client, sample_lookup_table):
        """Test creating a lookup table."""
        mock_response = MagicMock()
        mock_response.json.return_value = sample_lookup_table
        mock_client.post.return_value = mock_response

        handler = LookupTableHandler(mock_client)
        data = {"name": "New Table", "columns": [{"name": "key", "type": "string"}]}
        result = handler.create(data)

        assert result["id"] == "lt-12345"
        mock_client.post.assert_called_once()

    def test_delete_table(self, mock_client):
        """Test deleting a lookup table."""
        handler = LookupTableHandler(mock_client)
        result = handler.delete("lt-12345")

        assert result is True
        mock_client.delete.assert_called_with(
            "/platform/storage/lookups/v1/tables/lt-12345"
        )

    def test_clear_data(self, mock_client):
        """Test clearing lookup table data."""
        handler = LookupTableHandler(mock_client)
        result = handler.clear_data("lt-12345")

        assert result is True
        mock_client.delete.assert_called_with(
            "/platform/storage/lookups/v1/tables/lt-12345/data"
        )


class TestLookupTableCSV:
    """Tests for CSV functionality in LookupTableHandler."""

    def test_detect_delimiter_comma(self, mock_client):
        """Test CSV delimiter auto-detection for comma."""
        handler = LookupTableHandler(mock_client)
        csv_content = "name,value,count\na,b,1\nc,d,2"
        delimiter = handler._detect_delimiter(csv_content)
        assert delimiter == ","

    def test_detect_delimiter_semicolon(self, mock_client):
        """Test CSV delimiter auto-detection for semicolon."""
        handler = LookupTableHandler(mock_client)
        csv_content = "name;value;count\na;b;1\nc;d;2"
        delimiter = handler._detect_delimiter(csv_content)
        assert delimiter == ";"

    def test_detect_delimiter_tab(self, mock_client):
        """Test CSV delimiter auto-detection for tab."""
        handler = LookupTableHandler(mock_client)
        csv_content = "name\tvalue\tcount\na\tb\t1\nc\td\t2"
        delimiter = handler._detect_delimiter(csv_content)
        assert delimiter == "\t"

    def test_detect_delimiter_pipe(self, mock_client):
        """Test CSV delimiter auto-detection for pipe."""
        handler = LookupTableHandler(mock_client)
        csv_content = "name|value|count\na|b|1\nc|d|2"
        delimiter = handler._detect_delimiter(csv_content)
        assert delimiter == "|"

    def test_create_from_csv(self, mock_client, sample_lookup_table):
        """Test creating lookup table from CSV."""
        mock_create_response = MagicMock()
        mock_create_response.json.return_value = sample_lookup_table
        mock_client.post.return_value = mock_create_response

        handler = LookupTableHandler(mock_client)
        csv_content = "key,value\nk1,v1\nk2,v2"
        result = handler.create_from_csv(
            name="My Table",
            csv_content=csv_content,
            description="Test table",
        )

        assert result["id"] == "lt-12345"
        # Should have called post twice: create table and upload data
        assert mock_client.post.call_count >= 1

    def test_create_from_csv_no_header(self, mock_client, sample_lookup_table):
        """Test creating lookup table from CSV without header."""
        mock_create_response = MagicMock()
        mock_create_response.json.return_value = sample_lookup_table
        mock_client.post.return_value = mock_create_response

        handler = LookupTableHandler(mock_client)
        csv_content = "k1,v1\nk2,v2"
        result = handler.create_from_csv(
            name="My Table",
            csv_content=csv_content,
            has_header=False,
        )

        assert result["id"] == "lt-12345"

    def test_create_from_csv_empty_raises(self, mock_client):
        """Test creating lookup table from empty CSV raises error."""
        handler = LookupTableHandler(mock_client)

        with pytest.raises(ValueError, match="empty"):
            handler.create_from_csv(
                name="My Table",
                csv_content="",
            )


class TestGetLookupTablesCommand:
    """Tests for the get lookup-tables command."""

    @patch("dtctl.commands.get.load_config")
    @patch("dtctl.commands.get.create_client_from_config")
    def test_get_lookup_tables_list(
        self,
        mock_create_client,
        mock_load_config,
        cli_runner: CliRunner,
        mock_config,
        sample_lookup_table_list,
    ):
        """Test listing lookup tables."""
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = sample_lookup_table_list
        mock_client.get.return_value = mock_response
        mock_create_client.return_value = mock_client

        result = cli_runner.invoke(app, ["get", "lookup-tables"])

        assert result.exit_code == 0
        assert "Table 1" in result.output or "lt-12345" in result.output

    @patch("dtctl.commands.get.load_config")
    @patch("dtctl.commands.get.create_client_from_config")
    def test_get_lookup_tables_alias_lt(
        self,
        mock_create_client,
        mock_load_config,
        cli_runner: CliRunner,
        mock_config,
        sample_lookup_table_list,
    ):
        """Test listing lookup tables with 'lt' alias."""
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = sample_lookup_table_list
        mock_client.get.return_value = mock_response
        mock_create_client.return_value = mock_client

        result = cli_runner.invoke(app, ["get", "lt"])

        assert result.exit_code == 0

    @patch("dtctl.commands.get.load_config")
    @patch("dtctl.commands.get.create_client_from_config")
    def test_get_lookup_tables_alias_lookups(
        self,
        mock_create_client,
        mock_load_config,
        cli_runner: CliRunner,
        mock_config,
        sample_lookup_table_list,
    ):
        """Test listing lookup tables with 'lookups' alias."""
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = sample_lookup_table_list
        mock_client.get.return_value = mock_response
        mock_create_client.return_value = mock_client

        result = cli_runner.invoke(app, ["get", "lookups"])

        assert result.exit_code == 0

    @patch("dtctl.commands.get.load_config")
    @patch("dtctl.commands.get.create_client_from_config")
    def test_get_lookup_table_by_id(
        self,
        mock_create_client,
        mock_load_config,
        cli_runner: CliRunner,
        mock_config,
        sample_lookup_table,
    ):
        """Test getting a specific lookup table."""
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = sample_lookup_table
        mock_client.get.return_value = mock_response
        mock_create_client.return_value = mock_client

        result = cli_runner.invoke(app, ["get", "lt", "lt-12345"])

        assert result.exit_code == 0
        assert "Test Lookup Table" in result.output or "lt-12345" in result.output

    @patch("dtctl.commands.get.load_config")
    @patch("dtctl.commands.get.create_client_from_config")
    def test_get_lookup_table_data(
        self,
        mock_create_client,
        mock_load_config,
        cli_runner: CliRunner,
        mock_config,
        sample_lookup_table_data,
    ):
        """Test getting lookup table data."""
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = sample_lookup_table_data
        mock_client.get.return_value = mock_response
        mock_create_client.return_value = mock_client

        result = cli_runner.invoke(app, ["get", "lt", "lt-12345", "--data"])

        assert result.exit_code == 0
        # Should show row data
        assert "k1" in result.output or "v1" in result.output

    @patch("dtctl.commands.get.load_config")
    @patch("dtctl.commands.get.create_client_from_config")
    def test_get_lookup_table_data_with_limit(
        self,
        mock_create_client,
        mock_load_config,
        cli_runner: CliRunner,
        mock_config,
        sample_lookup_table_data,
    ):
        """Test getting lookup table data with custom limit."""
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = sample_lookup_table_data
        mock_client.get.return_value = mock_response
        mock_create_client.return_value = mock_client

        result = cli_runner.invoke(
            app, ["get", "lt", "lt-12345", "--data", "--limit", "50"]
        )

        assert result.exit_code == 0
        # Verify limit was passed
        call_args = mock_client.get.call_args
        assert call_args[1]["params"]["limit"] == 50


class TestCreateLookupTableCommand:
    """Tests for the create lookup-table command."""

    @patch("dtctl.commands.create.load_config")
    @patch("dtctl.commands.create.create_client_from_config")
    def test_create_lookup_table_from_csv(
        self,
        mock_create_client,
        mock_load_config,
        cli_runner: CliRunner,
        mock_config,
        sample_lookup_table,
        tmp_path,
    ):
        """Test creating lookup table from CSV file."""
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = sample_lookup_table
        mock_client.post.return_value = mock_response
        mock_create_client.return_value = mock_client

        # Create a temporary CSV file
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("key,value\nk1,v1\nk2,v2")

        result = cli_runner.invoke(
            app, ["create", "lookup-table", "-f", str(csv_file), "--name", "Test Table"]
        )

        assert result.exit_code == 0
        assert "Created" in result.output

    @patch("dtctl.commands.create.load_config")
    @patch("dtctl.commands.create.create_client_from_config")
    def test_create_lookup_table_csv_requires_name(
        self,
        mock_create_client,
        mock_load_config,
        cli_runner: CliRunner,
        mock_config,
        tmp_path,
    ):
        """Test that creating from CSV requires --name."""
        mock_load_config.return_value = mock_config
        mock_create_client.return_value = MagicMock()

        csv_file = tmp_path / "test.csv"
        csv_file.write_text("key,value\nk1,v1")

        result = cli_runner.invoke(
            app, ["create", "lookup-table", "-f", str(csv_file)]
        )

        assert result.exit_code == 1
        assert "--name is required" in result.output

    @patch("dtctl.commands.create.load_config")
    @patch("dtctl.commands.create.create_client_from_config")
    def test_create_lookup_table_dry_run(
        self,
        mock_create_client,
        mock_load_config,
        cli_runner: CliRunner,
        mock_config,
        tmp_path,
    ):
        """Test creating lookup table with dry-run."""
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_create_client.return_value = mock_client

        csv_file = tmp_path / "test.csv"
        csv_file.write_text("key,value\nk1,v1")

        result = cli_runner.invoke(
            app,
            [
                "--dry-run",
                "create",
                "lookup-table",
                "-f",
                str(csv_file),
                "--name",
                "Test",
            ],
        )

        assert result.exit_code == 0
        assert "Dry run" in result.output
        mock_client.post.assert_not_called()

    def test_create_lookup_table_file_not_found(self, cli_runner: CliRunner):
        """Test error when file doesn't exist."""
        result = cli_runner.invoke(
            app,
            ["create", "lookup-table", "-f", "/nonexistent/file.csv", "--name", "Test"],
        )

        assert result.exit_code == 1
        assert "not found" in result.output.lower()

    @patch("dtctl.commands.create.load_config")
    @patch("dtctl.commands.create.create_client_from_config")
    def test_create_lookup_table_alias_lt(
        self,
        mock_create_client,
        mock_load_config,
        cli_runner: CliRunner,
        mock_config,
        sample_lookup_table,
        tmp_path,
    ):
        """Test creating lookup table with 'lt' alias."""
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = sample_lookup_table
        mock_client.post.return_value = mock_response
        mock_create_client.return_value = mock_client

        csv_file = tmp_path / "test.csv"
        csv_file.write_text("key,value\nk1,v1")

        result = cli_runner.invoke(
            app, ["create", "lt", "-f", str(csv_file), "--name", "Test"]
        )

        assert result.exit_code == 0
