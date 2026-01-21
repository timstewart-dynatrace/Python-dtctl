# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- Add pagination support to all list operations to return complete results
  - Base CRUDHandler now fetches all pages automatically
  - Documents (dashboards, notebooks) use `page-key` pagination
  - Settings objects and schemas
  - Workflows and executions
  - SLOs, notifications
  - IAM resources (users, groups, policies, bindings, boundaries)
  - Lookup tables

## [0.2.0] - 2026-01-21

### Added
- `wait` command - Wait for DQL query conditions with configurable timeout/interval
  - Conditions: `any`, `none`, `count`, `count-gte`, `count-gt`, `count-lte`, `count-lt`
  - Timeout, interval, max attempts, exponential backoff options
  - Quiet mode for scripts
- `history` command - View version history of resources
  - `dtctl history workflow <id>` - View workflow versions
  - `dtctl history dashboard <id>` - View dashboard snapshots
  - `dtctl history notebook <id>` - View notebook snapshots
- `restore` command - Restore resources to previous versions
  - `dtctl restore workflow <id> --version <n>`
  - `dtctl restore dashboard <id> --snapshot <id>`
  - `dtctl restore notebook <id> --snapshot <id>`
  - Pre-restore snapshot creation option
- `auth` command - Authentication operations
  - `dtctl auth whoami` - Show current identity
  - `dtctl auth test` - Test authentication
- `completion` command - Generate shell completions
  - Supports bash, zsh, fish, powershell
  - Auto-install option (`--install`)
- `chown` command - Transfer ownership of documents
  - `dtctl chown dashboard <id> --to <user-id>`
  - `dtctl chown notebook <id> --to <user-id>`
  - Admin access flag for elevated permissions (`--admin`)
- Lookup tables resource handler
  - `dtctl get lookup-tables` - List lookup tables
  - `dtctl describe lookup-table <id>` - Describe lookup table
  - `dtctl create lookup-table -f data.csv --name <name>` - Create from CSV
  - `dtctl delete lookup-table <id>` - Delete lookup table
  - Auto-detect CSV delimiter
  - Get table data with `--data` flag
- Comprehensive test suite (102 tests)
- `docs/TOKEN_SCOPES.md` - Token scope documentation

### Fixed
- Document filter syntax (use single quotes for API compatibility)

### Changed
- README restructured to match Go project format
- Updated documentation structure

## [0.1.1] - 2025-01-XX

### Added
- Clone command for workflows, dashboards, notebooks, SLOs
- Template command for rendering and validation
- Limits and environments resources
- IAM describe commands for policies, bindings, boundaries
- Bulk operations (apply, delete, execute)
- Export command for resources
- Cache management commands
- In-memory caching with TTL
- Optional OAuth2 authentication support

## [0.1.0] - 2025-01-XX

### Added
- Initial release
- Core CLI framework with Typer
- Configuration management (YAML config, contexts, token storage)
- HTTP client with retry, rate limiting, error handling
- Output formatters: JSON, YAML, table, wide, CSV
- Global flags: `--context`, `--output`, `--verbose`, `--dry-run`, `--plain`
- Resources: workflows, executions, dashboards, notebooks, SLOs, settings, buckets, apps
- Commands: get, describe, create, delete, edit, apply, exec, logs, query, share

[Unreleased]: https://github.com/timstewart-dynatrace/Python-dtctl/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/timstewart-dynatrace/Python-dtctl/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/timstewart-dynatrace/Python-dtctl/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/timstewart-dynatrace/Python-dtctl/releases/tag/v0.1.0
