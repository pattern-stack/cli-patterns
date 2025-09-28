# CLI Patterns

![CI](https://github.com/pattern-stack/cli-patterns/workflows/CI/badge.svg)

A type-safe, interactive wizard-based terminal application framework designed to provide a unified interaction model across Pattern Stack projects.

## Features

- **Type-Safe**: Full MyPy strict mode compliance with semantic types
- **Protocol-Based**: Flexible, extensible architecture using Python protocols
- **Interactive Wizards**: Rich terminal UI with themed components
- **Dual Definition**: Support for both YAML configuration and Python decorators
- **Stateless Execution**: Each run is independent with optional session persistence
- **Real-time Output**: Async subprocess execution with themed output streaming

## Installation

```bash
# Clone the repository
git clone https://github.com/pattern-stack/cli-patterns.git
cd cli-patterns

# Install with development dependencies
make install
```

## Development

```bash
# Run all tests
make test

# Run specific test suites
make test-unit
make test-integration

# Code quality checks
make lint        # Run ruff linter
make type-check  # Run mypy type checking
make format      # Format code

# Full CI pipeline locally
make all         # Format, lint, type-check, and test
```

## Architecture

The project follows a protocol-based architecture with clear boundaries:

- `src/cli_patterns/core/` - Type definitions, models, and protocols
- `src/cli_patterns/config/` - Configuration and theme loading
- `src/cli_patterns/execution/` - Runtime engine and subprocess execution
- `src/cli_patterns/ui/` - User interface components and design system

## Requirements

- Python 3.9 or higher
- Unix-like environment (Linux, macOS, WSL)

## License

MIT License - See LICENSE file for details.

## Contributing

This project follows Pattern Stack standards. See CONTRIBUTING.md for guidelines.