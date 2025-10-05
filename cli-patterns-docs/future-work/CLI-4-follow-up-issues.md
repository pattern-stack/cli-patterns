# CLI-4 Follow-Up Issues

This document tracks future work items identified during CLI-4 refinement (2025-09-30). These will be converted to actual issues as needed.

## Immediate Next Steps (Week 2 continuation)

### Migrate Parser Context to SessionState
**Priority: High** (blocks integration)

**Description:**
Update the parser system to use the unified `SessionState` from core instead of its own `Context` type.

**Tasks:**
- Update `ui/parser/types.py` to import and use `SessionState` from `cli_patterns.core.models`
- Migrate `Context` fields to `SessionState` structure
- Update all parser implementations to use `SessionState`
- Update parser tests to use `SessionState`
- Remove old `Context` class

**Dependencies:** CLI-4 complete

**Estimated Effort:** ~150-200 lines changed

---

### YAML Definition Loader
**Priority: High** (enables YAML wizards)

**Description:**
Implement a loader that parses YAML files into `WizardConfig` objects with full validation.

**Tasks:**
- Create `definitions/yaml_loader.py`
- Parse YAML to Pydantic models (automatic validation)
- Handle variable interpolation syntax (`${option:...}`, `${var:...}`)
- Provide clear error messages for invalid YAML
- Support both file paths and string input
- Add comprehensive tests (valid/invalid YAML)

**Example:**
```python
from cli_patterns.definitions import load_yaml

wizard = load_yaml("./my-wizard.yml")
# Returns WizardConfig instance
```

**Dependencies:** CLI-4 complete

**Estimated Effort:** ~300-400 lines

---

### Python Decorator System
**Priority: High** (enables Python wizards)

**Description:**
Implement decorator-based API for defining wizards in Python code. Decorators introspect classes/functions and build `WizardConfig` instances.

**Tasks:**
- Create `definitions/decorators.py`
- Implement `@wizard` decorator (class-level)
- Implement `@branch` decorator (class or function)
- Implement `@action` decorator (method or function)
- Implement `@option` decorator (class attribute or parameter)
- Implement `@menu` decorator (method or function)
- Support both class-based and functional styles
- Build `WizardConfig` from decorated objects
- Add comprehensive tests

**Example:**
```python
@wizard(name="my-wizard", version="1.0.0", entry="main")
class MyWizard:
    pass

@branch(wizard=MyWizard, id="main", title="Main Menu")
class MainBranch:
    @option(id="project_path", type="path", default=".")
    project_path: str

    @action(name="Run Command")
    async def run(self, state: SessionState) -> ActionResult:
        return ActionResult(success=True)

    @menu(label="Settings", target="settings")
    def settings_menu(self):
        pass
```

**Dependencies:** CLI-4 complete

**Estimated Effort:** ~500-600 lines

---

## Core Functionality (Week 3+)

### Bash Action Executor
**Description:**
Implement `ActionExecutor` protocol for `BashActionConfig` type.

**Tasks:**
- Create `execution/bash_executor.py`
- Integrate with existing subprocess executor (CLI-9)
- Support variable interpolation in commands
- Handle environment variables
- Stream output with theming
- Return `ActionResult`
- Tests

**Dependencies:** CLI-4, YAML/Python loaders

**Estimated Effort:** ~200-250 lines

---

### Python Action Executor
**Description:**
Implement `ActionExecutor` protocol for `PythonActionConfig` type.

**Tasks:**
- Create `execution/python_executor.py`
- Dynamic module and function loading
- Pass `SessionState` to functions
- Error handling and traceback capture
- Return `ActionResult`
- Tests

**Dependencies:** CLI-4, YAML/Python loaders

**Estimated Effort:** ~150-200 lines

---

### Option Collectors Suite
**Description:**
Implement `OptionCollector` protocol for all option types.

**Tasks:**
- Create `ui/collectors/` directory
- Implement collector for each option type:
  - `string_collector.py` - Text input with validation
  - `select_collector.py` - Single selection from choices
  - `path_collector.py` - File/directory picker with validation
  - `number_collector.py` - Numeric input with range validation
  - `boolean_collector.py` - Yes/no prompt
- Integration with prompt_toolkit
- Return `CollectionResult`
- Tests for each collector

**Dependencies:** CLI-4

**Estimated Effort:** ~400-500 lines

---

### Navigation Controller
**Description:**
Implement `NavigationController` protocol for branch navigation.

**Tasks:**
- Create `execution/navigation_controller.py`
- Branch switching logic
- Navigation history management
- System commands handling (back, quit, help)
- Validation of navigation targets
- Return `NavigationResult`
- Tests

**Dependencies:** CLI-4

**Estimated Effort:** ~150-200 lines

---

### CLI Entry Point
**Description:**
Main entry point that loads wizard definitions and starts the interactive shell.

**Tasks:**
- Create `cli.py` main entry point
- Load wizard from YAML or Python
- Initialize `SessionState`
- Wire together all components (parser, executors, collectors, navigation)
- Start interactive shell with wizard context
- Command routing logic
- Error handling
- Tests

**Dependencies:** All above executors/collectors/controllers

**Estimated Effort:** ~300-400 lines

---

## Future Enhancements (Post-MVP)

### Action Type Registry
**Description:**
Plugin system allowing users to register custom action types.

**Tasks:**
- Create `definitions/action_registry.py`
- Registration API: `register_action_type(name, config_class, executor_class)`
- Dynamic type loading
- Extend `ActionConfigUnion` at runtime
- Documentation for plugin authors
- Tests

**Estimated Effort:** ~200-300 lines

---

### Option Type Registry
**Description:**
Plugin system allowing users to register custom option types.

**Tasks:**
- Create `definitions/option_registry.py`
- Registration API: `register_option_type(name, config_class, collector_class)`
- Dynamic type loading
- Extend `OptionConfigUnion` at runtime
- Documentation for plugin authors
- Tests

**Estimated Effort:** ~200-300 lines

---

### Graph Navigation Support
**Description:**
Extend menu system to support conditional navigation, cycles, and dynamic targets.

**Tasks:**
- Add optional fields to `MenuConfig`:
  - `condition: Optional[str]` - Show menu only if condition met
  - `dynamic_target: Optional[Callable]` - Compute target at runtime
  - `preserve_state: bool` - Keep state when navigating
  - `clear_history: bool` - Clear history on navigation
- Update navigation controller to handle conditions
- Add cycle detection
- Tests for complex navigation patterns

**Dependencies:** Navigation Controller complete

**Estimated Effort:** ~200-250 lines

---

### Project Discovery System
**Description:**
Auto-discover project structures and dynamically instantiate wizards.

**Tasks:**
- Create `discovery/` module
- Define discovery protocol
- Implement common patterns (e.g., find all `dbt_project.yml` files)
- Factory pattern for dynamic wizard creation
- Configuration for discovery rules
- Tests

**Example:**
```python
projects = discover_dbt_projects(os.getcwd())
wizard = create_dbt_wizard(projects)  # Dynamic WizardConfig
```

**Dependencies:** Python decorator system, executors

**Estimated Effort:** ~300-400 lines

---

## Notes

- These issues will be created in Linear as needed based on development priorities
- Effort estimates are approximate and may change during refinement
- Dependencies must be completed before starting dependent work
- All work must maintain MyPy strict mode compliance
- All work requires comprehensive test coverage
