# Code Style Guidelines

## Python Style

- **Type hints on all functions** - Required for all function parameters and return types
- **Docstrings for public APIs** - All public functions, classes, and methods must have docstrings
- Use `from __future__ import annotations` for forward references
- Follow PEP 8 with **100 character line limit**
- Use **Ruff** for linting and formatting

## Formatting Commands

```bash
ruff format src/
ruff check src/ --fix
```

## Adding New Resources

1. Create handler in `src/dtctl/resources/<resource>.py`:
```python
from dtctl.resources.base import CRUDHandler

class MyResourceHandler(CRUDHandler):
    @property
    def resource_name(self) -> str:
        return "myresource"

    @property
    def api_path(self) -> str:
        return "/platform/api/v1/myresources"
```

2. Add commands in `src/dtctl/commands/get.py`, `delete.py`, etc.

3. Define columns in `src/dtctl/output.py` for table output.

## Adding New Commands

1. Create command module in `src/dtctl/commands/<command>.py`
2. Register in `src/dtctl/cli.py` with `app.add_typer()`
3. Use helper functions for shared state access:
   - `get_context()` - context override
   - `get_output_format()` - output format
   - `is_verbose()` - verbose mode
   - `is_plain_mode()` - plain mode
   - `is_dry_run()` - dry-run mode

## Resource Naming

Follow kubectl conventions:
- Singular resource names in commands
- Abbreviations/aliases (e.g., `wf` for `workflow`, `dash` for `dashboard`)
- Use `@app.command()` decorator multiple times for aliases

## Error Handling

- Use `typer.Exit(1)` for errors
- Print errors with `[red]Error:[/red]` prefix using Rich
- Provide actionable error messages
- Include API error details when relevant
