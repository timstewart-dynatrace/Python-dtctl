# Development Workflow - MANDATORY

**ALL development work MUST follow this workflow.**

## Branching Requirements

1. **NEVER commit features directly to main**
   - ALL new features, enhancements, and non-trivial changes MUST be developed in a feature branch
   - Branch naming convention: `feature/descriptive-name` or `fix/descriptive-name`
   - Only documentation fixes and critical hotfixes may be committed directly to main (with approval)

2. **Feature Branch Workflow**
   ```bash
   # Create feature branch from main
   git checkout main
   git pull
   git checkout -b feature/my-feature

   # Develop and commit
   git add <files>
   git commit -m "feat: description"

   # Push feature branch
   git push -u origin feature/my-feature
   ```

3. **Merge Process**
   ```bash
   # Before merging: verify ALL documentation is complete
   git checkout main
   git merge feature/my-feature --no-ff

   # If documentation is missing, DO NOT MERGE
   # Create documentation commits in the feature branch first
   ```

## Documentation Requirements - MANDATORY

**ALL features MUST be documented BEFORE merging to main**

Documentation checklist (ALL must be completed):
- [ ] [AGENTS.md](../../AGENTS.md) - Add to project structure, patterns, or API endpoints
- [ ] [README.md](../../README.md) - Update quick start or features section
- [ ] [docs/IMPLEMENTATION_STATUS.md](../../docs/IMPLEMENTATION_STATUS.md) - Update feature status
- [ ] [CHANGELOG.md](../../CHANGELOG.md) - Add to appropriate section
- [ ] Code comments and docstrings for new functions/classes

## Version Management - MANDATORY

**ALL merges to main that add features or fixes MUST increment the version number.**

Current version: **0.2.4** (defined in `pyproject.toml` and `src/dtctl/__init__.py`)

### Semantic Versioning (SemVer)

We follow [Semantic Versioning 2.0.0](https://semver.org/):

**Format:** `MAJOR.MINOR.PATCH` (e.g., 0.2.0)

1. **MAJOR version** (X.0.0) - Incompatible API changes
2. **MINOR version** (0.X.0) - New features (backwards-compatible)
3. **PATCH version** (0.0.X) - Bug fixes (backwards-compatible)

### Version Bump Checklist

Before merging to main, ensure:
- [ ] Version incremented in `pyproject.toml`
- [ ] Version incremented in `src/dtctl/__init__.py`
- [ ] Both files have **matching** version numbers
- [ ] CHANGELOG.md updated with changes
- [ ] Version bump committed in feature branch before merge

## CHANGELOG Management - MANDATORY

**ALL changes MUST be documented in CHANGELOG.md**

We follow [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format.

### When to Update CHANGELOG

**In your feature branch, BEFORE merging:**

1. **For new features** - Add to `## [Unreleased]` → `### Added` section
2. **For changes** - Add to `## [Unreleased]` → `### Changed` section
3. **For bug fixes** - Add to `## [Unreleased]` → `### Fixed` section

## Verification Before Merge

- Run tests: `pytest tests/ -v`
- Verify command help: `dtctl <new-command> --help`
- Check all documentation files are updated
- Ensure examples are provided
- Verify AGENTS.md includes new patterns/endpoints

**REMEMBER: Documentation is NOT optional. It is MANDATORY before merge.**
