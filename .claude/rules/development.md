# Development Guide

## Technology Stack

- **Language**: Python 3.10+
- **CLI Framework**: Typer (Click-based, type hints)
- **HTTP Client**: httpx (async-capable, modern)
- **Data Models**: Pydantic v2 (validation, serialization)
- **Output**: Rich (tables, formatting, colors)
- **Configuration**: PyYAML, platformdirs (XDG paths)
- **Templates**: Jinja2

## Setup

### Install for Development

```bash
# Development install
pip install -e .

# With dev dependencies (pytest, mypy, ruff)
pip install -e ".[dev]"
```

### Verify Installation

```bash
dtctl --help
dtctl --version
```

## Common Tasks

### Run CLI

```bash
dtctl --help
dtctl config view
dtctl get workflows
dtctl get limits
dtctl get environments
dtctl clone workflow my-wf --name "Copy"
dtctl template render -f manifest.yaml --set env=prod
```

### Format Code

```bash
ruff format src/
ruff check src/ --fix
```

### Run Tests

```bash
# All unit tests
pytest tests/ -v

# With coverage
pytest --cov=dtctl

# Exclude integration tests
pytest tests/ -v -m "not integration"

# Type checking
mypy src/dtctl
```

### Validate Against Live API

```bash
# Run validation tests with a context
pytest tests/test_validation.py -v --context=<context-name>
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DTCTL_CONTEXT` | Override default context |
| `DTCTL_OUTPUT` | Override default output format |
| `DTCTL_VERBOSE` | Enable verbose mode |

## Configuration Location

Config file: `~/.config/dtctl/config.yaml` (XDG Base Directory compliant)
