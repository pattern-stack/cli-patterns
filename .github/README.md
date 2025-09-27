# GitHub Actions Workflows

This directory contains CI/CD workflows for the geography-patterns monorepo.

## Workflow Structure

### Per-Project Testing
- **`test-wof-explorer.yml`** - Tests for WOF Explorer package
- **`test-geo-platform.yml`** - Tests for Geo Platform package

### Quality Checks
- **`quality-checks.yml`** - Linting, type checking, and formatting checks across both packages

### Orchestration
- **`ci.yml`** - Main CI workflow that runs all checks together

## Workflow Details

### Test WOF Explorer (`test-wof-explorer.yml`)
- **Triggers**: Changes to `wof-explorer/` directory, workflow file, or dependencies
- **Python versions**: 3.11, 3.12, 3.13
- **Test database**: Downloads Barbados WOF database for integration tests
- **Commands**:
  - `uv run pytest tests/ -v`
  - `uv run pytest tests/test_examples.py -v`

### Test Geo Platform (`test-geo-platform.yml`)
- **Triggers**: Changes to `geo-platform/` directory, workflow file, or dependencies
- **Python versions**: 3.11, 3.12, 3.13
- **Services**: PostgreSQL with PostGIS extension
- **Commands**:
  - `uv run pytest __tests__/unit/ -v`
  - `uv run pytest __tests__/integration/ -v`
  - `uv run pytest __tests__/ -v`

### Quality Checks (`quality-checks.yml`)
- **Triggers**: All pushes and PRs
- **Matrix**: Runs for both `wof-explorer` and `geo-platform`
- **Jobs**:
  - **Lint**: `uv run ruff check .`
  - **Typecheck**: `uv run mypy src/`
  - **Format Check**: `uv run ruff format --check .` (+ black for WOF Explorer)

### Main CI (`ci.yml`)
- **Triggers**: Pushes to main/develop branches, all PRs
- **Strategy**: Orchestrates all other workflows
- **Final check**: Ensures all sub-workflows pass before marking CI as successful

## Quality Standards

### Expected Results
- **Geo Platform**: All checks should pass (0 linting issues, 0 type issues)
- **WOF Explorer**: Known issues documented (41 linting issues, 343 type issues)

### Failure Handling
- Geo Platform failures block CI
- WOF Explorer quality issues are documented but don't block CI (`continue-on-error: true`)
- Test failures always block CI for both packages

## Local Development

Run the same checks locally using Make commands:

```bash
# Run all checks
make check

# Per-package testing
make test-wof
make test-geo

# Quality checks
make lint
make typecheck
make format
```

## Path-Based Triggers

Workflows are optimized to only run when relevant files change:

- Package-specific workflows only trigger on changes to their respective directories
- Quality checks run on all changes
- Dependencies changes (pyproject.toml, uv.lock) trigger relevant workflows