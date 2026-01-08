"""Configuration management commands.

Provides commands for managing contexts, tokens, and preferences.
"""

from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from dtctl.config import (
    Config,
    load_config,
    save_config,
    get_config_path,
)
from dtctl.output import Printer, OutputFormat

app = typer.Typer(no_args_is_help=True)
console = Console()


@app.command("view")
def view_config(
    output: OutputFormat = typer.Option(
        OutputFormat.YAML,
        "--output",
        "-o",
        help="Output format",
    ),
) -> None:
    """Display the current configuration."""
    config = load_config()
    printer = Printer(format=output)

    # Mask tokens for security
    data = config.model_dump(by_alias=True)
    for token in data.get("tokens", []):
        if token.get("token"):
            token["token"] = token["token"][:10] + "..." + token["token"][-4:]

    printer.print(data)


@app.command("get-contexts")
def get_contexts() -> None:
    """List all configured contexts."""
    config = load_config()

    if not config.contexts:
        console.print("No contexts configured.")
        console.print("Use 'dtctl config set-context <name>' to create one.")
        return

    table = Table(show_header=True, header_style="bold")
    table.add_column("CURRENT")
    table.add_column("NAME")
    table.add_column("ENVIRONMENT")
    table.add_column("TOKEN-REF")

    for ctx in config.contexts:
        current = "*" if ctx.name == config.current_context else ""
        table.add_row(
            current,
            ctx.name,
            ctx.context.environment,
            ctx.context.token_ref,
        )

    console.print(table)


@app.command("current-context")
def current_context() -> None:
    """Display the current context name."""
    config = load_config()

    if not config.current_context:
        console.print("No current context set.")
        console.print("Use 'dtctl config use-context <name>' to set one.")
        raise typer.Exit(1)

    console.print(config.current_context)


@app.command("use-context")
def use_context(
    name: str = typer.Argument(..., help="Context name to switch to"),
) -> None:
    """Switch to a different context."""
    config = load_config()

    if not config.get_context(name):
        console.print(f"[red]Error:[/red] Context '{name}' not found.")
        available = [ctx.name for ctx in config.contexts]
        if available:
            console.print(f"Available contexts: {', '.join(available)}")
        raise typer.Exit(1)

    config.current_context = name
    save_config(config)
    console.print(f"Switched to context '{name}'.")


@app.command("set-context")
def set_context(
    name: str = typer.Argument(..., help="Context name"),
    environment: Optional[str] = typer.Option(
        None,
        "--environment",
        "-e",
        help="Dynatrace environment URL",
    ),
    token_ref: Optional[str] = typer.Option(
        None,
        "--token-ref",
        "-t",
        help="Reference to a named token",
    ),
    set_current: bool = typer.Option(
        False,
        "--current",
        help="Set as current context",
    ),
) -> None:
    """Create or update a context.

    Examples:
        dtctl config set-context prod --environment https://abc.apps.dynatrace.com --token-ref prod-token
        dtctl config set-context dev -e https://dev.apps.dynatrace.com -t dev-token --current
    """
    config = load_config()

    existing = config.get_context(name)

    if not existing and (not environment or not token_ref):
        console.print("[red]Error:[/red] New context requires --environment and --token-ref")
        raise typer.Exit(1)

    try:
        config.set_context(name, environment, token_ref)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    if set_current:
        config.current_context = name

    save_config(config)

    action = "Updated" if existing else "Created"
    console.print(f"{action} context '{name}'.")
    if set_current:
        console.print(f"Switched to context '{name}'.")


@app.command("delete-context")
def delete_context(
    name: str = typer.Argument(..., help="Context name to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Delete a context."""
    config = load_config()

    if not config.get_context(name):
        console.print(f"[red]Error:[/red] Context '{name}' not found.")
        raise typer.Exit(1)

    if not force:
        confirm = typer.confirm(f"Delete context '{name}'?")
        if not confirm:
            console.print("Aborted.")
            raise typer.Exit(0)

    config.delete_context(name)
    save_config(config)
    console.print(f"Deleted context '{name}'.")


@app.command("set-credentials")
def set_credentials(
    name: str = typer.Argument(..., help="Token name"),
    token: Optional[str] = typer.Option(
        None,
        "--token",
        "-t",
        help="Dynatrace API token (will prompt if not provided)",
    ),
) -> None:
    """Store API credentials.

    Example:
        dtctl config set-credentials prod-token --token dt0s16.XXXX
        dtctl config set-credentials dev-token  # Will prompt for token
    """
    config = load_config()

    if not token:
        token = typer.prompt("Enter API token", hide_input=True)

    if not token:
        console.print("[red]Error:[/red] Token cannot be empty.")
        raise typer.Exit(1)

    # Validate token format
    if not token.startswith("dt0"):
        console.print(
            "[yellow]Warning:[/yellow] Token doesn't look like a Dynatrace token "
            "(expected format: dt0s16.XXX or dt0c01.XXX)"
        )

    config.set_token(name, token)
    save_config(config)
    console.print(f"Stored credentials as '{name}'.")


@app.command("delete-credentials")
def delete_credentials(
    name: str = typer.Argument(..., help="Token name to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Delete stored credentials."""
    config = load_config()

    if not config.get_token(name):
        console.print(f"[red]Error:[/red] Token '{name}' not found.")
        raise typer.Exit(1)

    if not force:
        confirm = typer.confirm(f"Delete token '{name}'?")
        if not confirm:
            console.print("Aborted.")
            raise typer.Exit(0)

    config.delete_token(name)
    save_config(config)
    console.print(f"Deleted token '{name}'.")


@app.command("path")
def config_path() -> None:
    """Display the configuration file path."""
    console.print(str(get_config_path()))
