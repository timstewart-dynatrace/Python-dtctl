# Commands and Resources Reference

## Available Commands

| Command | Description |
|---------|-------------|
| `config` | Manage configuration contexts and credentials |
| `get` | List or get resources (workflows, dashboards, slos, limits, environments, etc.) |
| `describe` | Show detailed resource information |
| `create` | Create resources from manifests |
| `delete` | Delete resources |
| `apply` | Apply configuration (create or update) |
| `edit` | Edit resources in your editor |
| `query` | Execute DQL queries |
| `exec` | Execute workflows, analyzers, copilot |
| `logs` | View execution logs |
| `share` | Share documents |
| `unshare` | Remove document sharing |
| `bulk` | Bulk operations on resources |
| `export` | Export resources to files |
| `cache` | Manage API response cache |
| `clone` | Clone/duplicate resources |
| `template` | Render and validate templates |
| `wait` | Wait for DQL query conditions |
| `history` | View version history of resources |
| `restore` | Restore resources to previous versions |
| `auth` | Authentication operations (whoami, test) |
| `completion` | Generate shell completions (bash, zsh, fish, powershell) |
| `chown` | Change ownership of dashboards/notebooks |

## Supported Resources

| Resource | Aliases | Description |
|----------|---------|-------------|
| **Workflows** | `workflows`, `wf` | Automation workflows |
| **Executions** | `executions`, `exec` | Workflow execution history |
| **Documents** | `documents`, `docs` | All dashboards and notebooks |
| **Dashboards** | `dashboards`, `dash` | Dashboard documents |
| **Notebooks** | `notebooks`, `nb` | Notebook documents |
| **SLOs** | `slos`, `slo` | Service Level Objectives |
| **Settings** | `settings` | Settings objects |
| **Settings Schemas** | `schemas` | Settings schema definitions |
| **Buckets** | `buckets` | Grail storage buckets |
| **Apps** | `apps` | App Engine applications |
| **Users** | `users` | IAM users |
| **Groups** | `groups` | IAM groups |
| **Policies** | `policies` | IAM policies |
| **Bindings** | `bindings` | Policy bindings |
| **Boundaries** | `boundaries` | Policy boundaries |
| **Effective Permissions** | `effective-permissions` | Calculated permissions |
| **Notifications** | `notifications` | Event notifications |
| **Analyzers** | `analyzers` | Davis AI analyzers |
| **CoPilot Skills** | `copilot-skills` | Davis CoPilot skills |
| **EdgeConnect** | `edgeconnects`, `ec` | EdgeConnect configurations |
| **OpenPipeline** | `openpipelines`, `op` | OpenPipeline configurations |
| **Limits** | `limits` | Account limits & quotas |
| **Environments** | `environments`, `env` | Configured environments |
| **Lookup Tables** | `lookup-tables`, `lookups`, `lt` | Data lookup tables |

## Document Filtering

By default, document commands (`get documents`, `get dashboards`, `get notebooks`) show only user-created documents (UUID IDs).

Use `--all` / `-a` flag to include Dynatrace ready-made documents.

```bash
dtctl get dashboards          # User-created only
dtctl get dashboards --all    # Include ready-made
```
