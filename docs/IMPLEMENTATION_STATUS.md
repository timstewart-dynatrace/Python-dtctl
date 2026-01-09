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
- [x] Shell completion (bash, zsh, fish)
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

### Resources Implemented

| Resource | get | describe | create | delete | edit | apply | exec | logs | share |
|----------|-----|----------|--------|--------|------|-------|------|------|-------|
| **workflow** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | - | - |
| **execution** | ✅ | ✅ | - | - | - | - | - | ✅ | - |
| **dashboard** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | - | - | ✅ |
| **notebook** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | - | - | ✅ |
| **settings** | ✅ | ✅ | ✅ | ✅ | - | ✅ | - | - | - |
| **settings-schema** | ✅ | ✅ | - | - | - | - | - | - | - |
| **slo** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | - | - | - |
| **notification** | ✅ | ✅ | - | ✅ | - | - | - | - | - |
| **bucket** | ✅ | ✅ | ✅ | ✅ | - | ✅ | - | - | - |
| **openpipeline** | ✅ | ✅ | - | - | - | - | - | - | - |
| **app** | ✅ | ✅ | - | ✅ | - | - | - | - | - |
| **edgeconnect** | ✅ | ✅ | ✅ | ✅ | - | - | - | - | - |
| **user** | ✅ | ✅ | - | - | - | - | - | - | - |
| **group** | ✅ | ✅ | - | - | - | - | - | - | - |
| **analyzer** | ✅ | ✅ | - | - | - | - | ✅ | - | - |
| **copilot** | ✅ | - | - | - | - | - | ✅ | - | - |

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
