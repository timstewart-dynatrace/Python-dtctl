"""Auth command for authentication-related operations."""

from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from dtctl.client import create_client_from_config
from dtctl.config import load_config
from dtctl.output import OutputFormat, Printer

app = typer.Typer()
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


@app.command("whoami")
def whoami(
    output: Optional[OutputFormat] = typer.Option(None, "-o", "--output"),
) -> None:
    """Display current user identity.

    Shows information about the currently authenticated user based on
    the active context's credentials.

    Examples:
        dtctl auth whoami
        dtctl auth whoami -o json
    """
    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())

    # Get current context info
    context_name = get_context() or config.current_context
    ctx = config.get_context(context_name) if context_name else None

    if not ctx:
        console.print("[red]Error:[/red] No active context configured")
        raise typer.Exit(1)

    user_info: dict = {
        "context": context_name,
        "environment": ctx.environment,
        "authMethod": "oauth2" if ctx.uses_oauth else "bearer-token",
    }

    # Try to get user identity from the API
    try:
        # Try the IAM endpoint to get current user info
        # This endpoint returns info about the authenticated user
        response = client.get("/iam/v1/accounts/users/me")
        api_user = response.json()

        user_info["uid"] = api_user.get("uid", "")
        user_info["email"] = api_user.get("email", "")
        user_info["name"] = api_user.get("name", "")
        user_info["groups"] = api_user.get("groups", [])
    except Exception:
        # If /me endpoint doesn't work, try to infer from token or OAuth
        if is_verbose():
            console.print("[dim]Could not fetch user info from /me endpoint[/dim]")

        # For OAuth, we might have client info
        if ctx.uses_oauth:
            user_info["clientId"] = ctx.oauth_client_id
            user_info["resourceUrn"] = ctx.oauth_resource_urn or "(default)"

    fmt = output or get_output_format()
    printer = Printer(format=fmt, plain=is_plain_mode())

    if fmt in (OutputFormat.JSON, OutputFormat.YAML):
        printer.print(user_info)
    else:
        # Pretty table output
        table = Table(title="Current User Identity", show_header=False)
        table.add_column("Field", style="cyan")
        table.add_column("Value")

        table.add_row("Context", user_info.get("context", ""))
        table.add_row("Environment", user_info.get("environment", ""))
        table.add_row("Auth Method", user_info.get("authMethod", ""))

        if "uid" in user_info:
            table.add_row("User ID", user_info.get("uid", ""))
        if "email" in user_info:
            table.add_row("Email", user_info.get("email", ""))
        if "name" in user_info:
            table.add_row("Name", user_info.get("name", ""))
        if "groups" in user_info and user_info["groups"]:
            groups = ", ".join(user_info["groups"][:5])
            if len(user_info["groups"]) > 5:
                groups += f" (+{len(user_info['groups']) - 5} more)"
            table.add_row("Groups", groups)
        if "clientId" in user_info:
            table.add_row("Client ID", user_info.get("clientId", ""))
        if "resourceUrn" in user_info:
            table.add_row("Resource URN", user_info.get("resourceUrn", ""))

        console.print(table)


@app.command("test")
def test_auth(
    output: Optional[OutputFormat] = typer.Option(None, "-o", "--output"),
) -> None:
    """Test authentication to the current context.

    Attempts to make an API call to verify that the credentials
    are valid and working.

    Examples:
        dtctl auth test
    """
    config = load_config()

    context_name = get_context() or config.current_context
    ctx = config.get_context(context_name) if context_name else None

    if not ctx:
        console.print("[red]Error:[/red] No active context configured")
        raise typer.Exit(1)

    if not is_plain_mode():
        console.print(f"Testing authentication for context: [cyan]{context_name}[/cyan]")
        console.print(f"Environment: [dim]{ctx.environment}[/dim]")

    try:
        client = create_client_from_config(config, get_context(), is_verbose())

        # Try multiple endpoints to test authentication
        # Different tokens may have different permissions
        test_endpoints = [
            "/platform/classic/environment-api/v2/settings/schemas",  # Settings schemas
            "/platform/automation/v1/workflows",  # Workflows
            "/platform/document/v1/documents",  # Documents
            "/platform/consumption/v1/account-limits",  # Account limits
        ]

        authenticated = False
        last_error = None

        for endpoint in test_endpoints:
            try:
                response = client.get(endpoint)
                response.json()  # Ensure we can parse the response
                authenticated = True
                break
            except Exception as e:
                last_error = e
                # Try next endpoint
                continue

        if not authenticated:
            raise last_error or Exception("All test endpoints failed")

        result = {
            "status": "success",
            "context": context_name,
            "environment": ctx.environment,
            "message": "Authentication successful",
        }

        fmt = output or get_output_format()

        if fmt in (OutputFormat.JSON, OutputFormat.YAML):
            printer = Printer(format=fmt, plain=is_plain_mode())
            printer.print(result)
        else:
            console.print("[green]✓ Authentication successful[/green]")

    except Exception as e:
        result = {
            "status": "failed",
            "context": context_name,
            "environment": ctx.environment,
            "error": str(e),
        }

        fmt = output or get_output_format()

        if fmt in (OutputFormat.JSON, OutputFormat.YAML):
            printer = Printer(format=fmt, plain=is_plain_mode())
            printer.print(result)
        else:
            console.print(f"[red]✗ Authentication failed:[/red] {e}")

        raise typer.Exit(1)
