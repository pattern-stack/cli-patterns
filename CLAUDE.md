# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CLI Patterns is a type-safe, interactive wizard-based terminal application framework designed to provide a unified interaction model across Pattern Stack projects. The system emphasizes strong typing with MyPy strict mode, stateless execution, and supports both YAML configuration and Python code definitions.

## Development Commands

### Core Development Tasks
```bash
# Install dependencies
make install

# Run all tests
make test

# Run specific test categories
make test-unit         # Unit tests only
make test-integration  # Integration tests only
make test-coverage     # Tests with coverage report

# Run specific test file
PYTHONPATH=src python3 -m pytest tests/path/to/test_file.py -v

# Code quality checks
make lint        # Run ruff linter
make type-check  # Run mypy type checking (strict mode)
make format      # Format code with black

# Combined workflow
make all         # Format, lint, type-check, and test
```

### Testing Specific Components
```bash
# Test UI design components
PYTHONPATH=src python3 -m pytest tests/unit/ui/design/ -v

# Test execution components
PYTHONPATH=src python3 -m pytest tests/unit/execution/ -v

# Test parser components
PYTHONPATH=src python3 -m pytest tests/unit/ui/parser/ -v
```

## Architecture Overview

### Core Structure
The project follows a protocol-based architecture with clear boundaries between components:

- **Type System First**: All components use semantic types (`BranchId`, `ActionId`, `OptionKey`) to prevent type confusion
- **Protocol-Based Design**: Core functionality defined through protocols, allowing flexible implementations
- **Stateless Execution**: Each run is independent with optional session persistence
- **Hybrid Definitions**: Support for both YAML (simple workflows) and Python decorators (complex logic)

### Key Directories
```
src/cli_patterns/
├── core/           # Type definitions, models, and protocols
├── config/         # Configuration and theme loading
├── execution/      # Runtime engine and subprocess execution
├── ui/             # User interface components
│   ├── design/     # Design system (themes, tokens, components)
│   ├── parser/     # Command parsing system
│   └── screens/    # Screen implementations (future)
└── cli.py          # Main entry point
```

### Design System
The UI uses a comprehensive design system with:
- **Design Tokens**: Semantic tokens for categories, hierarchy, status, and emphasis
- **Theme System**: Extensible themes with inheritance support
- **Component Registry**: Centralized component registration and theming
- **Rich Integration**: Built on Rich library for terminal rendering

### Parser System
The command parsing system provides flexible input interpretation:
- **Protocol-based**: All parsers implement the `Parser` protocol for consistency
- **Pipeline Architecture**: `ParserPipeline` routes input to appropriate parsers
- **Command Registry**: Manages command metadata and provides fuzzy-matching suggestions
- **Multiple Paradigms**: Supports text commands, shell pass-through (!), and extensible for more

### Key Protocols
- `WizardConfig`: Complete wizard definition
- `SessionState`: Runtime state management
- `ActionExecutor`: Protocol for action execution
- `OptionCollector`: Protocol for option collection
- `NavigationController`: Protocol for navigation
- `Parser`: Protocol for command parsers with consistent input interpretation

## Type System Requirements

All code must maintain MyPy strict mode compliance:
- Use semantic types instead of primitives where appropriate
- Implement discriminated unions for action/option types
- Define runtime-checkable protocols for extensibility points
- Use Pydantic models for structured validation

## Testing Patterns

Tests are organized by component:
- `tests/unit/`: Unit tests for individual components
- `tests/integration/`: Integration tests for component interactions

Key testing focus areas:
- Type system validation
- Protocol compliance
- Theme and design token resolution
- Subprocess execution with real-time output
- YAML/Python definition loading

## Current Implementation Status

### Completed Components
- Design system (themes, tokens, components, registry)
- Subprocess executor with async execution and themed output (CLI-9)
- Interactive shell with prompt_toolkit (CLI-7)
- Command parser system with composable architecture (CLI-8)
- Command registry with fuzzy matching and suggestions
- Basic type definitions and protocols structure

### In Progress
- Test coverage improvements
- Integration testing

### Pending Implementation
- Core wizard models and validation
- YAML/JSON definition loaders
- Python decorator system
- Navigation controller
- Session state management
- CLI entry point

## Important Conventions

1. **Import Style**: Use absolute imports from `cli_patterns` package
2. **Type Annotations**: Required for all functions and class methods
3. **Error Handling**: Use structured exceptions with clear messages
4. **Async First**: Prefer async/await for I/O operations
5. **Protocol Compliance**: All implementations must satisfy their protocol contracts