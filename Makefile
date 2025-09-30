# CLI Patterns Makefile
# Development and testing automation

.PHONY: help install test test-unit test-integration test-coverage test-parser test-executor test-design test-fast test-components lint lint-fix type-check format clean clean-docker all quality format-check ci-setup ci-native ci-docker verify-sync benchmark test-all ci-summary

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
	@echo "make lint-fix      - Run ruff linter and auto-fix issues"
	@echo "make type-check    - Run mypy type checking"
	@echo "make format        - Format code with black"
	@echo "make clean         - Remove build artifacts and cache"
	@echo "make clean-docker  - Clean up Docker containers and volumes"
	@echo "make all           - Run format, lint, type-check, and test"

# Install dependencies
install:
	@if command -v uv > /dev/null 2>&1; then \
		uv sync; \
		uv add --dev mypy pytest pytest-asyncio pytest-cov pre-commit black ruff; \
	else \
		pip install -e .; \
		pip install mypy pytest pytest-asyncio pytest-cov pre-commit black ruff; \
	fi

# Run all tests
test:
	@if command -v uv > /dev/null 2>&1; then \
		PYTHONPATH=src uv run pytest tests/ -v; \
	else \
		PYTHONPATH=src python3 -m pytest tests/ -v; \
	fi

# Run unit tests only
test-unit:
	@if command -v uv > /dev/null 2>&1; then \
		PYTHONPATH=src uv run pytest tests/unit/ -v; \
	else \
		PYTHONPATH=src python3 -m pytest tests/unit/ -v; \
	fi

# Run integration tests only
test-integration:
	@if command -v uv > /dev/null 2>&1; then \
		PYTHONPATH=src uv run pytest tests/integration/ -v; \
	else \
		PYTHONPATH=src python3 -m pytest tests/integration/ -v; \
	fi

# Run tests with coverage
test-coverage:
	@if command -v uv > /dev/null 2>&1; then \
		PYTHONPATH=src uv run pytest tests/ --cov=cli_patterns --cov-report=term-missing --cov-report=html; \
	else \
		PYTHONPATH=src python3 -m pytest tests/ --cov=cli_patterns --cov-report=term-missing --cov-report=html; \
	fi

# Run specific test file
test-file:
	@read -p "Enter test file path: " filepath; \
	PYTHONPATH=src python3 -m pytest $$filepath -v

# Lint code
lint:
	@if command -v uv > /dev/null 2>&1; then \
		uv run ruff check src/ tests/; \
	else \
		ruff check src/ tests/; \
	fi

# Lint code and auto-fix issues
lint-fix:
	@if command -v uv > /dev/null 2>&1; then \
		uv run ruff check src/ tests/ --fix; \
	else \
		ruff check src/ tests/ --fix; \
	fi

# Type check with mypy
type-check:
	@if command -v uv > /dev/null 2>&1; then \
		PYTHONPATH=src uv run mypy src/cli_patterns --strict; \
	else \
		PYTHONPATH=src python3 -m mypy src/cli_patterns --strict; \
	fi

# Format code
format:
	@if command -v uv > /dev/null 2>&1; then \
		uv run black src/ tests/; \
	else \
		black src/ tests/; \
	fi

# Clean build artifacts
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf .ruff_cache

# Clean Docker containers and volumes
clean-docker:
	docker compose -f docker-compose.ci.yml down --remove-orphans

# Run all quality checks
all: format lint type-check test

# Quick test for current work
quick:
	@if command -v uv > /dev/null 2>&1; then \
		PYTHONPATH=src uv run pytest tests/unit/ui/design/ -v; \
	else \
		PYTHONPATH=src python3 -m pytest tests/unit/ui/design/ -v; \
	fi

# Watch tests (requires pytest-watch)
watch:
	@if command -v uv > /dev/null 2>&1; then \
		PYTHONPATH=src uv run pytest-watch tests/ --clear; \
	else \
		PYTHONPATH=src python3 -m pytest-watch tests/ --clear; \
	fi

# Run pre-commit hooks
pre-commit:
	pre-commit run --all-files

# Initialize pre-commit
pre-commit-install:
	pre-commit install

# Run tests by marker
test-parser:
	@if command -v uv > /dev/null 2>&1; then \
		PYTHONPATH=src uv run pytest tests/ -m parser -v; \
	else \
		PYTHONPATH=src python3 -m pytest tests/ -m parser -v; \
	fi

test-executor:
	@if command -v uv > /dev/null 2>&1; then \
		PYTHONPATH=src uv run pytest tests/ -m executor -v; \
	else \
		PYTHONPATH=src python3 -m pytest tests/ -m executor -v; \
	fi

test-design:
	@if command -v uv > /dev/null 2>&1; then \
		PYTHONPATH=src uv run pytest tests/ -m design -v; \
	else \
		PYTHONPATH=src python3 -m pytest tests/ -m design -v; \
	fi

test-fast:
	@if command -v uv > /dev/null 2>&1; then \
		PYTHONPATH=src uv run pytest tests/ -m "not slow" -v; \
	else \
		PYTHONPATH=src python3 -m pytest tests/ -m "not slow" -v; \
	fi

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

# CI-specific targets
# Combined quality checks
quality: lint type-check format-check

# Format check (for CI, doesn't modify)
format-check:
	@if command -v uv > /dev/null 2>&1; then \
		uv run black src/ tests/ --check; \
	else \
		black src/ tests/ --check; \
	fi

# Environment info (for sync checking)
ci-setup:
	@echo "=== Environment Info ==="
	@python3 --version
	@if command -v uv > /dev/null 2>&1; then \
		uv --version; \
		echo "=== Dependencies (first 10) ==="; \
		uv pip list | head -10; \
	else \
		pip --version; \
		echo "=== Dependencies (first 10) ==="; \
		pip list | head -10; \
	fi

# Native CI run
ci-native: quality test-all

# Docker CI run
ci-docker:
	docker compose -f docker-compose.ci.yml run --rm ci make ci-native

# Verify environments are in sync
verify-sync:
	@echo "Checking native environment..."
	@make ci-setup > /tmp/native-env.txt
	@echo "Checking Docker environment..."
	@docker compose -f docker-compose.ci.yml run ci make ci-setup > /tmp/docker-env.txt
	@echo "Comparing..."
	@diff /tmp/native-env.txt /tmp/docker-env.txt && echo "✅ In sync!" || echo "❌ Out of sync!"

# Placeholder for future benchmarks
benchmark:
	@echo "Benchmark suite not yet implemented"
	@echo "Future: pytest tests/ --benchmark-only"

# All tests
test-all: test-unit test-integration

# Summary for CI
ci-summary:
	@echo "=== CI Summary ==="
	@echo "Quality checks: make quality"
	@echo "All tests: make test-all"
	@echo "Component tests: make test-components"