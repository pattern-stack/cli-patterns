# CLI Patterns MVP Implementation Tickets

## Overview
This document outlines the implementation tickets for CLI Patterns MVP, organized by phase as defined in the PRD. Each ticket includes acceptance criteria, dependencies, and effort estimates.

**Effort Scale**:
- XS (1-2 hours)
- S (2-4 hours)
- M (4-8 hours)
- L (1-2 days)
- XL (3-5 days)

---

## Phase 1: Core Type System

### CLI-001: Setup Project Structure and Configuration
**Priority**: P0 - Blocker
**Effort**: S
**Dependencies**: None

**Description**: Initialize project with proper structure and development configuration.

**Tasks**:
- Create project directory structure
- Setup `pyproject.toml` with dependencies
- Configure MyPy for strict mode
- Setup pre-commit hooks for type checking
- Create `.gitignore` and README

**Acceptance Criteria**:
- [ ] MyPy runs in strict mode without errors
- [ ] Project installs cleanly with `pip install -e .`
- [ ] Pre-commit hooks run type checking

---

### CLI-002: Implement Core Type Definitions
**Priority**: P0 - Blocker
**Effort**: M
**Dependencies**: CLI-001

**Description**: Implement semantic types and base type definitions from the spec.

**Tasks**:
- Create `core/types.py` with NewType definitions
- Implement `BranchId`, `ActionId`, `OptionKey`, etc.
- Define `StateValue` union type
- Add type aliases for complex types

**Acceptance Criteria**:
- [ ] All semantic types defined with NewType
- [ ] Type aliases improve readability
- [ ] MyPy validates all type definitions

---

### CLI-003: Create Pydantic Base Models
**Priority**: P0 - Blocker
**Effort**: L
**Dependencies**: CLI-002

**Description**: Implement core Pydantic models for validation and serialization.

**Tasks**:
- Create `StrictModel` base class
- Implement `WizardConfig` model
- Implement `BranchConfig` model
- Implement `SessionState` model
- Add validators for all models

**Acceptance Criteria**:
- [ ] Models validate input correctly
- [ ] Serialization/deserialization works
- [ ] Custom validators enforce business rules
- [ ] 100% type coverage

---

### CLI-004: Implement Action Models with Discriminated Unions
**Priority**: P0 - Blocker
**Effort**: M
**Dependencies**: CLI-003

**Description**: Create action configuration models using discriminated unions.

**Tasks**:
- Implement `BaseActionConfig` abstract model
- Create `BashActionConfig` with `type: Literal["bash"]`
- Create `PythonActionConfig` with `type: Literal["python"]`
- Create `ConfigActionConfig` with `type: Literal["config"]`
- Define `ActionConfigUnion` discriminated union
- Implement `ActionResult` model

**Acceptance Criteria**:
- [ ] Discriminated unions work with Pydantic
- [ ] Type discrimination is automatic
- [ ] Each action type validates correctly

---

### CLI-005: Implement Option Models with Type Safety
**Priority**: P0 - Blocker
**Effort**: M
**Dependencies**: CLI-003

**Description**: Create option configuration models for user input collection.

**Tasks**:
- Implement `BaseOptionConfig` abstract model
- Create typed option configs (TextOption, NumberOption, etc.)
- Implement validation rules per type
- Define `OptionConfigUnion` discriminated union
- Add choice validation for select options

**Acceptance Criteria**:
- [ ] Each option type has proper validation
- [ ] Default values are type-checked
- [ ] Pattern validation works for text options
- [ ] Range validation works for number options

---

### CLI-006: Define Core Protocols
**Priority**: P0 - Blocker
**Effort**: M
**Dependencies**: CLI-002, CLI-003

**Description**: Define runtime-checkable protocols for extensibility.

**Tasks**:
- Create `ActionExecutor` protocol
- Create `OptionCollector` protocol
- Create `NavigationController` protocol
- Create `StorageAdapter` protocol
- Create `UIRenderer` protocol
- Make all protocols `@runtime_checkable`

**Acceptance Criteria**:
- [ ] Protocols are runtime checkable
- [ ] Protocol methods fully typed
- [ ] Protocols documented with docstrings

---

## Phase 2: Definition Loading

### CLI-007: Implement YAML Definition Parser
**Priority**: P0 - Blocker
**Effort**: L
**Dependencies**: CLI-003, CLI-004, CLI-005

**Description**: Build YAML parser that creates validated WizardConfig instances.

**Tasks**:
- Create `definitions/yaml_loader.py`
- Implement YAML to Pydantic model conversion
- Add schema validation
- Handle parsing errors gracefully
- Support environment variable expansion

**Acceptance Criteria**:
- [ ] Valid YAML produces WizardConfig
- [ ] Invalid YAML provides clear errors
- [ ] All model types supported
- [ ] Environment variables expanded

---

### CLI-008: Create Definition Registry System
**Priority**: P1 - High
**Effort**: M
**Dependencies**: CLI-007

**Description**: Build registry for discovering and loading wizard definitions.

**Tasks**:
- Create `definitions/registry.py`
- Implement wizard discovery from directories
- Support both YAML and Python definitions
- Add caching for loaded definitions
- Implement version management

**Acceptance Criteria**:
- [ ] Registry discovers all wizards in path
- [ ] Wizards loadable by name
- [ ] Version conflicts detected
- [ ] Caching improves performance

---

### CLI-009: Implement Python Decorator System
**Priority**: P1 - High
**Effort**: L
**Dependencies**: CLI-003, CLI-006

**Description**: Create decorator-based wizard definition system for Python.

**Tasks**:
- Create `@wizard` class decorator
- Create `@branch` class decorator
- Create `@action` method decorator
- Create `@option` decorator for inputs
- Build decorator-to-model converter

**Acceptance Criteria**:
- [ ] Decorators produce valid WizardConfig
- [ ] Type hints preserved through decoration
- [ ] Async methods supported
- [ ] Validation happens at decoration time

---

### CLI-010: Build Definition Validation System
**Priority**: P1 - High
**Effort**: M
**Dependencies**: CLI-007, CLI-009

**Description**: Comprehensive validation for wizard definitions.

**Tasks**:
- Validate branch references exist
- Validate entry branch specified
- Check for circular dependencies
- Validate action prerequisites
- Ensure unique IDs within scope

**Acceptance Criteria**:
- [ ] Invalid definitions rejected with clear errors
- [ ] All references validated
- [ ] Circular dependencies detected
- [ ] Performance acceptable for large wizards

---

## Phase 3: Execution Engine

### CLI-011: Implement Stateless Execution Engine
**Priority**: P0 - Blocker
**Effort**: L
**Dependencies**: CLI-003, CLI-006

**Description**: Build core execution engine for running wizards.

**Tasks**:
- Create `execution/engine.py`
- Implement state management
- Add branch navigation logic
- Implement action execution flow
- Add error handling and recovery

**Acceptance Criteria**:
- [ ] Engine executes wizard flow correctly
- [ ] State managed properly during execution
- [ ] Navigation between branches works
- [ ] Errors handled gracefully

---

### CLI-012: Create Subprocess Action Executor
**Priority**: P0 - Blocker
**Effort**: M
**Dependencies**: CLI-004, CLI-011

**Description**: Implement subprocess-based shell command execution.

**Tasks**:
- Create `execution/subprocess_executor.py`
- Implement `asyncio.create_subprocess_shell` wrapper
- Add timeout support
- Capture stdout/stderr properly
- Handle environment variables

**Acceptance Criteria**:
- [ ] Shell commands execute correctly
- [ ] Output captured and returned
- [ ] Timeouts work as expected
- [ ] Environment variables passed through

---

### CLI-013: Build Python Action Executor
**Priority**: P1 - High
**Effort**: M
**Dependencies**: CLI-004, CLI-011

**Description**: Execute Python functions as wizard actions.

**Tasks**:
- Create `execution/python_executor.py`
- Support sync and async functions
- Pass SessionState to functions
- Handle return values properly
- Add exception handling

**Acceptance Criteria**:
- [ ] Python functions execute correctly
- [ ] Both sync/async functions work
- [ ] State accessible in functions
- [ ] Exceptions handled gracefully

---

### CLI-014: Implement Navigation Controller
**Priority**: P0 - Blocker
**Effort**: M
**Dependencies**: CLI-011

**Description**: Handle navigation between wizard branches.

**Tasks**:
- Create `execution/navigation.py`
- Implement branch history tracking
- Add "back" navigation support
- Handle menu-based navigation
- Validate navigation targets

**Acceptance Criteria**:
- [ ] Navigation between branches works
- [ ] History tracked correctly
- [ ] Back navigation functions properly
- [ ] Invalid navigation prevented

---

### CLI-015: Create State Observer System
**Priority**: P2 - Medium
**Effort**: S
**Dependencies**: CLI-003, CLI-011

**Description**: Implement observer pattern for state changes.

**Tasks**:
- Add observer support to SessionState
- Create state change events
- Implement subscriber notification
- Add filtering for specific keys

**Acceptance Criteria**:
- [ ] Observers notified of changes
- [ ] Event filtering works
- [ ] No memory leaks from observers
- [ ] Performance acceptable

---

## Phase 4: Interactive Shell

### CLI-016: Setup prompt_toolkit Integration
**Priority**: P0 - Blocker
**Effort**: M
**Dependencies**: CLI-011

**Description**: Initialize prompt_toolkit for interactive terminal UI.

**Tasks**:
- Create `ui/interactive_shell.py`
- Setup PromptSession with history
- Configure key bindings
- Add basic styling/theme
- Implement main event loop

**Acceptance Criteria**:
- [ ] Interactive prompt displays
- [ ] History works with arrow keys
- [ ] Ctrl+C/Ctrl+D handled properly
- [ ] Basic styling applied

---

### CLI-017: Implement Command Parser and Router
**Priority**: P0 - Blocker
**Effort**: L
**Dependencies**: CLI-016

**Description**: Parse and route interactive commands to appropriate handlers.

**Tasks**:
- Create command parser
- Implement command registry
- Add command validation
- Route commands to handlers
- Add command aliases

**Acceptance Criteria**:
- [ ] Commands parsed correctly
- [ ] Invalid commands show helpful errors
- [ ] Command routing works
- [ ] Aliases function properly

---

### CLI-018: Build Interactive Navigation Commands
**Priority**: P0 - Blocker
**Effort**: M
**Dependencies**: CLI-014, CLI-017

**Description**: Implement navigation commands for interactive mode.

**Tasks**:
- Implement `navigate <branch>` command
- Implement `back` command
- Implement `jump <branch>` command
- Add `list branches` command
- Show current branch in prompt

**Acceptance Criteria**:
- [ ] All navigation commands work
- [ ] Current branch shown in prompt
- [ ] Invalid navigation handled
- [ ] Branch list displays correctly

---

### CLI-019: Create Action Execution Commands
**Priority**: P0 - Blocker
**Effort**: M
**Dependencies**: CLI-012, CLI-013, CLI-017

**Description**: Commands for running wizard actions interactively.

**Tasks**:
- Implement `run <action>` command
- Implement `list actions` command
- Add action execution feedback
- Show progress for long-running actions
- Handle action prerequisites

**Acceptance Criteria**:
- [ ] Actions execute from commands
- [ ] Progress shown during execution
- [ ] Output displayed properly
- [ ] Prerequisites checked

---

### CLI-020: Implement Tab Completion System
**Priority**: P1 - High
**Effort**: M
**Dependencies**: CLI-017

**Description**: Add intelligent tab completion for commands and arguments.

**Tasks**:
- Create command completer
- Add branch name completion
- Add action name completion
- Implement contextual completion
- Add file path completion for relevant commands

**Acceptance Criteria**:
- [ ] Tab completion works for all commands
- [ ] Context-aware suggestions
- [ ] File paths complete properly
- [ ] Performance is responsive

---

### CLI-021: Build Interactive Option Collection
**Priority**: P0 - Blocker
**Effort**: L
**Dependencies**: CLI-005, CLI-016

**Description**: Implement UIRenderer protocol for interactive option collection.

**Tasks**:
- Create `ui/option_renderer.py`
- Implement text input with validation
- Implement select menus
- Add multi-select support
- Show validation errors inline

**Acceptance Criteria**:
- [ ] All option types supported
- [ ] Validation feedback immediate
- [ ] Default values shown
- [ ] Cancel/back supported

---

### CLI-022: Create Help System
**Priority**: P1 - High
**Effort**: M
**Dependencies**: CLI-017

**Description**: Comprehensive help system for interactive mode.

**Tasks**:
- Implement `help` command
- Add command-specific help
- Create contextual hints
- Add wizard documentation display
- Implement `?` as help alias

**Acceptance Criteria**:
- [ ] General help available
- [ ] Command-specific help works
- [ ] Contextual hints shown
- [ ] Documentation accessible

---

### CLI-023: Add Rich Output Formatting
**Priority**: P2 - Medium
**Effort**: M
**Dependencies**: CLI-016

**Description**: Enhanced terminal output with colors and formatting.

**Tasks**:
- Add color coding for output types
- Implement progress indicators
- Create formatted tables for lists
- Add emoji/icon support
- Implement status messages

**Acceptance Criteria**:
- [ ] Output is visually clear
- [ ] Colors used consistently
- [ ] Tables format properly
- [ ] Progress indicators work

---

## Phase 5: Testing & Documentation

### CLI-024: Create Unit Test Suite
**Priority**: P0 - Blocker
**Effort**: XL
**Dependencies**: All implementation tickets

**Description**: Comprehensive unit tests for all components.

**Tasks**:
- Test all type definitions
- Test model validation
- Test execution engine
- Test command parsing
- Test navigation logic

**Acceptance Criteria**:
- [ ] 90%+ code coverage
- [ ] All edge cases tested
- [ ] Tests run in CI
- [ ] No flaky tests

---

### CLI-025: Build Integration Test Framework
**Priority**: P1 - High
**Effort**: L
**Dependencies**: CLI-024

**Description**: Integration tests for complete wizard flows.

**Tasks**:
- Create test wizard definitions
- Test YAML loading and execution
- Test Python decorator wizards
- Test interactive shell commands
- Test error scenarios

**Acceptance Criteria**:
- [ ] End-to-end flows tested
- [ ] Both YAML and Python tested
- [ ] Interactive mode tested
- [ ] Error handling verified

---

### CLI-026: Write User Documentation
**Priority**: P1 - High
**Effort**: L
**Dependencies**: All implementation tickets

**Description**: User-facing documentation for CLI Patterns.

**Tasks**:
- Write getting started guide
- Document YAML wizard format
- Document Python decorators
- Create interactive command reference
- Add troubleshooting section

**Acceptance Criteria**:
- [ ] Complete user guide
- [ ] API reference generated
- [ ] Examples provided
- [ ] Published to docs site

---

### CLI-027: Create Example Wizards
**Priority**: P1 - High
**Effort**: M
**Dependencies**: CLI-007, CLI-009

**Description**: Example wizards demonstrating features.

**Tasks**:
- Create simple YAML wizard
- Create complex Python wizard
- Add Pattern Stack setup wizard
- Create tutorial wizard
- Include in package

**Acceptance Criteria**:
- [ ] Examples cover all features
- [ ] Well documented
- [ ] Actually useful wizards
- [ ] Tested and working

---

### CLI-028: Setup CI/CD Pipeline
**Priority**: P1 - High
**Effort**: M
**Dependencies**: CLI-001, CLI-024

**Description**: Automated testing and release pipeline.

**Tasks**:
- Setup GitHub Actions workflow
- Run tests on PR
- Run MyPy type checking
- Setup automated releases
- Add badge to README

**Acceptance Criteria**:
- [ ] Tests run automatically
- [ ] Type checking enforced
- [ ] Releases automated
- [ ] Status visible in README

---

## Summary

**Total Tickets**: 28

**By Priority**:
- P0 (Blocker): 14 tickets
- P1 (High): 10 tickets
- P2 (Medium): 4 tickets

**By Original Phase**:
- Phase 1 (Core Types): 6 tickets
- Phase 2 (Definitions): 4 tickets
- Phase 3 (Execution): 5 tickets
- Phase 4 (Interactive): 8 tickets
- Phase 5 (Testing): 5 tickets

**Estimated Total Effort**: ~15-20 developer days

## Implementation Order (REVISED FOR INCREMENTAL VALUE)

### Milestone 1: Minimal Interactive Shell (Week 1)
**Goal**: Get a basic interactive shell running that can execute hardcoded bash commands

**Tickets**:
- CLI-001: Setup Project Structure
- CLI-002: Core Type Definitions (minimal - just what's needed)
- CLI-003: Core Pydantic Models (WizardConfig, BranchConfig, SessionState only)
- CLI-004: Action Models (BashActionConfig only)
- CLI-016: Setup prompt_toolkit Integration
- CLI-017: Command Parser (basic commands only)
- CLI-012: Subprocess Action Executor

**Deliverable**: Can launch shell, type commands, run bash actions

### Milestone 2: YAML Wizards Working (Week 2)
**Goal**: Load and execute YAML-defined wizards interactively

**Tickets**:
- CLI-007: YAML Definition Parser
- CLI-011: Execution Engine (basic version)
- CLI-014: Navigation Controller
- CLI-018: Interactive Navigation Commands
- CLI-019: Action Execution Commands

**Deliverable**: Can load a YAML wizard and navigate/execute it

### Milestone 3: Full Type System & Options (Week 3)
**Goal**: Complete type safety and user input collection

**Tickets**:
- CLI-005: Option Models with Type Safety
- CLI-006: Core Protocols
- CLI-021: Interactive Option Collection
- CLI-020: Tab Completion System
- CLI-022: Help System

**Deliverable**: Full option collection, help, and tab completion

### Milestone 4: Python Decorators & Advanced Features (Week 4)
**Goal**: Support Python-defined wizards and remaining action types

**Tickets**:
- CLI-009: Python Decorator System
- CLI-013: Python Action Executor
- CLI-008: Definition Registry
- CLI-010: Definition Validation
- CLI-015: State Observer System
- CLI-023: Rich Output Formatting

**Deliverable**: Full feature set with both YAML and Python support

### Milestone 5: Production Ready (Week 5)
**Goal**: Testing, documentation, and polish

**Tickets**:
- CLI-024: Unit Test Suite
- CLI-025: Integration Tests
- CLI-026: User Documentation
- CLI-027: Example Wizards
- CLI-028: CI/CD Pipeline

**Deliverable**: Production-ready, tested, documented system

## Dependencies Graph

```
Foundation Layer:
CLI-001 → CLI-002 → CLI-003 → CLI-004/005 → CLI-006
                          ↓
Definition Layer:         ↓
                   CLI-007/009 → CLI-008 → CLI-010
                          ↓
Execution Layer:          ↓
                   CLI-011 → CLI-012/013 → CLI-014 → CLI-015
                          ↓
Interactive Layer:        ↓
                   CLI-016 → CLI-017 → CLI-018/019/020 → CLI-021/022/023
                          ↓
Testing Layer:            ↓
                   CLI-024 → CLI-025 → CLI-026/027/028
```

---

**Document Version**: 1.0.0
**Last Updated**: 2025-09-18
**Status**: Ready for Review