"""Create command for creating resources from manifests."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from dtctl.client import create_client_from_config
from dtctl.config import load_config
from dtctl.output import Printer, OutputFormat
from dtctl.utils.format import parse_content
from dtctl.utils.template import parse_set_values, render_dict

app = typer.Typer(no_args_is_help=True)
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


def is_dry_run() -> bool:
    """Check if dry-run mode is enabled."""
    from dtctl.cli import state
    return state.dry_run


@app.command("workflow")
@app.command("wf")
def create_workflow(
    file: Path = typer.Option(..., "--file", "-f", help="Path to workflow manifest"),
    set_values: Optional[list[str]] = typer.Option(None, "--set", help="Set template variables (key=value)"),
    output: Optional[OutputFormat] = typer.Option(None, "-o", "--output"),
) -> None:
    """Create a workflow from a manifest file."""
    from dtctl.resources.workflow import WorkflowHandler

    if not file.exists():
        console.print(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(1)

    content = file.read_text()
    data = parse_content(content)

    if set_values:
        variables = parse_set_values(set_values)
        data = render_dict(data, variables)

    if is_dry_run():
        console.print("[yellow]Dry run - would create workflow:[/yellow]")
        printer = Printer(format=OutputFormat.YAML, plain=is_plain_mode())
        printer.print(data)
        return

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = WorkflowHandler(client)

    result = handler.create(data)

    fmt = output or get_output_format()
    printer = Printer(format=fmt, plain=is_plain_mode())

    console.print(f"[green]Created workflow:[/green] {result.get('id')}")
    printer.print(result)


@app.command("dashboard")
@app.command("dash")
def create_dashboard(
    file: Path = typer.Option(..., "--file", "-f", help="Path to dashboard manifest"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Dashboard name"),
    private: bool = typer.Option(True, "--private/--public", help="Private or public"),
    output: Optional[OutputFormat] = typer.Option(None, "-o", "--output"),
) -> None:
    """Create a dashboard from a manifest file."""
    from dtctl.resources.document import create_dashboard_handler

    if not file.exists():
        console.print(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(1)

    content = file.read_text()
    data = parse_content(content)

    doc_name = name or data.get("name", file.stem)

    if is_dry_run():
        console.print(f"[yellow]Dry run - would create dashboard: {doc_name}[/yellow]")
        return

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = create_dashboard_handler(client)

    result = handler.create(
        name=doc_name,
        doc_type="dashboard",
        content=data,
        is_private=private,
    )

    fmt = output or get_output_format()
    printer = Printer(format=fmt, plain=is_plain_mode())

    console.print(f"[green]Created dashboard:[/green] {result.get('id')}")
    printer.print(result)


@app.command("notebook")
@app.command("nb")
def create_notebook(
    file: Path = typer.Option(..., "--file", "-f", help="Path to notebook manifest"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Notebook name"),
    private: bool = typer.Option(True, "--private/--public", help="Private or public"),
    output: Optional[OutputFormat] = typer.Option(None, "-o", "--output"),
) -> None:
    """Create a notebook from a manifest file."""
    from dtctl.resources.document import create_notebook_handler

    if not file.exists():
        console.print(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(1)

    content = file.read_text()
    data = parse_content(content)

    doc_name = name or data.get("name", file.stem)

    if is_dry_run():
        console.print(f"[yellow]Dry run - would create notebook: {doc_name}[/yellow]")
        return

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = create_notebook_handler(client)

    result = handler.create(
        name=doc_name,
        doc_type="notebook",
        content=data,
        is_private=private,
    )

    fmt = output or get_output_format()
    printer = Printer(format=fmt, plain=is_plain_mode())

    console.print(f"[green]Created notebook:[/green] {result.get('id')}")
    printer.print(result)


@app.command("slo")
def create_slo(
    file: Path = typer.Option(..., "--file", "-f", help="Path to SLO manifest"),
    set_values: Optional[list[str]] = typer.Option(None, "--set", help="Set template variables"),
    output: Optional[OutputFormat] = typer.Option(None, "-o", "--output"),
) -> None:
    """Create an SLO from a manifest file."""
    from dtctl.resources.slo import SLOHandler

    if not file.exists():
        console.print(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(1)

    content = file.read_text()
    data = parse_content(content)

    if set_values:
        variables = parse_set_values(set_values)
        data = render_dict(data, variables)

    if is_dry_run():
        console.print("[yellow]Dry run - would create SLO:[/yellow]")
        printer = Printer(format=OutputFormat.YAML, plain=is_plain_mode())
        printer.print(data)
        return

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = SLOHandler(client)

    result = handler.create(data)

    fmt = output or get_output_format()
    printer = Printer(format=fmt, plain=is_plain_mode())

    console.print(f"[green]Created SLO:[/green] {result.get('id')}")
    printer.print(result)


@app.command("settings")
def create_settings(
    file: Path = typer.Option(..., "--file", "-f", help="Path to settings manifest"),
    schema: str = typer.Option(..., "--schema", "-s", help="Settings schema ID"),
    scope: str = typer.Option("environment", "--scope", help="Settings scope"),
    output: Optional[OutputFormat] = typer.Option(None, "-o", "--output"),
) -> None:
    """Create a settings object from a manifest file."""
    from dtctl.resources.settings import SettingsHandler

    if not file.exists():
        console.print(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(1)

    content = file.read_text()
    data = parse_content(content)

    if is_dry_run():
        console.print("[yellow]Dry run - would create settings object:[/yellow]")
        console.print(f"Schema: {schema}")
        console.print(f"Scope: {scope}")
        printer = Printer(format=OutputFormat.YAML, plain=is_plain_mode())
        printer.print(data)
        return

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = SettingsHandler(client)

    result = handler.create_object(schema_id=schema, scope=scope, value=data)

    fmt = output or get_output_format()
    printer = Printer(format=fmt, plain=is_plain_mode())

    console.print(f"[green]Created settings object:[/green] {result.get('objectId')}")
    printer.print(result)


@app.command("bucket")
def create_bucket(
    file: Path = typer.Option(..., "--file", "-f", help="Path to bucket manifest"),
    output: Optional[OutputFormat] = typer.Option(None, "-o", "--output"),
) -> None:
    """Create a bucket from a manifest file."""
    from dtctl.resources.bucket import BucketHandler

    if not file.exists():
        console.print(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(1)

    content = file.read_text()
    data = parse_content(content)

    if is_dry_run():
        console.print("[yellow]Dry run - would create bucket:[/yellow]")
        printer = Printer(format=OutputFormat.YAML, plain=is_plain_mode())
        printer.print(data)
        return

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = BucketHandler(client)

    result = handler.create(data)

    fmt = output or get_output_format()
    printer = Printer(format=fmt, plain=is_plain_mode())

    console.print(f"[green]Created bucket:[/green] {result.get('bucketName')}")
    printer.print(result)


@app.command("edgeconnect")
@app.command("ec")
def create_edgeconnect(
    file: Path = typer.Option(..., "--file", "-f", help="Path to EdgeConnect manifest"),
    output: Optional[OutputFormat] = typer.Option(None, "-o", "--output"),
) -> None:
    """Create an EdgeConnect configuration from a manifest file."""
    from dtctl.resources.edgeconnect import EdgeConnectHandler

    if not file.exists():
        console.print(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(1)

    content = file.read_text()
    data = parse_content(content)

    if is_dry_run():
        console.print("[yellow]Dry run - would create EdgeConnect:[/yellow]")
        printer = Printer(format=OutputFormat.YAML, plain=is_plain_mode())
        printer.print(data)
        return

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = EdgeConnectHandler(client)

    result = handler.create(data)

    fmt = output or get_output_format()
    printer = Printer(format=fmt, plain=is_plain_mode())

    console.print(f"[green]Created EdgeConnect:[/green] {result.get('id')}")
    printer.print(result)


@app.command("lookup-table")
@app.command("lt")
def create_lookup_table(
    file: Path = typer.Option(..., "--file", "-f", help="Path to CSV file or JSON/YAML manifest"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Table name (required for CSV)"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="Table description"),
    delimiter: Optional[str] = typer.Option(None, "--delimiter", help="CSV delimiter (auto-detected if not specified)"),
    no_header: bool = typer.Option(False, "--no-header", help="CSV has no header row"),
    output: Optional[OutputFormat] = typer.Option(None, "-o", "--output"),
) -> None:
    """Create a lookup table from a CSV or manifest file.

    Lookup tables are used for data enrichment and mapping in DQL queries.

    Examples:
        # Create from CSV
        dtctl create lookup-table -f data.csv --name my-table

        # Create from CSV with custom delimiter
        dtctl create lt -f data.tsv --name my-table --delimiter $'\\t'

        # Create from JSON/YAML manifest
        dtctl create lt -f table-def.yaml
    """
    from dtctl.resources.lookup import LookupTableHandler

    if not file.exists():
        console.print(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(1)

    content = file.read_text()
    file_ext = file.suffix.lower()

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = LookupTableHandler(client)

    fmt = output or get_output_format()
    printer = Printer(format=fmt, plain=is_plain_mode())

    # Determine if CSV or manifest
    if file_ext == ".csv" or (delimiter is not None):
        # CSV mode
        if not name:
            console.print("[red]Error:[/red] --name is required when creating from CSV")
            raise typer.Exit(1)

        if is_dry_run():
            console.print(f"[yellow]Dry run - would create lookup table: {name}[/yellow]")
            console.print(f"  File: {file}")
            console.print(f"  Delimiter: {delimiter or '(auto-detect)'}")
            console.print(f"  Has header: {not no_header}")
            return

        result = handler.create_from_csv(
            name=name,
            csv_content=content,
            description=description or "",
            delimiter=delimiter,
            has_header=not no_header,
        )

        console.print(f"[green]Created lookup table:[/green] {result.get('id')}")
        printer.print(result)

    else:
        # JSON/YAML manifest mode
        data = parse_content(content)

        if is_dry_run():
            console.print("[yellow]Dry run - would create lookup table:[/yellow]")
            printer = Printer(format=OutputFormat.YAML, plain=is_plain_mode())
            printer.print(data)
            return

        result = handler.create(data)

        console.print(f"[green]Created lookup table:[/green] {result.get('id')}")
        printer.print(result)
