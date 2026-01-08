"""Describe command for showing detailed resource information."""

from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from dtctl.client import create_client_from_config
from dtctl.config import load_config
from dtctl.output import Printer, OutputFormat

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


@app.command("workflow")
@app.command("wf")
def describe_workflow(
    identifier: str = typer.Argument(..., help="Workflow ID or name"),
    output: Optional[OutputFormat] = typer.Option(None, "-o", "--output"),
) -> None:
    """Show detailed workflow information."""
    from dtctl.resources.workflow import WorkflowHandler
    from dtctl.utils.resolver import ResourceResolver

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = WorkflowHandler(client)
    resolver = ResourceResolver(client)

    workflow_id = resolver.resolve_workflow(identifier)
    workflow = handler.get(workflow_id)

    fmt = output or get_output_format()
    if fmt in (OutputFormat.JSON, OutputFormat.YAML):
        printer = Printer(format=fmt, plain=is_plain_mode())
        printer.print(workflow)
        return

    # Rich formatted output
    console.print(Panel(f"[bold]Workflow: {workflow.get('title', 'N/A')}[/bold]"))
    console.print(f"ID: {workflow.get('id', 'N/A')}")
    console.print(f"Owner: {workflow.get('owner', 'N/A')}")
    console.print(f"Description: {workflow.get('description', 'N/A')}")
    console.print(f"Deployed: {'Yes' if workflow.get('isDeployed') else 'No'}")
    console.print(f"Private: {'Yes' if workflow.get('isPrivate') else 'No'}")

    # Show tasks
    tasks = workflow.get("tasks", {})
    if tasks:
        console.print("\n[bold]Tasks:[/bold]")
        table = Table(show_header=True)
        table.add_column("Name")
        table.add_column("Action")
        table.add_column("Position")
        for name, task in tasks.items():
            action = task.get("action", "N/A")
            position = f"({task.get('position', {}).get('x', 0)}, {task.get('position', {}).get('y', 0)})"
            table.add_row(name, action, position)
        console.print(table)

    # Show trigger
    trigger = workflow.get("trigger", {})
    if trigger:
        console.print(f"\n[bold]Trigger:[/bold] {trigger.get('type', 'None')}")


@app.command("execution")
@app.command("workflow-execution")
def describe_execution(
    execution_id: str = typer.Argument(..., help="Execution ID"),
    output: Optional[OutputFormat] = typer.Option(None, "-o", "--output"),
) -> None:
    """Show detailed execution information including task states."""
    from dtctl.resources.workflow import ExecutionHandler

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = ExecutionHandler(client)

    execution = handler.get_execution(execution_id)
    tasks = handler.get_task_executions(execution_id)

    fmt = output or get_output_format()
    if fmt in (OutputFormat.JSON, OutputFormat.YAML):
        printer = Printer(format=fmt, plain=is_plain_mode())
        printer.print({"execution": execution, "tasks": tasks})
        return

    # Rich formatted output
    console.print(Panel(f"[bold]Execution: {execution_id}[/bold]"))
    console.print(f"Workflow: {execution.get('workflow', 'N/A')}")
    console.print(f"Title: {execution.get('title', 'N/A')}")
    console.print(f"State: {execution.get('state', 'N/A')}")
    console.print(f"Started: {execution.get('startedAt', 'N/A')}")
    console.print(f"Ended: {execution.get('endedAt', 'N/A')}")
    console.print(f"Runtime: {execution.get('runtime', 'N/A')}")
    console.print(f"Trigger: {execution.get('triggerType', 'N/A')}")

    if tasks:
        console.print("\n[bold]Task Executions:[/bold]")
        table = Table(show_header=True)
        table.add_column("Task")
        table.add_column("State")
        table.add_column("Started")
        table.add_column("Duration")
        for task in tasks:
            table.add_row(
                task.get("name", "N/A"),
                task.get("state", "N/A"),
                str(task.get("startedAt", "N/A")),
                task.get("duration", "N/A"),
            )
        console.print(table)


@app.command("dashboard")
@app.command("dash")
def describe_dashboard(
    identifier: str = typer.Argument(..., help="Dashboard ID or name"),
    output: Optional[OutputFormat] = typer.Option(None, "-o", "--output"),
) -> None:
    """Show detailed dashboard information."""
    from dtctl.resources.document import create_dashboard_handler
    from dtctl.utils.resolver import ResourceResolver

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = create_dashboard_handler(client)
    resolver = ResourceResolver(client)

    doc_id = resolver.resolve_document(identifier, "dashboard")
    document = handler.get(doc_id)

    fmt = output or get_output_format()
    if fmt in (OutputFormat.JSON, OutputFormat.YAML):
        printer = Printer(format=fmt, plain=is_plain_mode())
        printer.print(document)
        return

    console.print(Panel(f"[bold]Dashboard: {document.get('name', 'N/A')}[/bold]"))
    console.print(f"ID: {document.get('id', 'N/A')}")
    console.print(f"Owner: {document.get('owner', 'N/A')}")
    console.print(f"Version: {document.get('version', 'N/A')}")
    console.print(f"Private: {'Yes' if document.get('isPrivate') else 'No'}")


@app.command("notebook")
@app.command("nb")
def describe_notebook(
    identifier: str = typer.Argument(..., help="Notebook ID or name"),
    output: Optional[OutputFormat] = typer.Option(None, "-o", "--output"),
) -> None:
    """Show detailed notebook information."""
    from dtctl.resources.document import create_notebook_handler
    from dtctl.utils.resolver import ResourceResolver

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = create_notebook_handler(client)
    resolver = ResourceResolver(client)

    doc_id = resolver.resolve_document(identifier, "notebook")
    document = handler.get(doc_id)

    fmt = output or get_output_format()
    if fmt in (OutputFormat.JSON, OutputFormat.YAML):
        printer = Printer(format=fmt, plain=is_plain_mode())
        printer.print(document)
        return

    console.print(Panel(f"[bold]Notebook: {document.get('name', 'N/A')}[/bold]"))
    console.print(f"ID: {document.get('id', 'N/A')}")
    console.print(f"Owner: {document.get('owner', 'N/A')}")
    console.print(f"Version: {document.get('version', 'N/A')}")
    console.print(f"Private: {'Yes' if document.get('isPrivate') else 'No'}")


@app.command("slo")
def describe_slo(
    identifier: str = typer.Argument(..., help="SLO ID or name"),
    output: Optional[OutputFormat] = typer.Option(None, "-o", "--output"),
) -> None:
    """Show detailed SLO information."""
    from dtctl.resources.slo import SLOHandler
    from dtctl.utils.resolver import ResourceResolver

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = SLOHandler(client)
    resolver = ResourceResolver(client)

    slo_id = resolver.resolve_slo(identifier)
    slo = handler.get(slo_id)

    fmt = output or get_output_format()
    if fmt in (OutputFormat.JSON, OutputFormat.YAML):
        printer = Printer(format=fmt, plain=is_plain_mode())
        printer.print(slo)
        return

    console.print(Panel(f"[bold]SLO: {slo.get('name', 'N/A')}[/bold]"))
    console.print(f"ID: {slo.get('id', 'N/A')}")
    console.print(f"Status: {slo.get('status', 'N/A')}")
    console.print(f"Target: {slo.get('target', 'N/A')}%")
    console.print(f"Warning: {slo.get('warning', 'N/A')}%")
    console.print(f"Current: {slo.get('evaluatedPercentage', 'N/A'):.2f}%")
    console.print(f"Error Budget: {slo.get('errorBudget', 'N/A'):.2f}%")
    console.print(f"Enabled: {'Yes' if slo.get('enabled') else 'No'}")


@app.command("settings")
def describe_settings(
    object_id: str = typer.Argument(..., help="Settings object ID"),
    output: Optional[OutputFormat] = typer.Option(None, "-o", "--output"),
) -> None:
    """Show detailed settings object information."""
    from dtctl.resources.settings import SettingsHandler

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = SettingsHandler(client)

    settings = handler.get_object(object_id)

    fmt = output or get_output_format()
    printer = Printer(format=fmt, plain=is_plain_mode())
    printer.print(settings)


@app.command("analyzer")
def describe_analyzer(
    analyzer_name: str = typer.Argument(..., help="Analyzer name"),
    output: Optional[OutputFormat] = typer.Option(None, "-o", "--output"),
) -> None:
    """Show detailed analyzer information."""
    from dtctl.resources.analyzer import AnalyzerHandler

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = AnalyzerHandler(client)

    analyzer = handler.get(analyzer_name)

    fmt = output or get_output_format()
    printer = Printer(format=fmt, plain=is_plain_mode())
    printer.print(analyzer)
