# Product Requirements Document: CLI Patterns MVP

## Executive Summary

CLI Patterns is a type-safe, wizard-based command-line interface system designed to provide a unified interaction model across all Pattern Stack projects. The system emphasizes strong typing, stateless execution, and a hybrid definition model supporting both YAML configuration and Python code.

## 1. Product Overview

### 1.1 Vision
Create a universal CLI framework that is intentionally lightweight, heavily type-protected, and provides a consistent interface across all Pattern Stack projects while remaining simple enough to eventually port to Rust.

### 1.2 Goals
- **Type Safety**: Leverage Python's type system to its fullest with MyPy strict mode compliance
- **Simplicity**: Sophisticated type system with simple runtime behavior
- **Flexibility**: Support both declarative (YAML) and programmatic (Python) wizard definitions
- **Portability**: Design with future Rust migration in mind
- **Stateless**: Default to stateless execution with optional session persistence

### 1.3 Non-Goals for MVP
- Complex shell management (tmux integration)
- Cross-project navigation
- UI implementation (only protocols)
- Hook systems (pre/post execution)
- Remote execution
- Transaction/rollback support

## 2. Key Features

### 2.1 Wizard-Based Navigation
- Tree-structured command organization
- Branch-based execution flow
- Menu-driven navigation between branches
- State management within execution context

### 2.2 Hybrid Definition System
- **YAML/JSON Definitions**: Simple, declarative wizard definitions for straightforward workflows
- **Python Decorators**: Complex logic implementation with decorator-based registration
- **Validation**: Parse-time, compile-time, and runtime validation

### 2.3 Type System
- **Semantic Types**: `BranchId`, `ActionId`, `OptionKey` prevent type confusion
- **Discriminated Unions**: Automatic type discrimination for actions and options
- **Runtime Protocols**: Checkable protocols for extensibility
- **Pydantic Models**: Structured validation with clear error messages

### 2.4 Action System
- **Bash Actions**: Shell command execution via subprocess
- **Python Actions**: Native Python function execution
- **Config Actions**: State/configuration updates
- **Validation**: Prerequisites and confirmation support

### 2.5 Option Collection
- **Type-Safe Input**: Text, number, boolean, select, multi-select
- **Validation**: Pattern matching, range checking, choice validation
- **Defaults**: Type-appropriate default values

## 3. Architecture

### 3.1 Core Components

```
cli_patterns/
├── core/                 # Type definitions and models
├── definitions/          # Wizard loading and registration
├── execution/           # Runtime engine
└── cli/                 # Entry point
```

### 3.2 Key Interfaces

1. **WizardConfig**: Complete wizard definition
2. **SessionState**: Runtime state management
3. **ActionExecutor**: Protocol for action execution
4. **OptionCollector**: Protocol for option collection
5. **NavigationController**: Protocol for navigation
6. **StorageAdapter**: Protocol for state persistence
7. **UIRenderer**: Protocol for UI implementation

### 3.3 Execution Model

1. **Stateless by Default**: Each execution is independent
2. **Optional Persistence**: Session continuity when needed
3. **Memory-Only State**: State exists only during execution
4. **Domain Responsibility**: Domains manage their own persistent state

## 4. User Stories

### 4.1 Developer Using YAML Definition
**As a** developer
**I want to** define simple workflows in YAML
**So that** I can create wizards without writing code

**Acceptance Criteria:**
- Can define branches, actions, options, and menus in YAML
- YAML is validated at load time
- Errors provide clear feedback about definition issues

### 4.2 Developer Using Python Decorators
**As a** developer with complex logic
**I want to** implement wizards in Python
**So that** I can use custom validation and business logic

**Acceptance Criteria:**
- Can use decorators to define wizards, branches, and actions
- Full access to SessionState for complex operations
- Type checking catches errors at development time

### 4.3 End User Running Wizard
**As an** end user
**I want to** run wizards with clear navigation
**So that** I can complete tasks without memorizing commands

**Acceptance Criteria:**
- Clear presentation of available options
- Navigation between branches is intuitive
- Input validation provides helpful error messages
- Can quit or go back at any point

## 5. Technical Requirements

### 5.1 Language & Runtime
- Python 3.11+ (for better type hints and error messages)
- Full MyPy strict mode compliance
- Async/await support throughout

### 5.2 Dependencies
- **pydantic**: Model validation and serialization
- **pyyaml**: YAML parsing
- **click** or **typer**: CLI framework (TBD)
- **asyncio**: Async execution

### 5.3 Type Safety Requirements
- No untyped functions
- Explicit return types
- Proper use of Optional, Union, Literal
- Runtime checkable protocols
- NewType for semantic distinctions

### 5.4 Performance Requirements
- Wizard loading: < 100ms
- Action execution: No overhead beyond subprocess/function call
- Memory usage: < 50MB for typical wizard

## 6. Success Metrics

### 6.1 Developer Experience
- Zero runtime type errors when MyPy passes
- < 5 minutes to create simple YAML wizard
- < 30 minutes to implement complex Python wizard

### 6.2 User Experience
- Zero crashes from type errors
- Clear error messages for validation failures
- Intuitive navigation without documentation

### 6.3 Code Quality
- 100% type coverage
- 90%+ test coverage
- All ADRs documented

## 7. Decisions & Constraints

See linked ADRs:
- [ADR-001: Stateless Execution Model](./adrs/ADR-001-stateless-execution.md)
- [ADR-002: Hybrid Definition System](./adrs/ADR-002-hybrid-definitions.md)
- [ADR-003: Subprocess for Shell Execution](./adrs/ADR-003-subprocess-execution.md)
- [ADR-004: Branch-Level UI Protocol](./adrs/ADR-004-branch-ui-protocol.md)
- [ADR-005: Type System Design](./adrs/ADR-005-type-system.md)

## 8. Future Considerations

### 8.1 Rust Migration
- Protocol-based design enables trait mapping
- Type system maps to Rust types
- Subprocess execution remains similar

### 8.2 Potential Enhancements
- Hook system for pre/post execution
- Cross-project wizard navigation
- Remote execution support
- Transaction/rollback for actions
- Shell session management (tmux)

## 9. Implementation Plan

### Phase 1: Core Type System
1. Implement type definitions from spec
2. Create Pydantic models
3. Set up MyPy configuration

### Phase 2: Definition Loading
1. YAML/JSON parser and validator
2. Python decorator system
3. Definition validation

### Phase 3: Execution Engine
1. Stateless execution engine
2. Subprocess executor
3. Navigation controller

### Phase 4: CLI Entry Point
1. Click/Typer integration
2. Wizard discovery
3. Basic error handling

### Phase 5: Testing & Documentation
1. Unit tests for all components
2. Integration tests for wizards
3. User documentation

## 10. Appendices

### 10.1 Example YAML Wizard
```yaml
name: simple-setup
version: 1.0.0
entry_branch: main

branches:
  - id: main
    name: Simple Setup
    actions:
      - id: check
        type: bash
        command: echo "Checking system..."
```

### 10.2 Example Python Wizard
```python
@wizard(name="complex-setup", version="1.0.0")
class ComplexWizard:
    @branch(id="main", entry=True)
    class MainBranch:
        @action(id="validate")
        async def validate(self, state: SessionState) -> ActionResult:
            # Complex logic here
            return ActionResult(success=True)
```

---

**Document Version**: 1.0.0
**Date**: 2024-01-18
**Author**: Pattern Stack Team
**Status**: Draft