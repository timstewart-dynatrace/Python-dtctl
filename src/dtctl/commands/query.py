"""Query command for executing DQL queries."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from dtctl.client import create_client_from_config
from dtctl.config import load_config
from dtctl.output import OutputFormat, Printer
from dtctl.utils.template import parse_set_values, render_template

app = typer.Typer(invoke_without_command=True)
console = Console()


def get_output_format() -> OutputFormat:
    """Get output format from CLI state."""
    from dtctl.cli import state

    return state.output


def is_plain_mode() -> bool:
    """Check if plain mode is enabled."""
    from dtctl.cli import state

    return state.plain


def get_context() -> str | None:
    """Get context override from CLI state."""
    from dtctl.cli import state

    return state.context


def is_verbose() -> bool:
    """Check if verbose mode is enabled."""
    from dtctl.cli import state

    return state.verbose


@app.callback(invoke_without_command=True)
def execute_query(
    ctx: typer.Context,
    query: str | None = typer.Argument(None, help="DQL query string"),
    file: Path | None = typer.Option(None, "--file", "-f", help="Path to DQL query file"),
    set_values: list[str] | None = typer.Option(
        None, "--set", help="Set template variables (key=value)"
    ),
    timeout: int = typer.Option(60000, "--timeout", "-t", help="Query timeout in milliseconds"),
    limit: int = typer.Option(1000, "--limit", "-l", help="Maximum number of records"),
    output: OutputFormat | None = typer.Option(None, "-o", "--output"),
) -> None:
    """Execute a DQL query.

    Examples:
        dtctl query "fetch logs | limit 10"
        dtctl query -f query.dql
        dtctl query "fetch logs | filter host == '{{ host }}'" --set host=my-host
    """
    if ctx.invoked_subcommand is not None:
        return

    # Get query from argument or file
    if file:
        if not file.exists():
            console.print(f"[red]Error:[/red] File not found: {file}")
            raise typer.Exit(1)
        query_str = file.read_text()
    elif query:
        query_str = query
    else:
        console.print("[red]Error:[/red] Either query argument or --file is required")
        raise typer.Exit(1)

    # Apply template variables
    if set_values:
        variables = parse_set_values(set_values)
        query_str = render_template(query_str, variables)

    if is_verbose():
        console.print(f"[dim]Query:[/dim] {query_str}")

    from dtctl.resources.query import QueryHandler

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = QueryHandler(client)

    try:
        result = handler.execute(
            query=query_str,
            timeout_ms=timeout,
            max_result_records=limit,
        )
    except TimeoutError as e:
        console.print(f"[red]Query timeout:[/red] {e}")
        raise typer.Exit(1) from None

    # Check for errors
    state = result.get("state", "")
    if state == "FAILED":
        error = result.get("error", {})
        message = error.get("message", "Unknown error")
        console.print(f"[red]Query failed:[/red] {message}")
        raise typer.Exit(1)

    # Extract records
    records = result.get("result", {}).get("records", [])
    metadata = result.get("result", {}).get("metadata", {})

    fmt = output or get_output_format()
    printer = Printer(format=fmt, plain=is_plain_mode())

    if fmt in (OutputFormat.JSON, OutputFormat.YAML):
        printer.print(result)
    else:
        # Table output - show records
        if records:
            printer.print(records)
        else:
            console.print("No records returned.")

        # Show metadata summary
        if not is_plain_mode() and metadata:
            total = metadata.get("totalCount", len(records))
            console.print(f"\n[dim]Total records: {total}[/dim]")
