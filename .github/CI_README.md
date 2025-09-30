# GitHub Actions CI/CD

This directory contains CI/CD workflows for the CLI Patterns framework.

## Workflow Structure

### Main CI Pipeline (`ci.yml`)
The primary CI workflow that orchestrates all quality checks and tests.

**Triggers:**
- Push to `main` or `develop` branches
- All pull requests
- Manual workflow dispatch with optional Docker mode

**Jobs:**
- **Quality Checks**: Linting, type checking, and formatting verification
- **Test Suites**: Parallel execution of unit, integration, and component tests
- **Fast Tests**: Quick smoke tests for rapid feedback
- **Python Compatibility**: Tests against multiple Python versions (main branch only)
- **Benchmarks**: Performance benchmarking placeholder (main branch only)

### Claude Integration (`claude.yml`)
GitHub App integration for Claude Code assistant.

**Features:**
- Automated PR reviews and assistance
- Issue refinement and implementation
- TDD-driven development support

### Local Actions (`actions/`)
Reusable action components following Pattern Stack standards.

**Setup Action** (`actions/setup/action.yml`):
- Python environment configuration with `uv`
- Dependency caching
- Development tools installation

## Test Organization

Tests are organized by markers and components:

| Test Suite | Description | Command |
|------------|-------------|---------|
| `unit` | Unit tests for individual components | `make test-unit` |
| `integration` | Integration tests for component interactions | `make test-integration` |
| `parser` | Parser and CLI registry tests | `make test-parser` |
| `executor` | Execution engine tests | `make test-executor` |
| `design` | Design system and theming tests | `make test-design` |
| `fast` | Quick tests (excludes slow-marked tests) | `make test-fast` |

## Execution Modes

### Native Execution (Default)
Runs directly on GitHub-hosted runners using the setup action.

### Docker Execution (Optional)
Containerized execution for consistent environments:
- Triggered via workflow dispatch with `use_docker: true`
- Uses `docker-compose.ci.yml` configuration
- Ensures reproducible builds across environments

## Quality Standards

All code must pass:
- **Ruff**: Linting and formatting checks
- **MyPy**: Strict type checking
- **Black**: Code formatting (secondary formatter)
- **Tests**: All test suites must pass

## Local Development

Run the same CI checks locally:

```bash
# Install dependencies
make install

# Run all quality checks
make quality

# Run all tests
make test

# Run specific test suites
make test-unit
make test-integration
make test-parser

# Run with coverage
make test-coverage

# Format code
make format
```

## Python Version Support

The project officially supports Python 3.9 through 3.12, with compatibility testing across versions on the main branch.

## Pattern Stack Standards

This CI configuration follows Pattern Stack organizational standards:
- Hierarchical action structure for future organization-wide sharing
- Consistent naming conventions
- Docker-first optional execution
- Comprehensive test coverage requirements