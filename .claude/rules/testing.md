# Testing Conventions

## Running Tests

```bash
# Run all unit tests
pytest tests/ -v

# Run with coverage
pytest --cov=dtctl

# Run excluding integration/validation tests
pytest tests/ -v --ignore=tests/test_validation.py --ignore=tests/test_integration.py

# Type checking
mypy src/dtctl
```

## Test Categories

### Unit Tests
- Located in `tests/test_*.py`
- Mock all external dependencies
- Run without network access
- Fast execution

### Integration Tests
- Marked with `@pytest.mark.integration`
- Require valid Dynatrace context
- Run with: `pytest tests/test_integration.py -v`
- Skip with: `pytest tests/ -m "not integration"`

### Validation Tests
- Marked with `@pytest.mark.validation`
- Accept `--context` parameter for live API testing
- Use dry-run mode for mutating operations
- **Always log output for reference** when running with a context

```bash
# Run validation tests and log output for reference
pytest tests/test_validation.py -v --context=<context-name> 2>&1 | tee validation-output.log

# Run with timestamps for debugging
pytest tests/test_validation.py -v --context=<context-name> --tb=short 2>&1 | tee "validation-$(date +%Y%m%d-%H%M%S).log"

# Run with full verbosity (shows captured stdout/stderr for all tests)
pytest tests/test_validation.py -v --context=<context-name> -s --tb=long 2>&1 | tee validation-verbose.log

# Run with maximum verbosity (includes fixture setup, full tracebacks)
pytest tests/test_validation.py -vv --context=<context-name> -s --tb=long --capture=no 2>&1 | tee validation-full.log
```

## Test Fixtures

Common fixtures are defined in `tests/conftest.py`:

- `cli_runner` - Typer CliRunner for testing commands
- `mock_config` - Mock configuration with test contexts
- `mock_client` - Mock HTTP client
- `patch_config` - Patch load_config to return mock
- `patch_client` - Patch create_client_from_config to return mock
- `sample_*` - Sample data fixtures for various resources

## Writing Tests

### Command Tests
```python
from typer.testing import CliRunner
from dtctl.cli import app

def test_my_command(cli_runner: CliRunner, patch_config, patch_client):
    result = cli_runner.invoke(app, ["my-command", "arg"])
    assert result.exit_code == 0
    assert "expected output" in result.output
```

### Handler Tests
```python
from unittest.mock import MagicMock
from dtctl.resources.myresource import MyHandler

def test_handler_list(mock_client):
    mock_client.get.return_value.json.return_value = {"items": [...]}
    handler = MyHandler(mock_client)
    result = handler.list()
    assert len(result) == expected_count
```

## Verification Before Merge

- All tests must pass: `pytest tests/ -v`
- Verify command help works: `dtctl <new-command> --help`
- Check for regressions in existing functionality
