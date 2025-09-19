# ADR-002: Hybrid Definition System

## Status
Accepted

## Context
Wizard definitions need to support two distinct use cases:
1. Simple, declarative workflows (like dbt) that can be fully defined in configuration
2. Complex workflows requiring custom logic, validation, and dynamic behavior

We needed a system that supports both without forcing users into one paradigm.

## Decision
We will implement a **hybrid definition system** supporting both:
- **YAML/JSON definitions** for simple, declarative wizards
- **Python decorators** for complex wizards with custom logic
- Both compile to the same internal `WizardConfig` model

## Consequences

### Positive
- **Low barrier to entry**: Simple wizards need no code
- **Full power when needed**: Complex logic fully supported
- **Gradual complexity**: Start with YAML, migrate to Python if needed
- **Type safety**: Both approaches produce typed configurations
- **Tooling friendly**: YAML can be generated/edited by tools

### Negative
- **Two systems to maintain**: Both YAML parser and decorator system
- **Feature parity**: Must ensure both support same features
- **Documentation**: Need to document both approaches

### Neutral
- Users choose the appropriate tool for their needs
- Migration path exists from simple to complex

## Implementation

### YAML Definition
```yaml
name: simple-setup
version: 1.0.0
branches:
  - id: main
    actions:
      - id: setup
        type: bash
        command: ./setup.sh
```

### Python Definition
```python
@wizard(name="complex-setup", version="1.0.0")
class ComplexWizard:
    @branch(id="main")
    class MainBranch:
        @action(id="setup")
        async def setup(self, state: SessionState) -> ActionResult:
            # Complex logic here
            return ActionResult(success=True)
```

Both produce the same `WizardConfig` instance.

## References
- PRD Section 2.2: Hybrid Definition System
- User feedback requesting dbt-like simplicity