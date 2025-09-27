# CLI Patterns Makefile
# Development and testing automation

.PHONY: help install test test-unit test-integration test-coverage test-parser test-executor test-design test-fast test-components lint type-check format clean all

# Default target
help:
	@echo "CLI Patterns Development Commands"
	@echo "================================="
	@echo "make install        - Install project dependencies with uv"
	@echo "make test          - Run all tests"
	@echo "make test-unit     - Run unit tests only"
	@echo "make test-integration - Run integration tests only"
	@echo "make test-coverage - Run tests with coverage report"
	@echo "make test-parser   - Run parser component tests"
	@echo "make test-executor - Run executor/execution component tests"
	@echo "make test-design   - Run design system tests"
	@echo "make test-fast     - Run non-slow tests only"
	@echo "make test-components - Run all component tests (parser, executor, design)"
	@echo "make lint          - Run ruff linter"
	@echo "make type-check    - Run mypy type checking"
	@echo "make format        - Format code with black"
	@echo "make clean         - Remove build artifacts and cache"
	@echo "make all           - Run format, lint, type-check, and test"

# Install dependencies
install:
	uv sync
	uv add --dev mypy pytest pytest-asyncio pytest-cov pre-commit black ruff

# Run all tests
test:
	PYTHONPATH=src python3 -m pytest tests/ -v

# Run unit tests only
test-unit:
	PYTHONPATH=src python3 -m pytest tests/unit/ -v

# Run integration tests only
test-integration:
	PYTHONPATH=src python3 -m pytest tests/integration/ -v

# Run tests with coverage
test-coverage:
	PYTHONPATH=src python3 -m pytest tests/ --cov=cli_patterns --cov-report=term-missing --cov-report=html

# Run specific test file
test-file:
	@read -p "Enter test file path: " filepath; \
	PYTHONPATH=src python3 -m pytest $$filepath -v

# Lint code
lint:
	uv run ruff check src/ tests/

# Type check with mypy
type-check:
	PYTHONPATH=src python3 -m mypy src/cli_patterns --strict

# Format code
format:
	uv run black src/ tests/

# Clean build artifacts
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf .ruff_cache

# Run all quality checks
all: format lint type-check test

# Quick test for current work
quick:
	PYTHONPATH=src python3 -m pytest tests/unit/ui/design/ -v

# Watch tests (requires pytest-watch)
watch:
	PYTHONPATH=src python3 -m pytest-watch tests/ --clear

# Run pre-commit hooks
pre-commit:
	pre-commit run --all-files

# Initialize pre-commit
pre-commit-install:
	pre-commit install

# Run tests by marker
test-parser:
	PYTHONPATH=src python3 -m pytest tests/ -m parser -v

test-executor:
	PYTHONPATH=src python3 -m pytest tests/ -m executor -v

test-design:
	PYTHONPATH=src python3 -m pytest tests/ -m design -v

test-fast:
	PYTHONPATH=src python3 -m pytest tests/ -m "not slow" -v

test-components:
	PYTHONPATH=src python3 -m pytest tests/ -m "parser or executor or design" -v

# Show test summary
summary:
	@echo "Test Summary"
	@echo "============"
	@echo -n "Unit Tests: "
	@PYTHONPATH=src python3 -m pytest tests/unit/ -q 2>/dev/null | tail -1
	@echo -n "Integration Tests: "
	@PYTHONPATH=src python3 -m pytest tests/integration/ -q 2>/dev/null | tail -1
	@echo -n "Type Check: "
	@PYTHONPATH=src python3 -m mypy src/cli_patterns --strict 2>&1 | grep -E "Success|Found" | head -1