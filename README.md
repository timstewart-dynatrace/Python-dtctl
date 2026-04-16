# dtctl

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**Your Dynatrace platform, one command away.**

`dtctl` brings the power of `kubectl` to Dynatrace — manage workflows, dashboards, queries, and more from your terminal. Built for developers who prefer the command line and AI-assisted workflows.

```bash
dtctl get workflows                           # List all workflows
dtctl query "fetch logs | limit 10"           # Run DQL queries
dtctl edit dashboard "Production Overview"    # Edit resources in your $EDITOR
dtctl apply -f workflow.yaml                  # Declarative configuration
```

> **⚠️ DISCLAIMER**: This tool is provided "as-is" without warranty and is **not produced, endorsed, or supported by Dynatrace**. It is an independent, community-driven project. **Use at your own risk.** The authors assume no liability for any issues arising from its use. Always test in non-production environments first. For official Dynatrace tools and support, please visit [dynatrace.com](https://www.dynatrace.com).

## Why dtctl?

- **kubectl-style UX** — Familiar commands: `get`, `describe`, `edit`, `apply`, `delete`
- **AI-friendly** — Plain output modes and YAML editing for seamless AI tool integration
- **Multi-environment** — Switch between dev/staging/prod with a single command
- **Template support** — DQL queries and manifests with Jinja2 template variables
- **Shell completion** — Tab completion for bash, zsh, fish, and PowerShell

## AI Agent Skill

dtctl includes an **Agent Skill** — a structured guide that teaches AI assistants (like GitHub Copilot or Claude Code) how to use dtctl effectively.

**To enable:**
1. Copy [`AGENTS.md`](AGENTS.md) to your AI assistant's configuration directory
2. The AI will learn dtctl commands, resource types, and best practices

This makes dtctl particularly powerful for AI-assisted DevOps workflows.

## Quick Start

```bash
# Install from source
pip install -e .

# Configure your environment
dtctl config set-credentials my-token --token "dt0s16.YOUR_TOKEN"

dtctl config set-context my-env \
  --environment "https://abc12345.apps.dynatrace.com" \
  --token-ref my-token

# Go!
dtctl get workflows
dtctl query "fetch logs | limit 10"
```

## What Can It Do?

| Resource | Operations |
|----------|------------|
| Workflows | get, describe, create, edit, delete, execute, history, restore |
| Dashboards & Notebooks | get, describe, create, edit, delete, share, history, restore |
| DQL Queries | execute with template variables, wait for conditions |
| SLOs | get, describe, create, edit, delete, apply |
| Settings | get schemas, get/create/update/delete objects |
| Buckets | get, describe, create, delete |
| Lookup Tables | get, describe, create, delete |
| IAM | get users, groups, policies, bindings, boundaries |
| And more... | OpenPipeline, EdgeConnect, Davis AI, Limits, Environments |

## Documentation

| Guide | Description |
|-------|-------------|
| [Installation](docs/INSTALLATION.md) | Install dtctl from source or PyPI |
| [Quick Start](docs/QUICK_START.md) | Configuration and first commands |
| [Token Scopes](docs/TOKEN_SCOPES.md) | Required API token permissions |
| [API Design](docs/API_DESIGN.md) | Complete command reference |
| [Architecture](docs/ARCHITECTURE.md) | Implementation details |
| [Implementation Status](docs/IMPLEMENTATION_STATUS.md) | Feature roadmap and progress |

## Contributing

Contributions are welcome! Please see [AGENTS.md](AGENTS.md) for development guidelines and architecture details.

## License

MIT License — see [LICENSE](LICENSE)

---

<sub>A Python port inspired by [dynatrace-oss/dtctl](https://github.com/dynatrace-oss/dtctl)</sub>
