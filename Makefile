.PHONY: all install dev clean test lint format typecheck build

# Default target
all: install

# Install the package in development mode
install:
	pip install -e .

# Install with development dependencies
dev:
	pip install -e ".[dev]"

# Run tests
test:
	pytest tests/ -v

# Run tests with coverage
coverage:
	pytest tests/ -v --cov=dtctl --cov-report=html --cov-report=term

# Run linter
lint:
	ruff check src/

# Fix linting issues
lint-fix:
	ruff check src/ --fix

# Format code
format:
	ruff format src/

# Type checking
typecheck:
	mypy src/dtctl

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf src/*.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# Build distribution packages
build: clean
	python -m build

# Upload to PyPI (requires twine)
publish: build
	twine upload dist/*

# Upload to TestPyPI
publish-test: build
	twine upload --repository testpypi dist/*

# Show help
help:
	@echo "Available targets:"
	@echo "  install      - Install package in development mode"
	@echo "  dev          - Install with development dependencies"
	@echo "  test         - Run tests"
	@echo "  coverage     - Run tests with coverage report"
	@echo "  lint         - Run linter"
	@echo "  lint-fix     - Fix linting issues"
	@echo "  format       - Format code"
	@echo "  typecheck    - Run type checker"
	@echo "  clean        - Remove build artifacts"
	@echo "  build        - Build distribution packages"
	@echo "  publish      - Upload to PyPI"
	@echo "  publish-test - Upload to TestPyPI"
