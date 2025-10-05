# ADR-008: Wizard Type System Architecture

## Status
Accepted

## Context
CLI-4 requires defining the core type system for wizard configuration. We needed to decide how to structure types, handle extensibility, integrate with the parser system, and manage state across the framework.

## Decision
We will implement a **comprehensive wizard type system** with the following design choices:

### 1. Framework Architecture
CLI Patterns is a **framework, not an application**. Users install it and create their own wizard configurations via YAML or Python.

### 2. Discriminated Unions for Extensibility
Use discriminated unions NOW for type-safe extensibility:
```python
class BashActionConfig(BaseConfig):
    type: Literal["bash"] = "bash"
    command: str

class PythonActionConfig(BaseConfig):
    type: Literal["python"] = "python"
    module: str
    function: str

ActionConfigUnion = Union[BashActionConfig, PythonActionConfig]
```

Add registry system LATER when users need custom types beyond what we provide.

### 3. Tree Navigation (MVP)
- Menus point to target branches (tree structure)
- Navigation history tracked for "back" functionality
- Graph navigation (any→any, cycles, conditions) deferred to future tickets
- Easily extensible: add optional fields to MenuConfig later

### 4. Separation of Concerns
Keep actions, options, and menus separate:
- **Actions**: Execute something (bash, python, etc.)
- **Options**: Configure state (paths, selections, settings)
- **Menus**: Navigate between branches

Do NOT conflate (e.g., no actions in menus). Sequences/chaining added later if needed.

### 5. Built-in System Commands
Framework provides system commands automatically:
- `back` - Navigate to previous branch via history
- `quit`/`exit` - Exit wizard
- `help` - Context-sensitive help

These are NOT defined in YAML/Python configs; they're always available.

### 6. Unified SessionState
Single state model shared between wizard and parser:
```python
class SessionState(StrictModel):
    # Wizard state
    current_branch: BranchId
    navigation_history: list[BranchId]
    option_values: dict[OptionKey, StateValue]

    # Parser state
    parse_mode: ParseMode
    command_history: list[str]

    # Shared
    variables: dict[str, Any]
```

Replaces parser's separate `Context` type. Both systems read/write to SessionState.

### 7. Global State with Namespacing
- All option values stored globally in `option_values` dict
- Options flow between branches by default
- Users can namespace options if isolation needed: `"main.dev_schema"` vs `"models.dev_schema"`
- Per-branch state scoping deferred to future if needed

### 8. BaseConfig with Metadata
All config types inherit from BaseConfig:
```python
class BaseConfig(StrictModel):
    metadata: dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)
```

Enables introspection, filtering, documentation generation, and custom tooling.

### 9. StateValue as JsonValue
Use `JsonValue` type (anything JSON-serializable) instead of limited union:
- Supports primitives: str, int, float, bool, None
- Supports collections: lists, dicts
- Supports nesting
- Aligns with YAML/JSON definition loading

### 10. Specific Result Types
Each protocol operation returns a specific result type:
- `ActionResult` - for action execution
- `CollectionResult` - for option collection
- `NavigationResult` - for navigation

Provides structured success/failure with error messages.

## Consequences

### Positive
- **Type safety**: Full MyPy strict mode compliance with discriminated unions
- **Extensibility**: Easy to add new action/option types without breaking changes
- **Integration**: Parser and wizard share state seamlessly
- **Clarity**: Clear separation between actions, options, menus
- **Evolution path**: Tree→graph, static→dynamic, simple→complex
- **Framework flexibility**: Users configure their own wizards
- **Introspection**: Metadata enables tooling and documentation

### Negative
- **Initial complexity**: More upfront type definitions than minimal approach
- **Migration**: Parser Context must be migrated to SessionState
- **Learning curve**: Discriminated unions require understanding
- **Global state**: Potential for unexpected sharing between branches

### Neutral
- Tree navigation sufficient for MVP, graph deferred
- Registry system deferred until users need custom types
- Per-branch state scoping deferred unless requested

## Implementation Plan

### Phase 1: Core Types (`core/types.py`)
- Semantic types: `BranchId`, `ActionId`, `OptionKey`, `MenuId`
- Factory functions with optional validation
- Type guards for runtime checking
- `StateValue = JsonValue`

### Phase 2: Models (`core/models.py`)
- `BaseConfig` with metadata/tags
- Discriminated unions: `ActionConfigUnion`, `OptionConfigUnion`
- `BranchConfig`, `MenuConfig`, `WizardConfig`
- `SessionState` (unified wizard + parser)
- Result types: `ActionResult`, `CollectionResult`, `NavigationResult`

### Phase 3: Protocols (`core/protocols.py`)
- `ActionExecutor`, `OptionCollector`, `NavigationController`
- All use `SessionState` and return specific result types

### Phase 4: Tests
- Semantic type validation
- Model validation (Pydantic rules)
- Discriminated union discrimination
- SessionState integration

## Future Work

### Near-term (Next Sprint)
- Migrate parser Context to SessionState (CLI-XX)
- YAML loader implementation (CLI-XX)
- Python decorator system (CLI-XX)

### Mid-term (Later Sprints)
- Action type registry (CLI-XX)
- Option type registry (CLI-XX)
- Graph navigation support (CLI-XX)
- Project discovery system (CLI-XX)

### Long-term (Future)
- Per-branch state scoping (if needed)
- Action sequences/chaining (if needed)
- Conditional navigation (if needed)
- Remote execution support (if needed)

## References
- [ADR-005: Type System Design](./ADR-005-type-system.md)
- [ADR-002: Hybrid Definition System](./ADR-002-hybrid-definitions.md)
- [ADR-004: Branch-Level UI Protocol](./ADR-004-branch-ui-protocol.md)
- [ADR-007: Composable Parser System](./ADR-007-composable-parser-system.md)
- CLI-4 Refinement Session (2025-09-30)

## Example: DBT Wizard

```yaml
name: dbt-wizard
version: 1.0.0
entry_branch: main

branches:
  - id: main
    title: "DBT Project Manager"

    options:
      - id: dbt_project
        type: path
        name: "DBT Project Path"
        default: "./dbt_project.yml"

      - id: dev_schema
        type: string
        name: "Dev Schema"
        default: "dbt_dev"

    actions:
      - id: dbt_run
        type: bash
        name: "Run DBT"
        command: "dbt run --project-dir ${option:dbt_project}"

      - id: dbt_build
        type: bash
        name: "Build DBT"
        command: "dbt build --project-dir ${option:dbt_project}"

    menus:
      - id: menu_projects
        label: "Manage Projects"
        target: dbt_projects

      - id: menu_models
        label: "Browse Models"
        target: dbt_models

  - id: dbt_projects
    title: "DBT Projects"
    # back, quit, help automatically available
    actions:
      - id: list_projects
        type: bash
        name: "List Projects"
        command: "find . -name dbt_project.yml"
```

This demonstrates:
- Tree navigation (main → projects, main → models)
- Options flow globally (dbt_project usable in any branch)
- Actions use variable interpolation (${option:dbt_project})
- Built-in commands (back) not defined in YAML
