"""Template command for rendering and validating templates.

Provides commands to render templates with variables and validate template syntax.
"""

from __future__ import annotations

from pathlib import Path

import typer
import yaml
from rich.console import Console
from rich.syntax import Syntax

from dtctl.output import OutputFormat
from dtctl.utils.template import (
    parse_set_values,
    render_dict,
    render_template,
)

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


@app.command("render")
def render(
    file: Path = typer.Option(..., "--file", "-f", help="Template file to render"),
    set_values: list[str] = typer.Option([], "--set", "-s", help="Variable values (key=value)"),
    output_file: Path | None = typer.Option(
        None, "--output", "-o", help="Output file (default: stdout)"
    ),
    output_format: str | None = typer.Option(None, "--format", help="Output format (yaml, json)"),
) -> None:
    """Render a template file with variable substitution.

    Processes a YAML or JSON template file and replaces {{ variable }}
    placeholders with provided values.

    Examples:
        dtctl template render -f workflow.yaml --set name=my-workflow
        dtctl template render -f config.yaml --set env=prod --set region=us-east
        dtctl template render -f template.yaml --set name=test -o rendered.yaml
    """
    if not file.exists():
        console.print(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(1)

    # Read template file
    content = file.read_text()

    # Parse variables
    try:
        variables = parse_set_values(set_values)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from None

    # Determine if file is YAML or JSON
    try:
        if file.suffix in [".yaml", ".yml"]:
            data = yaml.safe_load(content)
            default_format = "yaml"
        else:
            import json

            data = json.loads(content)
            default_format = "json"
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to parse file: {e}")
        raise typer.Exit(1) from None

    # Render template
    try:
        if isinstance(data, dict):
            rendered = render_dict(data, variables)
        elif isinstance(data, list):
            from dtctl.utils.template import render_list

            rendered = render_list(data, variables)
        elif isinstance(data, str):
            rendered = render_template(data, variables)
        else:
            rendered = data
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from None

    # Format output
    fmt = output_format or default_format
    if fmt == "yaml":
        output = yaml.dump(rendered, default_flow_style=False, sort_keys=False)
    else:
        import json

        output = json.dumps(rendered, indent=2)

    # Write output
    if output_file:
        output_file.write_text(output)
        if not is_plain_mode():
            console.print(f"[green]Rendered template written to {output_file}[/green]")
    else:
        if is_plain_mode():
            print(output)
        else:
            syntax = Syntax(output, fmt, theme="monokai", line_numbers=True)
            console.print(syntax)


@app.command("validate")
def validate(
    file: Path = typer.Option(..., "--file", "-f", help="Template file to validate"),
) -> None:
    """Validate a template file's syntax.

    Checks if the template file is valid YAML/JSON and identifies
    all template variables that need to be provided.

    Examples:
        dtctl template validate -f workflow.yaml
        dtctl template validate -f config.json
    """
    import re

    if not file.exists():
        console.print(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(1)

    content = file.read_text()
    errors = []
    warnings = []

    # Check YAML/JSON syntax
    try:
        if file.suffix in [".yaml", ".yml"]:
            yaml.safe_load(content)
            file_type = "YAML"
        else:
            import json

            json.loads(content)
            file_type = "JSON"
    except yaml.YAMLError as e:
        errors.append(f"Invalid YAML syntax: {e}")
    except Exception as e:
        errors.append(f"Invalid JSON syntax: {e}")

    # Find all template variables
    variables = set(re.findall(r"\{\{\s*(\w+)", content))

    # Check for unclosed template tags
    open_tags = len(re.findall(r"\{\{", content))
    close_tags = len(re.findall(r"\}\}", content))
    if open_tags != close_tags:
        errors.append(f"Mismatched template tags: {open_tags} '{{{{' vs {close_tags} '}}}}'")

    # Check for common template issues
    for var in variables:
        # Check for missing default values on optional variables
        if "| default" not in content:
            if var.startswith("optional_"):
                warnings.append(f"Variable '{var}' appears optional but has no default value")

    # Print results
    if errors:
        console.print("[red]Validation failed:[/red]")
        for error in errors:
            console.print(f"  [red]✗[/red] {error}")
        raise typer.Exit(1)

    if is_plain_mode():
        print("valid: true")
        print(f"file_type: {file_type}")
        print(f"variables: {', '.join(sorted(variables)) if variables else 'none'}")
        return

    console.print(f"[green]✓[/green] Template is valid {file_type}")

    if variables:
        console.print(f"\n[bold]Required variables ({len(variables)}):[/bold]")
        for var in sorted(variables):
            console.print(f"  • {var}")
    else:
        console.print("\n[dim]No template variables found[/dim]")

    if warnings:
        console.print("\n[yellow]Warnings:[/yellow]")
        for warning in warnings:
            console.print(f"  [yellow]![/yellow] {warning}")


@app.command("variables")
def list_variables(
    file: Path = typer.Option(..., "--file", "-f", help="Template file to analyze"),
) -> None:
    """List all template variables in a file.

    Extracts and displays all {{ variable }} placeholders found
    in the template file.

    Examples:
        dtctl template variables -f workflow.yaml
    """
    import re

    if not file.exists():
        console.print(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(1)

    content = file.read_text()

    # Find all template variables with their full expressions
    full_expressions = re.findall(r"\{\{(.+?)\}\}", content)
    variable_names = set(re.findall(r"\{\{\s*(\w+)", content))

    if is_plain_mode():
        for var in sorted(variable_names):
            print(var)
        return

    if not variable_names:
        console.print("[dim]No template variables found[/dim]")
        return

    console.print(f"[bold]Template variables in {file.name}:[/bold]\n")

    for var in sorted(variable_names):
        # Find all expressions using this variable
        expressions = [e.strip() for e in full_expressions if var in e]
        has_default = any("default" in e for e in expressions)

        status = "[green]has default[/green]" if has_default else "[yellow]required[/yellow]"
        console.print(f"  • {var} ({status})")


@app.command("apply")
def apply_template(
    file: Path = typer.Option(..., "--file", "-f", help="Template file"),
    set_values: list[str] = typer.Option([], "--set", "-s", help="Variable values (key=value)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show rendered output without applying"),
) -> None:
    """Render a template and apply it to Dynatrace.

    Combines template rendering with the apply command, allowing
    you to create/update resources from templates in one step.

    Examples:
        dtctl template apply -f workflow.yaml --set name=my-workflow
        dtctl template apply -f config.yaml --set env=prod --dry-run
    """
    if not file.exists():
        console.print(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(1)

    # Read and parse template
    content = file.read_text()

    try:
        variables = parse_set_values(set_values)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from None

    # Parse YAML
    try:
        data = yaml.safe_load(content)
    except yaml.YAMLError as e:
        console.print(f"[red]Error:[/red] Failed to parse YAML: {e}")
        raise typer.Exit(1) from None

    # Render template
    try:
        if isinstance(data, dict):
            rendered = render_dict(data, variables)
        elif isinstance(data, list):
            from dtctl.utils.template import render_list

            rendered = render_list(data, variables)
        else:
            rendered = data
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from None

    if dry_run:
        console.print("[yellow]Dry run:[/yellow] Would apply:")
        output = yaml.dump(rendered, default_flow_style=False, sort_keys=False)
        syntax = Syntax(output, "yaml", theme="monokai")
        console.print(syntax)
        return

    # Import and use apply logic
    from dtctl.commands.apply import apply_manifest

    apply_manifest(rendered)
