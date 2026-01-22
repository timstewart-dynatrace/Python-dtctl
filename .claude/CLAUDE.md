# dtctl - Claude Code Instructions

> **⚠️ DISCLAIMER**: This tool is **not produced, endorsed, or supported by Dynatrace**. It is an independent, community-driven project. **Use at your own risk.** The authors assume no liability for any issues arising from its use.

## Project Overview

`dtctl` is a kubectl-like CLI tool for interacting with the Dynatrace REST API. The tool follows kubectl's design patterns:
- Resource-oriented commands (get, describe, create, delete, edit, apply, exec)
- Support for multiple output formats (JSON, YAML, table, CSV)
- Configuration management via config files
- Context switching between environments

**Important**: Use kubectl naming conventions (e.g., `exec` not `execute`). Exclude classic-environment v1 and v2 APIs.

## Quick Start

```bash
pip install -e ".[dev]"      # Install with dev dependencies
dtctl --help                  # View available commands
dtctl get workflows           # List workflows
dtctl get dashboards --all    # Include ready-made documents
```

## Rules and Guidelines

| Rule File | Description |
|-----------|-------------|
| [architecture.md](rules/architecture.md) | Project structure, core components, design patterns |
| [commands.md](rules/commands.md) | Available commands and supported resources |
| [development.md](rules/development.md) | Setup, common tasks, tech stack, environment variables |
| [code-style.md](rules/code-style.md) | Python style, adding resources/commands, error handling |
| [testing.md](rules/testing.md) | Test categories, fixtures, writing tests |
| [workflow.md](rules/workflow.md) | Git branching, versioning, changelog, documentation |

## Current Version

**0.2.3** (defined in `pyproject.toml` and `src/dtctl/__init__.py`)

## Key Rules Summary

1. **NEVER commit features directly to main** - Use feature branches
2. **ALL features MUST be documented BEFORE merging**
3. **ALL merges to main MUST increment the version number**
4. **ALL changes MUST be documented in CHANGELOG.md**

See [workflow.md](rules/workflow.md) for complete requirements.
