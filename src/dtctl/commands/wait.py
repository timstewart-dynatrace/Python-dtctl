"""Wait command for polling DQL queries until conditions are met."""

from __future__ import annotations

import time
from enum import Enum
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from dtctl.client import create_client_from_config
from dtctl.config import load_config
from dtctl.output import OutputFormat, Printer
from dtctl.utils.template import parse_set_values, render_template

app = typer.Typer(invoke_without_command=True)
console = Console()


class WaitCondition(str, Enum):
    """Conditions that can be evaluated against query results."""

    COUNT_EQ = "count"  # count equals N
    COUNT_GTE = "count-gte"  # count >= N
    COUNT_GT = "count-gt"  # count > N
    COUNT_LTE = "count-lte"  # count <= N
    COUNT_LT = "count-lt"  # count < N
    ANY = "any"  # at least one record
    NONE = "none"  # no records


# Exit codes matching the Go implementation
EXIT_SUCCESS = 0
EXIT_TIMEOUT = 1
EXIT_MAX_ATTEMPTS = 2
EXIT_ERROR = 3


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


def evaluate_condition(
    records: list,
    condition: WaitCondition,
    target_count: int,
) -> bool:
    """Evaluate a condition against query results.

    Args:
        records: List of query result records
        condition: The condition to evaluate
        target_count: Target count for count-based conditions

    Returns:
        True if condition is met
    """
    count = len(records)

    if condition == WaitCondition.COUNT_EQ:
        return count == target_count
    elif condition == WaitCondition.COUNT_GTE:
        return count >= target_count
    elif condition == WaitCondition.COUNT_GT:
        return count > target_count
    elif condition == WaitCondition.COUNT_LTE:
        return count <= target_count
    elif condition == WaitCondition.COUNT_LT:
        return count < target_count
    elif condition == WaitCondition.ANY:
        return count > 0
    elif condition == WaitCondition.NONE:
        return count == 0

    return False


@app.callback(invoke_without_command=True)
def wait_for_condition(
    ctx: typer.Context,
    query: Optional[str] = typer.Argument(None, help="DQL query string"),
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="Path to DQL query file"),
    set_values: Optional[list[str]] = typer.Option(
        None, "--set", help="Set template variables (key=value)"
    ),
    condition: WaitCondition = typer.Option(
        WaitCondition.ANY,
        "--condition",
        "-c",
        help="Condition to wait for",
    ),
    target_count: int = typer.Option(
        1,
        "--count",
        "-n",
        help="Target count for count-based conditions",
    ),
    timeout: int = typer.Option(
        300,
        "--timeout",
        "-t",
        help="Maximum wait time in seconds",
    ),
    interval: float = typer.Option(
        10.0,
        "--interval",
        "-i",
        help="Polling interval in seconds",
    ),
    max_attempts: int = typer.Option(
        0,
        "--max-attempts",
        help="Maximum number of attempts (0 for unlimited)",
    ),
    backoff: float = typer.Option(
        1.0,
        "--backoff",
        help="Exponential backoff multiplier (1.0 = no backoff)",
    ),
    max_interval: float = typer.Option(
        60.0,
        "--max-interval",
        help="Maximum interval when using backoff",
    ),
    query_timeout: int = typer.Option(
        60000,
        "--query-timeout",
        help="Query timeout in milliseconds",
    ),
    query_limit: int = typer.Option(
        1000,
        "--query-limit",
        help="Maximum number of records per query",
    ),
    output: Optional[OutputFormat] = typer.Option(None, "-o", "--output"),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Suppress progress output, only show final result",
    ),
) -> None:
    """Wait for a DQL query to match a condition.

    Repeatedly executes a DQL query until the specified condition is met,
    a timeout is reached, or the maximum number of attempts is exceeded.

    Exit codes:
        0 - Condition met successfully
        1 - Timeout reached
        2 - Maximum attempts exceeded
        3 - Error executing query

    Examples:
        # Wait for at least one log entry matching a filter
        dtctl wait "fetch logs | filter status == 500 | limit 1" --condition any

        # Wait for exactly 5 records
        dtctl wait "fetch metrics | summarize count()" --condition count --count 5

        # Wait with custom timeout and interval
        dtctl wait -f query.dql --timeout 600 --interval 30

        # Wait with exponential backoff
        dtctl wait "fetch events" --backoff 1.5 --max-interval 120
    """
    if ctx.invoked_subcommand is not None:
        return

    # Get query from argument or file
    if file:
        if not file.exists():
            console.print(f"[red]Error:[/red] File not found: {file}")
            raise typer.Exit(EXIT_ERROR)
        query_str = file.read_text()
    elif query:
        query_str = query
    else:
        console.print("[red]Error:[/red] Either query argument or --file is required")
        raise typer.Exit(EXIT_ERROR)

    # Apply template variables
    if set_values:
        variables = parse_set_values(set_values)
        query_str = render_template(query_str, variables)

    if is_verbose():
        console.print(f"[dim]Query:[/dim] {query_str}")
        console.print(f"[dim]Condition:[/dim] {condition.value}")
        if condition in (
            WaitCondition.COUNT_EQ,
            WaitCondition.COUNT_GTE,
            WaitCondition.COUNT_GT,
            WaitCondition.COUNT_LTE,
            WaitCondition.COUNT_LT,
        ):
            console.print(f"[dim]Target count:[/dim] {target_count}")
        console.print(f"[dim]Timeout:[/dim] {timeout}s")
        console.print(f"[dim]Interval:[/dim] {interval}s")

    from dtctl.resources.query import QueryHandler

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = QueryHandler(client)

    start_time = time.time()
    attempt = 0
    current_interval = interval

    while True:
        attempt += 1
        elapsed = time.time() - start_time

        # Check timeout
        if elapsed >= timeout:
            if not quiet:
                console.print(f"[yellow]Timeout:[/yellow] Condition not met within {timeout}s")
            raise typer.Exit(EXIT_TIMEOUT)

        # Check max attempts
        if max_attempts > 0 and attempt > max_attempts:
            if not quiet:
                console.print(
                    f"[yellow]Max attempts:[/yellow] Condition not met after {max_attempts} attempts"
                )
            raise typer.Exit(EXIT_MAX_ATTEMPTS)

        if not quiet and not is_plain_mode():
            console.print(
                f"[dim]Attempt {attempt}: Executing query... "
                f"(elapsed: {elapsed:.0f}s/{timeout}s)[/dim]"
            )

        try:
            result = handler.execute(
                query=query_str,
                timeout_ms=query_timeout,
                max_result_records=query_limit,
            )
        except Exception as e:
            console.print(f"[red]Error executing query:[/red] {e}")
            raise typer.Exit(EXIT_ERROR)

        # Check for query errors
        state_value = result.get("state", "")
        if state_value == "FAILED":
            error = result.get("error", {})
            message = error.get("message", "Unknown error")
            console.print(f"[red]Query failed:[/red] {message}")
            raise typer.Exit(EXIT_ERROR)

        # Extract records
        records = result.get("result", {}).get("records", [])
        record_count = len(records)

        if not quiet and not is_plain_mode():
            console.print(f"[dim]  Found {record_count} records[/dim]")

        # Evaluate condition
        if evaluate_condition(records, condition, target_count):
            if not quiet:
                console.print(
                    f"[green]Success:[/green] Condition '{condition.value}' met "
                    f"after {attempt} attempt(s) ({elapsed:.1f}s)"
                )

            # Output final results
            fmt = output or get_output_format()
            printer = Printer(format=fmt, plain=is_plain_mode())

            if fmt in (OutputFormat.JSON, OutputFormat.YAML):
                printer.print(result)
            elif records:
                printer.print(records)

            raise typer.Exit(EXIT_SUCCESS)

        # Calculate next interval with backoff
        if backoff > 1.0:
            current_interval = min(current_interval * backoff, max_interval)

        # Wait before next attempt (but not longer than remaining timeout)
        remaining = timeout - (time.time() - start_time)
        sleep_time = min(current_interval, remaining)

        if sleep_time > 0:
            if not quiet and not is_plain_mode():
                console.print(f"[dim]  Waiting {sleep_time:.1f}s before next attempt...[/dim]")
            time.sleep(sleep_time)
