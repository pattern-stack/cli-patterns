# CLI-8 Refinement Summary

**Date:** 2024-01-25
**Participants:** @dug, Claude

## Key Discovery

CLI Patterns is not building **a CLI**, but rather **a system for building CLI systems**. This fundamentally changes how we approach the command parser.

## Refined Approach: Composable Parser System

Instead of a single command parser, CLI-8 will implement a composable parser system that supports three interaction paradigms:

### 1. Free-form Text Mode
- Traditional command-line with `/` and `!` prefixes
- Example: `think about architecture`, `/help`, `!git status`

### 2. Smart Augmentation Mode
- Intelligent wrappers for existing CLIs
- Auto-completion and suggestions
- Example: `d[TAB]` → `dbt` → shows `[run, build, test]`

### 3. Pure Navigation Mode
- Arrow-key driven menus
- No typing required
- Example: Main Menu → Arrow to select → Sub-menu

## Technical Design

```python
# Core abstractions
class Parser(Protocol):
    def can_parse(self, input: str, context: Context) -> bool
    def parse(self, input: str, context: Context) -> ParseResult
    def get_suggestions(self, partial: str) -> List[str]

class ParserPipeline:
    """Routes input to appropriate parser based on context"""
    def add_parser(self, parser: Parser, condition: Callable)
    def parse(self, input: str, context: Context)
```

## Implementation Plan

### Phase 1: Foundation (Week 1)
- [ ] Create Parser protocol and ParseResult types
- [ ] Implement ParserPipeline for composition
- [ ] Build basic TextParser for free-form commands
- [ ] Add ShellParser for `!` prefix passthrough

### Phase 2: Smart Features (Week 2)
- [ ] Implement AutocompleteParser
- [ ] Add suggestion engine
- [ ] Create wrapper configurations (e.g., dbt)
- [ ] Build context tracking

### Phase 3: Navigation (Week 2)
- [ ] Implement NavigationParser
- [ ] Add menu rendering
- [ ] Handle arrow-key events
- [ ] Support mode switching

## Decisions Made

1. **Composable over Monolithic**: Multiple specialized parsers instead of one complex parser
2. **Protocol-based**: All parsers implement the same interface
3. **Context-aware**: Parsers can activate based on current context
4. **Mode switching**: Users can transition between modes seamlessly

## ADR Created

See [ADR-007: Composable Parser System](../adrs/ADR-007-composable-parser-system.md) for detailed architectural decision.

## Updated Acceptance Criteria

- [ ] Multiple parsers can be composed in a pipeline
- [ ] Parsers activate based on context conditions
- [ ] Smooth transitions between interaction modes
- [ ] Each parser is independently testable
- [ ] All parsers use design tokens for theming
- [ ] Error messages include mode-appropriate suggestions

## Next Steps

1. Update CLI-8 ticket with this refined approach
2. Create sub-tickets for each parser implementation
3. Begin with TextParser as the foundation
4. Design Context and Session state management

## Example Usage

```python
# Create a session that combines all modes
session = CLISession()

# Start in navigation
session.mode = InteractionMode.NAVIGATION
# User selects "Database" with arrow keys

# Switch to augmented mode
session.mode = InteractionMode.AUGMENTED
session.wrapper = "dbt"
# User types "d" → autocompletes to "dbt run"

# Drop to free-form for complex command
session.mode = InteractionMode.TEXT
# User types "!psql -c 'SELECT * FROM users'"
```

## Notes from Refinement Session

- Started with assumption of single parser
- Through exploration, discovered the need for multiple paradigms
- Realized this aligns with CLI Patterns' goal: a system to build systems
- Emphasized composability and flexibility over simplicity
- Decided to embrace complexity where it serves user flexibility