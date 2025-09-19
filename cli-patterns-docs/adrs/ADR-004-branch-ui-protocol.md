# ADR-004: Branch-Level UI Protocol

## Status
Accepted

## Context
The CLI Patterns system needs to support different UI implementations (CLI, TUI, potentially web) without coupling the core wizard logic to any specific UI framework. We needed to define the abstraction boundary.

## Decision
We will define a **branch-level UI protocol** where:
- UI implementations interact at the branch granularity
- The protocol defines three core methods: `render_branch`, `collect_options`, `show_menu`
- UI implementations are injected via dependency injection
- Core logic remains UI-agnostic

## Consequences

### Positive
- **Clean separation**: Core logic doesn't know about UI
- **Multiple UIs**: Can support CLI, TUI, web, etc.
- **Testability**: Can test with mock UI
- **Branch coherence**: UI operations align with navigation model
- **Future flexibility**: Can add new UI types without changing core

### Negative
- **Protocol constraints**: All UIs must fit this abstraction
- **Limited customization**: UIs can only customize at branch level
- **No fine-grained control**: Can't customize individual options differently

### Neutral
- Branch level is a natural boundary for UI operations
- Most UI frameworks can adapt to this model

## Implementation
```python
@runtime_checkable
class UIRenderer(Protocol):
    """Protocol for UI rendering at branch level."""

    async def render_branch(
        self,
        branch: BranchConfig,
        state: SessionState
    ) -> None:
        """Render a branch UI."""
        ...

    async def collect_options(
        self,
        options: List[OptionConfigUnion],
        state: SessionState
    ) -> Dict[OptionKey, StateValue]:
        """Collect all options for a branch."""
        ...

    async def show_menu(
        self,
        menus: List[MenuConfig],
        state: SessionState
    ) -> Optional[MenuId]:
        """Show menu and get selection."""
        ...
```

## Future Considerations
- May need hooks for pre/post branch rendering
- Could add protocol for progress indication
- Might need custom renderer protocol for special cases

## References
- PRD Section 3.2: Key Interfaces
- Discussion on UI separation requirements