# dtctl Implementation Status

> **⚠️ DISCLAIMER**: This tool is **not produced, endorsed, or supported by Dynatrace**. It is an independent, community-driven project. **Use at your own risk.** The authors assume no liability for any issues arising from its use. Always test in non-production environments first.

## Overview

This document tracks implemented features and planned work for the Python dtctl CLI.

---

## Implemented Features ✅

### Core Infrastructure
- [x] Python package with Typer CLI framework
- [x] Configuration management (YAML config, contexts, token storage)
- [x] HTTP client with retry, rate limiting, error handling
- [x] Output formatters: JSON, YAML, table, wide, CSV
- [x] Global flags: `--context`, `--output`, `--verbose`, `--dry-run`, `--plain`
- [x] Shell completion (bash, zsh, fish, powershell)
- [x] In-memory caching with TTL (reduce API calls)
- [x] Optional OAuth2 authentication support

### Verbs Implemented
- [x] `get` - List/retrieve resources
- [x] `describe` - Detailed resource info
- [x] `create` - Create from manifest
- [x] `delete` - Delete resources
- [x] `edit` - Edit in $EDITOR
- [x] `apply` - Create or update
- [x] `exec` - Execute workflows
- [x] `logs` - View execution logs
- [x] `query` - Execute DQL queries
- [x] `cache` - Manage API response cache
- [x] `bulk` - Bulk operations on resources
- [x] `export` - Export resources to files
- [x] `clone` - Clone/duplicate resources
- [x] `template` - Render and validate templates
- [x] `wait` - Wait for DQL query conditions
- [x] `history` - View version history
- [x] `restore` - Restore to previous versions
- [x] `auth` - Authentication operations (whoami, test)
- [x] `completion` - Generate shell completions (bash, zsh, fish, powershell)
- [x] `chown` - Change ownership of dashboards/notebooks

### Resources Implemented

| Resource | get | describe | create | delete | edit | apply | exec | logs | share | chown |
|----------|-----|----------|--------|--------|------|-------|------|------|-------|-------|
| **workflow** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | - | - | - |
| **execution** | ✅ | ✅ | - | - | - | - | - | ✅ | - | - |
| **document** | ✅ | - | - | - | - | - | - | - | - | - |
| **dashboard** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | - | - | ✅ | ✅ |
| **notebook** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | - | - | ✅ | ✅ |
| **settings** | ✅ | ✅ | ✅ | ✅ | - | ✅ | - | - | - | - |
| **settings-schema** | ✅ | ✅ | - | - | - | - | - | - | - | - |
| **slo** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | - | - | - | - |
| **notification** | ✅ | ✅ | - | ✅ | - | - | - | - | - | - |
| **bucket** | ✅ | ✅ | ✅ | ✅ | - | ✅ | - | - | - | - |
| **openpipeline** | ✅ | ✅ | - | - | - | - | - | - | - | - |
| **app** | ✅ | ✅ | - | ✅ | - | - | - | - | - | - |
| **edgeconnect** | ✅ | ✅ | ✅ | ✅ | - | - | - | - | - | - |
| **user** | ✅ | ✅ | - | - | - | - | - | - | - | - |
| **group** | ✅ | ✅ | - | - | - | - | - | - | - | - |
| **policy** | ✅ | ✅ | - | - | - | - | - | - | - | - |
| **binding** | ✅ | ✅ | - | - | - | - | - | - | - | - |
| **boundary** | ✅ | ✅ | - | - | - | - | - | - | - | - |
| **effective-permissions** | ✅ | - | - | - | - | - | - | - | - | - |
| **analyzer** | ✅ | ✅ | - | - | - | - | ✅ | - | - | - |
| **copilot** | ✅ | - | - | - | - | - | ✅ | - | - | - |
| **limits** | ✅ | - | - | - | - | - | - | - | - | - |
| **environments** | ✅ | - | - | - | - | - | - | - | - | - |
| **lookup-table** | ✅ | ✅ | ✅ | ✅ | - | - | - | - | - | - |

### DQL Query Features
- [x] Inline queries: `dtctl query "fetch logs | limit 10"`
- [x] File-based queries: `dtctl query -f query.dql`
- [x] Template variables: `--set key=value`
- [x] All output formats supported

### Davis AI Features
- [x] List analyzers: `dtctl get analyzers`
- [x] Get analyzer definition: `dtctl get analyzer <name>`
- [x] Execute analyzer: `dtctl exec analyzer <name> -f input.json`
- [x] List CoPilot skills: `dtctl get copilot-skills`
- [x] Chat with CoPilot: `dtctl exec copilot "question"`
- [x] NL to DQL: `dtctl exec nl2dql "show error logs"`

---

## Planned Features

### Cache Features
- [x] In-memory cache with configurable TTL
- [x] Cache statistics (`dtctl cache stats`)
- [x] Clear cache (`dtctl cache clear`)
- [x] Prefix-based clearing (`dtctl cache clear --prefix workflows`)
- [x] Expired entry cleanup (`dtctl cache clear --expired`)

### Bulk Operations
- [x] Bulk apply resources from file (`dtctl bulk apply -f resources.yaml`)
- [x] Bulk delete resources (`dtctl bulk delete -f ids.csv --type workflow`)
- [x] Bulk create workflows (`dtctl bulk create-workflows -f workflows.yaml`)
- [x] Bulk execute workflows (`dtctl bulk exec-workflows -f workflows.csv`)

### Export Features
- [x] Export all resources (`dtctl export all`)
- [x] Export by type (`dtctl export all -i workflows,slos`)
- [x] Export single resource (`dtctl export workflow <id>`)
- [x] Export query results (`dtctl export query-results "..." -o results.csv`)
- [x] Multiple formats: JSON, YAML, CSV

### OAuth2 Authentication (Optional)
- [x] Client credentials flow support
- [x] Automatic token refresh
- [x] Token caching with expiry buffer
- [x] Alternative to bearer tokens for automation

### Clone Features
- [x] Clone workflows (`dtctl clone workflow <id> --name "New Name"`)
- [x] Clone dashboards (`dtctl clone dashboard <id> --name "New Name"`)
- [x] Clone notebooks (`dtctl clone notebook <id> --name "New Name"`)
- [x] Clone SLOs (`dtctl clone slo <id> --name "New Name"`)
- [x] Options for privacy, deployment state

### Template Features
- [x] Render templates (`dtctl template render -f template.yaml --set key=value`)
- [x] Validate templates (`dtctl template validate -f template.yaml`)
- [x] List variables (`dtctl template variables -f template.yaml`)
- [x] Apply templates (`dtctl template apply -f template.yaml --set key=value`)

### Additional GET Commands
- [x] Get limits (`dtctl get limits`)
- [x] Get environments (`dtctl get environments`)

### IAM Features
- [x] List policies (`dtctl get policies`)
- [x] Describe policy (`dtctl describe policy <uuid>`)
- [x] List bindings (`dtctl get bindings`)
- [x] Describe binding (`dtctl describe binding --policy <uuid> --group <uuid>`)
- [x] List boundaries (`dtctl get boundaries`)
- [x] Describe boundary (`dtctl describe boundary --policy <uuid> --group <uuid>`)
- [x] Get effective permissions (`dtctl get effective-permissions <id> --user|--group`)
- [x] Support for account and environment level scoping

### Wait Command
- [x] Wait for DQL conditions (`dtctl wait --condition any "fetch logs | limit 10"`)
- [x] Conditions: `any`, `none`, `count`, `count-gte`, `count-gt`, `count-lte`, `count-lt`
- [x] Timeout and interval options
- [x] Max attempts limit
- [x] Exponential backoff support
- [x] Quiet mode for scripts

### History & Restore
- [x] View workflow versions (`dtctl history workflow <id>`)
- [x] View dashboard snapshots (`dtctl history dashboard <id>`)
- [x] View notebook snapshots (`dtctl history notebook <id>`)
- [x] Restore workflow to version (`dtctl restore workflow <id> --version <n>`)
- [x] Restore dashboard to snapshot (`dtctl restore dashboard <id> --snapshot <id>`)
- [x] Restore notebook to snapshot (`dtctl restore notebook <id> --snapshot <id>`)
- [x] Pre-restore snapshot creation option

### Auth Command
- [x] Show current identity (`dtctl auth whoami`)
- [x] Test authentication (`dtctl auth test`)
- [x] JSON output support

### Shell Completion
- [x] Bash completion script generation
- [x] Zsh completion script generation
- [x] Fish completion script generation
- [x] PowerShell completion script generation
- [x] Auto-install option (`--install`)

### Lookup Tables
- [x] List lookup tables (`dtctl get lookup-tables`)
- [x] Describe lookup table (`dtctl describe lookup-table <id>`)
- [x] Create from CSV (`dtctl create lookup-table -f data.csv --name <name>`)
- [x] Delete lookup table (`dtctl delete lookup-table <id>`)
- [x] Auto-detect CSV delimiter
- [x] Get table data (`dtctl get lookup-tables <id> --data`)

### Change Ownership
- [x] Transfer dashboard ownership (`dtctl chown dashboard <id> --to <user-id>`)
- [x] Transfer notebook ownership (`dtctl chown notebook <id> --to <user-id>`)
- [x] Admin access flag for elevated permissions (`--admin`)

### Phase 5: Advanced CLI Features (Remaining)
- [ ] Label selectors (`-l env=prod`)
- [ ] Watch mode (`--watch`)
- [ ] Diff command
- [ ] Patch command
- [ ] JSONPath output
- [ ] Chart/sparkline output for timeseries

### Phase 6: Production Readiness
- [ ] PyPI package publishing
- [ ] GitHub Actions CI/CD
- [ ] Homebrew formula
- [ ] OS keychain integration
- [ ] Comprehensive test suite

---

## Success Metrics

| Phase | Status |
|-------|--------|
| Phase 0 (Foundation) | ✅ Complete |
| Phase 1 (Workflows & DQL) | ✅ Complete |
| Phase 2 (Notebooks & Dashboards) | ✅ Complete |
| Phase 3 (Additional Resources) | ✅ Complete |
| Phase 4 (Advanced Resources) | ✅ Complete |
| Phase 5-6 | ⏳ Planned |
