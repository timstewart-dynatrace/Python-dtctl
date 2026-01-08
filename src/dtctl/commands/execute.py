"""Execute command for running workflows, analyzers, and copilot."""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Any

import typer
from rich.console import Console

from dtctl.client import create_client_from_config
from dtctl.config import load_config
from dtctl.output import Printer, OutputFormat
from dtctl.utils.format import parse_content
from dtctl.utils.template import parse_set_values

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
def execute_workflow(
    identifier: str = typer.Argument(..., help="Workflow ID or name"),
    params: Optional[list[str]] = typer.Option(
        None, "--param", "-p", help="Execution parameters (key=value)"
    ),
    wait: bool = typer.Option(False, "--wait", "-w", help="Wait for completion"),
    timeout: int = typer.Option(300, "--timeout", "-t", help="Wait timeout in seconds"),
    output: Optional[OutputFormat] = typer.Option(None, "-o", "--output"),
) -> None:
    """Execute a workflow.

    Examples:
        dtctl exec workflow my-workflow
        dtctl exec workflow my-workflow --param key=value --wait
    """
    from dtctl.resources.workflow import ExecutionHandler
    from dtctl.utils.resolver import ResourceResolver

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = ExecutionHandler(client)
    resolver = ResourceResolver(client)

    workflow_id = resolver.resolve_workflow(identifier)

    # Parse parameters
    exec_params: dict[str, Any] = {}
    if params:
        exec_params = parse_set_values(params)

    console.print(f"Executing workflow: {workflow_id}")
    result = handler.execute(workflow_id, exec_params if exec_params else None)

    execution_id = result.get("executionId") or result.get("id")
    console.print(f"Started execution: {execution_id}")

    if wait:
        console.print(f"Waiting for completion (timeout: {timeout}s)...")
        try:
            final_result = handler.wait_for_completion(
                execution_id, timeout=timeout
            )
            state = final_result.get("state", "UNKNOWN")
            if state == "SUCCESS":
                console.print(f"[green]Execution completed successfully[/green]")
            else:
                console.print(f"[yellow]Execution ended with state: {state}[/yellow]")
            result = final_result
        except TimeoutError:
            console.print(f"[yellow]Timeout waiting for completion[/yellow]")

    fmt = output or get_output_format()
    printer = Printer(format=fmt, plain=is_plain_mode())
    printer.print(result)


@app.command("analyzer")
def execute_analyzer(
    analyzer_name: str = typer.Argument(..., help="Analyzer name"),
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="Input data file"),
    data: Optional[str] = typer.Option(None, "--data", "-d", help="Input data as JSON string"),
    output: Optional[OutputFormat] = typer.Option(None, "-o", "--output"),
) -> None:
    """Execute a Davis analyzer.

    Examples:
        dtctl exec analyzer my-analyzer -f input.json
        dtctl exec analyzer my-analyzer -d '{"key": "value"}'
    """
    from dtctl.resources.analyzer import AnalyzerHandler

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = AnalyzerHandler(client)

    # Get input data
    if file:
        if not file.exists():
            console.print(f"[red]Error:[/red] File not found: {file}")
            raise typer.Exit(1)
        input_data = parse_content(file.read_text())
    elif data:
        input_data = parse_content(data)
    else:
        input_data = {}

    console.print(f"Executing analyzer: {analyzer_name}")
    result = handler.execute(analyzer_name, input_data)

    fmt = output or get_output_format()
    printer = Printer(format=fmt, plain=is_plain_mode())
    printer.print(result)


@app.command("copilot")
def execute_copilot(
    message: str = typer.Argument(..., help="Message to send to CoPilot"),
    output: Optional[OutputFormat] = typer.Option(None, "-o", "--output"),
) -> None:
    """Chat with Davis CoPilot.

    Examples:
        dtctl exec copilot "What are the top errors in the last hour?"
    """
    from dtctl.resources.copilot import CoPilotHandler

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = CoPilotHandler(client)

    result = handler.chat(message)

    fmt = output or get_output_format()

    if fmt in (OutputFormat.JSON, OutputFormat.YAML):
        printer = Printer(format=fmt, plain=is_plain_mode())
        printer.print(result)
    else:
        # Pretty print chat response
        response = result.get("response", result.get("message", "No response"))
        console.print(response)


@app.command("nl2dql")
def execute_nl2dql(
    question: str = typer.Argument(..., help="Natural language question"),
    output: Optional[OutputFormat] = typer.Option(None, "-o", "--output"),
) -> None:
    """Convert natural language to DQL query.

    Examples:
        dtctl exec nl2dql "Show me error logs from the last hour"
    """
    from dtctl.resources.copilot import CoPilotHandler

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = CoPilotHandler(client)

    result = handler.nl2dql(question)

    fmt = output or get_output_format()

    if fmt in (OutputFormat.JSON, OutputFormat.YAML):
        printer = Printer(format=fmt, plain=is_plain_mode())
        printer.print(result)
    else:
        # Show the generated query
        query = result.get("query", result.get("dql", "No query generated"))
        console.print("[bold]Generated DQL:[/bold]")
        console.print(query)
