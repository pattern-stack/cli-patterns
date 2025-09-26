# ADR-007: Composable Parser System for Multiple Interaction Paradigms

## Status
Accepted

## Date
2024-01-25

## Context

During the refinement of CLI-8 (Basic Command Parser), we discovered that CLI Patterns is not building a single CLI interface, but rather a **system for building CLI systems**. Different use cases require fundamentally different interaction paradigms:

1. **Free-form text** (like Claude Code with `/` and `!` commands)
2. **Smart augmentation** (wrapping existing CLIs like `dbt` with autocomplete)
3. **Pure navigation** (arrow-key driven menus with no typing)

These paradigms need to coexist and even blend within a single session. A user might start in a navigation menu, select an option that drops them into an augmented dbt wrapper, then switch to free-form text for complex queries.

## Decision

We will build CLI-8 as a **composable parser system** rather than a monolithic command parser. This system will support multiple interaction modes that can be activated based on context.

### Core Architecture

```python
class InteractionMode(Enum):
    TEXT = "text"           # Free-form commands
    AUGMENTED = "smart"     # Autocomplete wrappers
    NAVIGATION = "menu"     # Pure arrow keys

class Parser(Protocol):
    """All parsers implement this interface"""
    def can_parse(self, input: str, context: Context) -> bool:
    def parse(self, input: str, context: Context) -> ParseResult:
    def get_suggestions(self, partial: str) -> List[str]:

class ParserPipeline:
    """Composable parser system"""
    def add_parser(self, parser: Parser, condition: Callable):
    def parse(self, input: str, context: Context):
```

### Key Components

1. **Mode Manager** - Switches between interaction modes dynamically
2. **Parser Chain** - Routes input to appropriate parser based on context
3. **Suggestion Engine** - Powers autocomplete across modes
4. **Navigation Controller** - Handles arrow-key navigation
5. **Context Tracker** - Maintains state about where we are in the interaction

## Alternatives Considered

### Alternative 1: Single Monolithic Parser
Build one parser that handles all cases with flags and options.

**Rejected because:**
- Would become unwieldy as we add more modes
- Hard to maintain clear separation of concerns
- Difficult for wizard authors to customize

### Alternative 2: Separate Tools
Build completely separate tools for each interaction mode.

**Rejected because:**
- Users want to mix modes within a session
- Would duplicate significant code
- Hard to maintain consistent theming and behavior

### Alternative 3: Configuration-Based
Use YAML/JSON to configure a single parser's behavior.

**Rejected because:**
- Not flexible enough for complex interactions
- Hard to express dynamic mode switching
- Would limit extensibility

## Consequences

### Positive
- **Flexibility**: Wizard authors can mix and match interaction modes
- **Extensibility**: New parsers can be added without touching existing code
- **Clarity**: Each parser has a single responsibility
- **Testability**: Parsers can be tested in isolation
- **User Experience**: Seamless transitions between modes

### Negative
- **Complexity**: More moving parts than a simple parser
- **Learning Curve**: Developers need to understand the composition model
- **Coordination**: Parsers need to coordinate through shared context

### Neutral
- Changes the mental model from "parsing commands" to "managing interactions"
- Requires thinking about state and context more explicitly
- Influences how we structure the wizard definition system

## Implementation Notes

1. Start with basic `TextParser` for free-form commands
2. Add `ShellParser` for `!` prefix shell passthrough
3. Implement `AutocompleteParser` for smart augmentation
4. Build `NavigationParser` for menu-driven interaction
5. Create `ModeSwitcher` to transition between modes

Each parser should:
- Use the design token system for consistent theming
- Integrate with the subprocess executor for command execution
- Support async operations
- Provide rich error messages with suggestions

## References

- CLI-8: Basic Command Parser ticket
- CLI Patterns PRD (Product Requirements Document)
- Prompt_toolkit documentation for input handling
- Rich documentation for output formatting

## Follow-up Actions

1. Update CLI-8 ticket with composable parser design
2. Create sub-tickets for each parser implementation
3. Design the Context and Session state management
4. Document parser authoring guide for developers