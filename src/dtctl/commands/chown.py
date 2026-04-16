"""Change ownership commands for documents."""

from __future__ import annotations

import typer
from rich import print as rprint

from dtctl.client import APIError, create_client_from_config
from dtctl.config import load_config

app = typer.Typer(help="Change ownership of resources", no_args_is_help=True)


def get_context() -> str | None:
    """Get context from CLI state."""
    from dtctl.cli import state

    return state.context


def is_verbose() -> bool:
    """Check if verbose mode is enabled."""
    from dtctl.cli import state

    return state.verbose


def is_dry_run() -> bool:
    """Check if dry-run mode is enabled."""
    from dtctl.cli import state

    return state.dry_run


@app.command("dashboard")
@app.command("dash")
def chown_dashboard(
    identifier: str = typer.Argument(..., help="Dashboard ID or name"),
    new_owner: str = typer.Option(..., "--to", "-t", help="New owner user ID"),
    admin_access: bool = typer.Option(
        False, "--admin", "-a", help="Use admin access (requires document:documents:admin scope)"
    ),
) -> None:
    """Transfer ownership of a dashboard to another user.

    Warning: The current owner loses access after transfer.

    Examples:
        dtctl chown dashboard my-dashboard --to user@example.com
        dtctl chown dash abc123 --to user-id --admin
    """
    from dtctl.resources.document import create_dashboard_handler
    from dtctl.utils.resolver import ResourceResolver

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = create_dashboard_handler(client)
    resolver = ResourceResolver(client)

    # Resolve name to ID if needed
    doc_id = resolver.resolve_document(identifier, "dashboard")

    if is_dry_run():
        rprint(
            f"[yellow]Would transfer ownership of dashboard '{identifier}' to '{new_owner}'[/yellow]"
        )
        return

    try:
        success = handler.transfer_owner(doc_id, new_owner, admin_access=admin_access)
        if success:
            rprint(f"[green]✓[/green] Ownership transferred to '{new_owner}'")
            rprint("[dim]Note: Previous owner has lost access to this dashboard[/dim]")
        else:
            rprint("[red]✗[/red] Failed to transfer ownership")
            raise typer.Exit(1)
    except APIError as e:
        rprint(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from None


@app.command("notebook")
@app.command("nb")
def chown_notebook(
    identifier: str = typer.Argument(..., help="Notebook ID or name"),
    new_owner: str = typer.Option(..., "--to", "-t", help="New owner user ID"),
    admin_access: bool = typer.Option(
        False, "--admin", "-a", help="Use admin access (requires document:documents:admin scope)"
    ),
) -> None:
    """Transfer ownership of a notebook to another user.

    Warning: The current owner loses access after transfer.

    Examples:
        dtctl chown notebook my-notebook --to user@example.com
        dtctl chown nb abc123 --to user-id --admin
    """
    from dtctl.resources.document import create_notebook_handler
    from dtctl.utils.resolver import ResourceResolver

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = create_notebook_handler(client)
    resolver = ResourceResolver(client)

    # Resolve name to ID if needed
    doc_id = resolver.resolve_document(identifier, "notebook")

    if is_dry_run():
        rprint(
            f"[yellow]Would transfer ownership of notebook '{identifier}' to '{new_owner}'[/yellow]"
        )
        return

    try:
        success = handler.transfer_owner(doc_id, new_owner, admin_access=admin_access)
        if success:
            rprint(f"[green]✓[/green] Ownership transferred to '{new_owner}'")
            rprint("[dim]Note: Previous owner has lost access to this notebook[/dim]")
        else:
            rprint("[red]✗[/red] Failed to transfer ownership")
            raise typer.Exit(1)
    except APIError as e:
        rprint(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from None
