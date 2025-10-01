# 📋 MVP Completion Issues for CLI Patterns

## 🎯 Critical Path Issues (Must Have for MVP)

---

### **CLI-30: Implement YAML Wizard Definition Loader**
**Priority:** P0 - Critical Blocker
**Effort:** M (4-8 hours)
**Dependencies:** None (can start immediately)

**Description:**
Create a YAML loader that transforms wizard YAML files into validated `WizardConfig` instances, similar to the existing theme loader.

**Acceptance Criteria:**
- [ ] Create `src/cli_patterns/config/wizard_loader.py`
- [ ] Implement `load_wizard_from_yaml(path: Path) -> WizardConfig`
- [ ] Support environment variable expansion (${ENV_VAR} syntax)
- [ ] Validate all branch/action/option references exist
- [ ] Provide clear error messages for invalid YAML
- [ ] Add unit tests with valid/invalid YAML examples
- [ ] Create `examples/simple_wizard.yaml` demonstrating all features

**Technical Notes:**
- Follow pattern from `theme_loader.py`
- Use Pydantic's discriminated union parsing
- Ensure type discrimination works for action/option types

---

### **CLI-31: Implement Core Protocol Implementations**
**Priority:** P0 - Critical Blocker
**Effort:** L (1-2 days)
**Dependencies:** CLI-30 (for testing with real wizards)

**Description:**
Create concrete implementations of the three core protocols to enable wizard execution.

**Acceptance Criteria:**
- [ ] Create `src/cli_patterns/execution/action_executor.py`:
  - `BasicActionExecutor` class implementing `ActionExecutor` protocol
  - Handle `BashActionConfig` using existing `SubprocessExecutor`
  - Handle `PythonActionConfig` with dynamic import/execution
  - Return proper `ActionResult` with success/error states

- [ ] Create `src/cli_patterns/execution/option_collector.py`:
  - `InteractiveOptionCollector` implementing `OptionCollector` protocol
  - Use prompt_toolkit for interactive prompts
  - Support all 5 option types with appropriate UI
  - Validate input according to option config
  - Return `CollectionResult` with collected value

- [ ] Create `src/cli_patterns/execution/navigation_controller.py`:
  - `TreeNavigationController` implementing `NavigationController` protocol
  - Manage branch history for "back" navigation
  - Validate navigation targets exist
  - Update `SessionState` correctly
  - Return `NavigationResult` with success/error

**Technical Notes:**
- Leverage existing design system for styled prompts
- Use existing validation from option models
- Ensure async compatibility where needed

---

### **CLI-32: Build Wizard Execution Engine**
**Priority:** P0 - Critical Blocker
**Effort:** L (1-2 days)
**Dependencies:** CLI-31

**Description:**
Create the core engine that orchestrates wizard execution by coordinating protocol implementations.

**Acceptance Criteria:**
- [ ] Create `src/cli_patterns/execution/engine.py`
- [ ] Implement `WizardEngine` class with:
  - `__init__(wizard: WizardConfig, state: SessionState | None = None)`
  - `async run()` - main execution loop
  - `execute_action(action_id: ActionId)` - run action via executor
  - `collect_option(option_key: OptionKey)` - collect via collector
  - `navigate_to(branch_id: BranchId)` - navigate via controller
  - `get_current_branch() -> BranchConfig`
- [ ] Handle state persistence between actions
- [ ] Support variable interpolation (`${option:key}`, `${var:name}`)
- [ ] Error handling with graceful recovery
- [ ] Add comprehensive unit tests

**Technical Notes:**
- Engine should be stateless (state passed in)
- Use dependency injection for protocol implementations
- Support both sync and async execution modes

---

### **CLI-33: Integrate Wizard System into Interactive Shell**
**Priority:** P0 - Critical Blocker
**Effort:** M (4-8 hours)
**Dependencies:** CLI-32

**Description:**
Connect the wizard engine to the interactive shell, adding wizard-specific commands.

**Acceptance Criteria:**
- [ ] Modify `src/cli_patterns/ui/shell.py` to:
  - Accept optional wizard path on startup
  - Load wizard via YAML loader
  - Initialize `WizardEngine` with wizard
  - Show current branch in prompt

- [ ] Add wizard commands to shell:
  - `load <path>` - load wizard YAML file
  - `navigate <branch>` - go to specific branch
  - `back` - navigate to previous branch
  - `list branches` - show all branches
  - `list actions` - show current branch actions
  - `run <action>` - execute specific action
  - `list options` - show current branch options
  - `set <option>` - set option value
  - `show state` - display current SessionState

- [ ] Update command registry with new commands
- [ ] Add tab completion for branch/action/option names
- [ ] Integration tests for wizard commands

**Technical Notes:**
- Maintain backward compatibility with non-wizard mode
- Use existing parser pipeline for command routing
- Leverage design system for output formatting

---

### **CLI-34: Create Example Wizards and Quick Start Guide**
**Priority:** P1 - High
**Effort:** S (2-4 hours)
**Dependencies:** CLI-33

**Description:**
Create working example wizards and documentation for users to get started quickly.

**Acceptance Criteria:**
- [ ] Create `examples/wizards/` directory with:
  - `simple_demo.yaml` - basic wizard showing all features
  - `dbt_wizard.yaml` - DBT project management (from ADR-008)
  - `project_setup.yaml` - Pattern Stack project setup wizard

- [ ] Create `docs/quickstart.md` with:
  - Installation instructions
  - Running your first wizard
  - YAML wizard format reference
  - Common patterns and tips

- [ ] Update main README with quickstart section
- [ ] Ensure all examples actually run without errors

**Technical Notes:**
- Examples should demonstrate real use cases
- Include comments explaining YAML structure
- Test examples as part of CI

---

### **CLI-35: Add Python Decorator System for Wizard Definition**
**Priority:** P1 - High
**Effort:** L (1-2 days)
**Dependencies:** CLI-32 (need engine to test)

**Description:**
Implement Python decorators as an alternative to YAML for defining wizards.

**Acceptance Criteria:**
- [ ] Create `src/cli_patterns/decorators.py` with:
  - `@wizard(name, version)` - class decorator
  - `@branch(id, title, description)` - method decorator
  - `@action(id, name)` - method decorator for actions
  - `@option(key, type, **config)` - parameter decorator

- [ ] Decorators should build `WizardConfig` at runtime
- [ ] Support async methods for actions
- [ ] Type hints preserved and validated
- [ ] Create `examples/wizards/python_wizard.py` example

**Technical Notes:**
- Use Python's inspect module for introspection
- Validate at decoration time, not runtime
- Maintain full type safety with MyPy

---

## 📊 Summary

**Total New Issues:** 6

**Critical Path (P0):**
- CLI-30: YAML Loader (4-8 hours)
- CLI-31: Protocol Implementations (1-2 days)
- CLI-32: Execution Engine (1-2 days)
- CLI-33: Shell Integration (4-8 hours)

**High Priority (P1):**
- CLI-34: Examples & Docs (2-4 hours)
- CLI-35: Python Decorators (1-2 days)

**Total Estimated Effort:** 5-7 days for MVP

**Recommended Sequence:**
1. Start with CLI-30 (YAML loader) - validates type system works
2. Then CLI-31 (protocols) - enables execution
3. Then CLI-32 (engine) - brings it together
4. Then CLI-33 (shell) - makes it usable
5. Finally CLI-34 (examples) - demonstrates value
6. Optional CLI-35 (decorators) - alternative to YAML

These issues will take you from "beautiful infrastructure" to "working wizard system" that users can actually use.

## 🚀 Current Status (After CLI-4-5-6 Merge)

### ✅ What's Complete
- **Core Type System** (100%): All semantic types, models, protocols defined
- **Design System** (100%): Full theming, components, tokens
- **Parser System** (100%): Command parsing with fuzzy matching
- **Subprocess Executor** (100%): Secure async execution with themed output
- **Interactive Shell** (40%): Basic shell works, needs wizard integration
- **Security** (100%): Command injection prevention, DoS protection

### ❌ What's Missing for MVP
- **Definition Loading** (0%): No way to load wizard YAML/Python
- **Execution Engine** (20%): Only subprocess executor exists
- **Protocol Implementations** (0%): Protocols defined but not implemented
- **Navigation System** (0%): No branch navigation
- **Option Collection** (0%): No UI for collecting user input
- **Wizard Commands** (0%): Shell doesn't know about wizards

## 🎯 MVP Definition

A working MVP means:
1. User can define a wizard in YAML
2. User can load and run the wizard interactively
3. User can navigate between branches
4. User can execute actions (bash/python)
5. User can provide input via options
6. System maintains state throughout session

After completing these 6 issues, CLI Patterns will be a **functional wizard framework** ready for real use cases.