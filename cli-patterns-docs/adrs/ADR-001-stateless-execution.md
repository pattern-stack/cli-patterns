# ADR-001: Stateless Execution Model

## Status
Accepted

## Context
When designing the CLI Patterns system, we needed to decide on the execution model for wizards. Options included:
1. Stateful execution with persistent session management
2. Stateless execution with optional persistence
3. Always-persistent state with database backing

Pattern Stack projects have different state requirements - some need persistence, others don't. We wanted to avoid unnecessary complexity while supporting both use cases.

## Decision
We will implement a **stateless-by-default** execution model where:
- Each wizard execution is independent
- State exists only in memory during execution
- Session persistence is optional and explicit
- Domains manage their own persistent state

## Consequences

### Positive
- **Simplicity**: No database or file system required by default
- **Performance**: No I/O overhead for simple wizards
- **Flexibility**: Domains can choose their persistence strategy
- **Testing**: Easier to test without persistent state
- **Portability**: Works anywhere without setup

### Negative
- **No automatic continuity**: Users can't resume by default
- **Domain complexity**: Domains must handle their own persistence
- **State loss**: Crashes lose in-progress state

### Neutral
- Session persistence can be added when needed
- Storage adapters provide persistence options

## Implementation
```python
class ExecutionEngine:
    def __init__(self, wizard_config: WizardConfig):
        self.wizard = wizard_config
        self.state = SessionState(wizard_name=wizard_config.name)
        # State exists only for this execution

    async def run_with_session(self, session_id: Optional[str] = None):
        """Optionally load previous state."""
        if session_id:
            self.state = await self.load_session(session_id)
```

## References
- PRD Section 3.3: Execution Model
- Initial design discussion in cli-pattern-plan.md