"""Logs command for viewing execution logs."""

from __future__ import annotations

import typer
from rich.console import Console

from dtctl.client import create_client_from_config
from dtctl.config import load_config

app = typer.Typer(invoke_without_command=True)
console = Console()


def get_context() -> str | None:
    """Get context override from CLI state."""
    from dtctl.cli import state

    return state.context


def is_verbose() -> bool:
    """Check if verbose mode is enabled."""
    from dtctl.cli import state

    return state.verbose


@app.callback(invoke_without_command=True)
def get_logs(
    ctx: typer.Context,
    execution_id: str = typer.Argument(..., help="Execution ID"),
    follow: bool = typer.Option(False, "--follow", "-f", help="Follow log output"),
    tail: int | None = typer.Option(None, "--tail", "-n", help="Number of lines to show"),
) -> None:
    """View execution logs.

    Examples:
        dtctl logs <execution-id>
        dtctl logs <execution-id> --tail 50
    """
    if ctx.invoked_subcommand is not None:
        return

    from dtctl.resources.workflow import ExecutionHandler

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = ExecutionHandler(client)

    logs = handler.get_logs(execution_id)

    if tail:
        lines = logs.split("\n")
        logs = "\n".join(lines[-tail:])

    console.print(logs)
