"""Main CLI entry point for dtctl.

Provides the root command and registers all subcommands.
"""

from __future__ import annotations

import logging
import sys
from typing import Optional

import typer
from rich.console import Console

from dtctl import __version__
from dtctl.commands import config as config_cmd
from dtctl.commands import get as get_cmd
from dtctl.commands import describe as describe_cmd
from dtctl.commands import create as create_cmd
from dtctl.commands import delete as delete_cmd
from dtctl.commands import apply as apply_cmd
from dtctl.commands import edit as edit_cmd
from dtctl.commands import query as query_cmd
from dtctl.commands import execute as exec_cmd
from dtctl.commands import logs as logs_cmd
from dtctl.commands import share as share_cmd
from dtctl.output import OutputFormat

# Create console for rich output
console = Console()

# Create the main Typer app
app = typer.Typer(
    name="dtctl",
    help="""A kubectl-inspired CLI for managing Dynatrace platform resources.

[yellow]DISCLAIMER:[/yellow] This tool is NOT produced, endorsed, or supported by Dynatrace.
It is an independent, community-driven project. Use at your own risk.""",
    add_completion=True,
    no_args_is_help=True,
    rich_markup_mode="rich",
)

# Global state for shared options
class State:
    """Global state shared across commands."""

    def __init__(self) -> None:
        self.context: str | None = None
        self.output: OutputFormat = OutputFormat.TABLE
        self.verbose: bool = False
        self.plain: bool = False
        self.dry_run: bool = False


state = State()


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console.print(f"dtctl version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    ctx: typer.Context,
    context: Optional[str] = typer.Option(
        None,
        "--context",
        "-c",
        help="Override the current context",
        envvar="DTCTL_CONTEXT",
    ),
    output: OutputFormat = typer.Option(
        OutputFormat.TABLE,
        "--output",
        "-o",
        help="Output format",
        envvar="DTCTL_OUTPUT",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose/debug output",
        envvar="DTCTL_VERBOSE",
    ),
    plain: bool = typer.Option(
        False,
        "--plain",
        help="Plain output mode (no colors, no prompts)",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Preview changes without applying them",
    ),
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
) -> None:
    """dtctl - A kubectl-inspired CLI for managing Dynatrace platform resources.

    DISCLAIMER: This tool is NOT produced, endorsed, or supported by Dynatrace.
    It is an independent, community-driven project. Use at your own risk.

    Use 'dtctl <command> --help' for more information about a command.

    Examples:
        dtctl config set-context prod --environment https://abc.apps.dynatrace.com
        dtctl get workflows
        dtctl describe workflow my-workflow
        dtctl apply -f workflow.yaml
        dtctl query "fetch logs | limit 10"
    """
    # Store global options in state
    state.context = context
    state.output = output
    state.verbose = verbose
    state.plain = plain
    state.dry_run = dry_run

    # Configure logging
    if verbose:
        logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")
    else:
        logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")


# Register subcommands
app.add_typer(config_cmd.app, name="config", help="Manage configuration contexts and credentials")
app.add_typer(get_cmd.app, name="get", help="Get/list resources")
app.add_typer(describe_cmd.app, name="describe", help="Show detailed resource information")
app.add_typer(create_cmd.app, name="create", help="Create resources from manifests")
app.add_typer(delete_cmd.app, name="delete", help="Delete resources")
app.add_typer(apply_cmd.app, name="apply", help="Apply configuration from file (create or update)")
app.add_typer(edit_cmd.app, name="edit", help="Edit resources in your default editor")
app.add_typer(query_cmd.app, name="query", help="Execute DQL queries")
app.add_typer(exec_cmd.app, name="exec", help="Execute workflows, analyzers, or copilot")
app.add_typer(logs_cmd.app, name="logs", help="View execution logs")
app.add_typer(share_cmd.app, name="share", help="Share documents with users")


@app.command()
def unshare(
    resource_type: str = typer.Argument(..., help="Resource type (dashboard, notebook)"),
    identifier: str = typer.Argument(..., help="Resource ID or name"),
    user: Optional[str] = typer.Option(None, "--user", "-u", help="User SSO ID"),
    group: Optional[str] = typer.Option(None, "--group", "-g", help="Group UUID"),
) -> None:
    """Remove sharing from a document."""
    from dtctl.commands.share import unshare_document
    unshare_document(resource_type, identifier, user, group)


def main_cli() -> None:
    """Main entry point for the CLI."""
    try:
        app()
    except Exception as e:
        if state.verbose:
            console.print_exception()
        else:
            console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main_cli()
