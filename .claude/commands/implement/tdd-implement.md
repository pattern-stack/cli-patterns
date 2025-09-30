---
description: TDD-driven implementation orchestrator for CLI Patterns - collaboratively defines tests, builds them, then implements protocol-based, type-safe code
argument-hint: [issue-id] or leave blank to implement current work
allowed-tools: Task, TodoWrite, Bash, Read, Write, MultiEdit, Glob, Grep
---

# CLI Patterns TDD Implementation Orchestrator

You are orchestrating a Test-Driven Development (TDD) implementation process for the CLI Patterns framework. This workflow ensures high-quality, protocol-based, type-safe code with MyPy strict compliance and comprehensive test coverage.

## Core TDD Principles + CLI Patterns Architecture

1. **Red Phase**: Write tests that fail (validating protocol compliance and type safety)
2. **Green Phase**: Write minimal code implementing protocols to make tests pass
3. **Refactor Phase**: Improve code while maintaining MyPy strict mode compliance
4. **Component-by-Component**: Progress through core → ui/design → ui/parser → execution

## CLI Patterns Component Guidelines

### Core Components
- **Types**: Semantic types (BranchId, ActionId, OptionKey, WizardId) for type safety
- **Protocols**: Runtime-checkable protocol definitions for extensibility
- **Models**: Pydantic models with strict validation (CLI-5 pending)

### UI Components
- **Design System**: Design tokens, themes, component registry with Rich integration
- **Parser System**: Protocol-based parsers with pipeline architecture
  - Text parser for plain commands
  - Shell parser for shell pass-through (!)
  - Command registry with fuzzy matching
- **Screens**: Future screen implementations

### Execution Components
- **Subprocess Executor**: Async execution with themed output (CLI-9)
- **Session State**: Runtime state management
- **Action Executors**: Protocol-based action execution

### Configuration
- **YAML/JSON Loaders**: Definition loading (pending)
- **Python Decorators**: Code-based definitions (pending)
- **Theme Loading**: Extensible theming system

## Phase 0: Context Gathering

### Step 0.1: Identify the Task
$ARGUMENTS

If an issue ID was provided (e.g., CLI-8):
```bash
# Check if using Linear/GitHub issues
gh issue view $1 || echo "Issue not found on GitHub"
git log --grep="$1" --oneline -5
```

If no issue specified, check current context:
```bash
# Check current branch and recent work
git branch --show-current
gh pr status || echo "No PR found"
git log --oneline -10
```

### Step 0.2: Load Architecture Context
Load CLI Patterns architecture requirements:
- Review @CLAUDE.md for project overview and conventions
- Check @src/cli_patterns/core/ for types and protocols
- Review @pyproject.toml for markers and dependencies
- Examine @tests/conftest.py for test configuration

```bash
# Check for related documentation
ls -la cli-patterns-docs/adrs/ 2>/dev/null || echo "No ADRs directory"

# Check test structure and markers
grep -r "pytestmark" tests/ | head -5

# Verify MyPy configuration
grep -A10 "\[tool.mypy\]" pyproject.toml
```

### Step 0.3: Determine Implementation Strategy
Identify which CLI Patterns components will be involved:
- **Semantic Types**: Which NewTypes are needed (BranchId, ActionId, OptionKey)?
- **Protocols**: What protocols need implementation (Parser, ActionExecutor, etc.)?
- **Design Tokens**: Will UI components need theming?
- **Parser Types**: Text commands, shell pass-through, or new paradigm?
- **Test Markers**: Which markers apply (unit, integration, parser, executor, design)?

### Step 0.4: Understand Current State
Create a TodoWrite list to track all implementation phases:

```
TodoWrite:
- Gather requirements and identify components
- Define test conditions by component (core/ui/execution)
- Generate protocol-compliant test suite
- Implement core types and protocols
- Implement UI components (design/parser/screens)
- Implement execution components
- Validate MyPy strict mode compliance
- Run component-specific tests
- Run final validation suite
- Prepare for review
```

## Phase 1: Test Condition Definition (Agent 1)

### Step 1.1: Launch Requirements Analysis Agent

**Task Tool Usage:**
```
Task: "Analyze requirements and define test conditions"
Prompt: "
You are the TEST CONDITION ARCHITECT. Your role is to work WITH THE USER to understand requirements and define test conditions in plain language.

CONTEXT:
- Issue: [issue-id and description]
- Existing code patterns: [from exploration]
- Architecture constraints: [from CLAUDE.md]

YOUR MISSION:
1. UNDERSTAND the feature deeply:
   - What interaction paradigm does it enable?
   - Which protocols need implementation?
   - What semantic types are involved?
   - How does it maintain stateless execution?

2. COLLABORATE with the user to identify PROTOCOL-BASED test scenarios:
   - **Type Tests**: Semantic type usage and validation
   - **Protocol Tests**: Protocol compliance and contracts
   - **Component Tests**: Component-specific behavior (parser, executor, design)
   - **Integration Tests**: Component interaction and composition

3. OUTPUT test conditions by COMPONENT:
   Format each as: 'GIVEN [context] WHEN [action] THEN [expected outcome]'

   Example:
   - GIVEN a Parser protocol implementation WHEN parse called THEN returns ParseResult
   - GIVEN a command with design tokens WHEN rendered THEN applies theme correctly
   - GIVEN subprocess executor WHEN async execution THEN streams output with themes

4. GROUP test conditions by CLI PATTERNS COMPONENT:
   - **Core Tests**
     - Semantic type creation and usage
     - Protocol compliance verification
     - ActionResult success/failure handling
   - **UI/Parser Tests**
     - Parser pipeline routing
     - Command registry fuzzy matching
     - Shell pass-through behavior
   - **UI/Design Tests**
     - Design token resolution
     - Theme inheritance and overrides
     - Component rendering with Rich
   - **Execution Tests**
     - Subprocess async execution
     - Output streaming and theming
     - Session state management

5. For each test condition, note:
   - Priority (Critical/Important/Nice-to-have)
   - Type (Unit/Integration/E2E)
   - Dependencies (what needs to exist first)

IMPORTANT:
- BE THOROUGH - missing test conditions now means bugs later
- USE EXAMPLES - concrete scenarios are better than abstract descriptions
- THINK LIKE A USER - what would surprise or frustrate them?
- CONSIDER FAILURE - how should the system fail gracefully?

Return a structured list of test conditions ready for test generation.
"
Subagent: general-purpose
```

### Step 1.2: Review and Refine with User

**PAUSE FOR USER INPUT**

Present the test conditions to the user:
```markdown
## Proposed Test Conditions

Based on my understanding of [feature], here are the test conditions I've identified:

### Core Component: [Types/Protocols]

#### Type Safety Tests
1. **Semantic Types**: GIVEN a BranchId WHEN created from string THEN maintains type distinction
2. **Protocol Compliance**: GIVEN a Parser implementation WHEN methods called THEN satisfies protocol contract

### UI/Parser Component: [Parser Name]

#### Parser Tests
1. **Pipeline Routing**: GIVEN multiple parsers WHEN input matches condition THEN routes to correct parser
2. **Registry Matching**: GIVEN command registry WHEN fuzzy match requested THEN returns suggestions
3. **Shell Pass-through**: GIVEN input starting with ! WHEN parsed THEN delegates to shell

### UI/Design Component: [Theme/Component]

#### Design System Tests
1. **Token Resolution**: GIVEN design token WHEN resolved THEN applies theme hierarchy
2. **Component Rendering**: GIVEN themed component WHEN rendered THEN uses Rich styles correctly

### Execution Component: [Executor Name]

#### Execution Tests
1. **Async Execution**: GIVEN subprocess command WHEN executed async THEN streams output
2. **Theme Application**: GIVEN output lines WHEN displayed THEN applies design tokens
3. **Session State**: GIVEN stateless execution WHEN state needed THEN manages session correctly

### Questions for Clarification:
- Should we handle [specific scenario]?
- What's the expected behavior for [edge case]?
- Are there performance requirements?

What would you like to add, remove, or modify?
```

### Step 1.3: Finalize Test Specification

Once user agrees, create a CLI Patterns test specification:

```bash
Write tests/test_specs/[issue-id]-test-specification.md
```

Content should include:
- Test conditions organized by component (core/ui/execution)
- Protocol compliance verification
- Type safety validation with MyPy strict
- Component boundary tests
- Parser pipeline composition tests
- Design token inheritance tests
- Stateless execution verification

## Phase 2: Test Generation (Agent 2)

### Step 2.1: Launch Test Builder Agent

**Task Tool Usage:**
```
Task: "Build comprehensive test suite from specifications"
Prompt: "
You are the TEST BUILDER. Your role is to transform test conditions into executable tests.

INPUT: Test conditions from Phase 1
- [List of GIVEN-WHEN-THEN conditions]
- Module groupings
- Priority levels

YOUR MISSION:
1. ANALYZE CLI Patterns testing structure:
   - Check tests/unit/ for component isolation tests
   - Check tests/integration/ for component interaction tests
   - Check tests/conftest.py for auto-marking configuration
   - Follow existing test patterns and fixtures

2. GENERATE COMPONENT-SPECIFIC test files:
   - tests/unit/core/test_[types|protocols].py
   - tests/unit/ui/parser/test_[parser_name].py
   - tests/unit/ui/design/test_[component].py
   - tests/unit/execution/test_[executor].py
   - tests/integration/test_[component]_integration.py

3. For each test condition, create:
   - Setup (Arrange)
   - Action (Act)
   - Assertion (Assert)
   - Teardown if needed

4. Include test utilities:
   - Fixtures for common test data
   - Helper functions for assertions
   - Mock objects for dependencies
   - Performance benchmarks where specified

5. STRUCTURE for maintainability:
   - Group related tests in classes
   - Use parametrize for similar tests with different data
   - Add docstrings explaining what's being tested
   - Include error messages that help debugging

EXAMPLE CLI PATTERNS TEST OUTPUT:
```python
# tests/unit/ui/parser/test_custom_parser.py
import pytest
from unittest.mock import Mock

from cli_patterns.ui.parser.protocols import Parser
from cli_patterns.ui.parser.types import Context, ParseError, ParseResult

pytestmark = pytest.mark.parser  # Auto-marks all tests

class TestCustomParser:
    '''Tests for CustomParser protocol implementation'''

    @pytest.fixture
    def parser(self) -> Parser:
        '''Create parser instance for testing.'''
        return CustomParser()

    @pytest.fixture
    def context(self) -> Context:
        '''Create context for testing.'''
        return Context(mode="interactive", history=[], session_state={})

    def test_should_implement_parser_protocol(self, parser: Parser) -> None:
        '''GIVEN CustomParser WHEN checking protocol THEN implements Parser.'''
        # Assert - MyPy will verify at type-check time
        assert isinstance(parser, Parser)
        assert hasattr(parser, 'parse')
        assert hasattr(parser, 'can_parse')

# tests/unit/core/test_action_result.py
from cli_patterns.core.types import ActionResult

class TestActionResult:
    '''Tests for ActionResult dataclass'''

    def test_should_indicate_success_correctly(self) -> None:
        '''GIVEN ActionResult WHEN created with success=True THEN failed property is False.'''
        # Arrange & Act
        result = ActionResult(success=True, data={"output": "test"})

        # Assert
        assert result.success is True
        assert result.failed is False
        assert result.data == {"output": "test"}

    def test_should_handle_subprocess_output(self) -> None:
        '''GIVEN ActionResult WHEN subprocess output provided THEN stores stdout/stderr.'''
        # Arrange & Act
        result = ActionResult(
            success=True,
            stdout="Command output",
            stderr="Warning messages"
        )

        # Assert
        assert result.stdout == "Command output"
        assert result.stderr == "Warning messages"

# tests/unit/ui/design/test_token_resolution.py
from cli_patterns.ui.design.tokens import DesignTokens
from cli_patterns.ui.design.themes import Theme

pytestmark = pytest.mark.design

class TestDesignTokenResolution:
    '''Tests for design token resolution and theming'''

    def test_should_resolve_tokens_with_theme_hierarchy(self) -> None:
        '''GIVEN design tokens WHEN theme applied THEN resolves with inheritance.'''
        # Arrange
        theme = Theme(name="custom", parent="default")
        tokens = DesignTokens(theme=theme)

        # Act
        style = tokens.resolve("emphasis.strong")

        # Assert
        assert style is not None
        assert "bold" in style.meta  # Verify Rich style attributes

# tests/integration/test_parser_pipeline.py
class TestParserPipelineIntegration:
    '''Integration tests for parser pipeline composition'''

    @pytest.mark.integration
    async def test_should_route_between_multiple_parsers(self) -> None:
        '''GIVEN pipeline with multiple parsers WHEN various inputs THEN routes correctly.'''
        # Test complete parser composition and routing
        pipeline = ParserPipeline()
        pipeline.add_parser(TextParser(), lambda i, c: not i.startswith("!"))
        pipeline.add_parser(ShellParser(), lambda i, c: i.startswith("!"))

        # Test routing logic
        text_result = await pipeline.parse("list files", context)
        shell_result = await pipeline.parse("!ls -la", context)

        assert text_result.parser_type == "text"
        assert shell_result.parser_type == "shell"

    @pytest.mark.parametrize('invalid_input,expected_error', [
        ('command "unclosed', ParseError),
        ('', EmptyCommandError),
        ('!', ShellPassthroughError),
    ])
    def test_should_raise_appropriate_errors(self, parser: Parser, context: Context, invalid_input: str, expected_error: type) -> None:
        '''GIVEN invalid input WHEN parsed THEN raises appropriate error.'''
        with pytest.raises(expected_error):
            parser.parse(invalid_input, context)
```

IMPORTANT:
- Tests must FAIL initially (no implementation exists)
- Tests must be INDEPENDENT (no test depends on another)
- Tests must be FAST (mock external dependencies)
- Tests must be CLEAR (anyone can understand what's being tested)

Create all test files and return a summary of what was created.
"
Subagent: general-purpose
```

### Step 2.2: Verify Test Suite Compilation

Run tests to confirm they fail as expected:

```bash
# Try to run the new tests (they should fail)
make test 2>&1 | head -50

# Check for syntax errors
PYTHONPATH=src python3 -m py_compile tests/**/*.py

# Verify test discovery and markers
pytest --collect-only tests/ -q
pytest --markers

# Run MyPy on test files to verify type annotations
make type-check
```

### Step 2.3: Create Test Execution Tracker

Update TodoWrite with specific test files:

```
TodoWrite updates:
- ✓ Define test conditions with user
- ✓ Generate protocol-compliant test suite
- [ ] Implement core type tests (0/4 types)
- [ ] Implement protocol compliance tests (0/3 protocols)
- [ ] Implement parser component tests (0/5 parsers)
- [ ] Implement design system tests (0/3 components)
- [ ] Implement execution tests (0/2 executors)
- [ ] Validate MyPy strict compliance
- [ ] Refactor and optimize
- [ ] Run final validation
```

## Phase 3: Implementation (Agent 3)

### Step 3.1: Module-by-Module Implementation

For EACH module in the TodoWrite list, launch an implementation agent:

**Task Tool Usage (Example for first module):**
```
Task: "Implement parser module to pass tests"
Prompt: "
You are the IMPLEMENTATION SPECIALIST. Your role is to write code that makes tests pass.

TARGET: Make tests pass following CLI Patterns architecture

CLI PATTERNS CONSTRAINTS:
- **Protocol Compliance**: All implementations must satisfy protocol contracts
- **Type Safety**: MyPy strict mode with semantic types (BranchId, ActionId, etc.)
- **Component Boundaries**: Clear separation between core/ui/execution
- **Stateless Execution**: Each run independent with optional session persistence
- **Design System**: Use design tokens and themes for all UI components
- **Parser Composition**: Composable parsers with pipeline architecture

CLI PATTERNS PROCESS:
1. IDENTIFY the component:
   - Core: Implement types, protocols, models
   - UI/Parser: Implement parsers following protocol
   - UI/Design: Implement with design tokens and Rich
   - Execution: Implement async executors with theming

2. FOLLOW protocols:
   - Parser protocol for all parsers
   - ActionExecutor protocol for actions
   - NavigationController protocol for navigation
   - OptionCollector protocol for option collection

3. IMPLEMENT following rules:
   - All functions with type hints
   - MyPy strict mode compliance
   - Use semantic types not primitives
   - Protocol-based extensibility

3. For each test that passes, track progress:
   - Run: pytest tests/test_parser.py::TestClass::test_method -v
   - Confirm green status
   - Document any assumptions made

4. HANDLE failures systematically:
   - Read the error message carefully
   - Fix only what's needed
   - Don't modify tests (they're the specification)
   - If a test seems wrong, document why but don't change it

5. After all tests pass:
   - Run full test suite for the module
   - Check for any regressions
   - Verify type checking passes
   - Ensure linting passes

CLI PATTERNS IMPLEMENTATION EXAMPLES:

```python
# CORE: Semantic types and protocols
from typing import Protocol, runtime_checkable
from cli_patterns.core.types import BranchId, ActionId, OptionKey

@runtime_checkable
class Parser(Protocol):
    '''Protocol for all parser implementations.'''

    def can_parse(self, input_text: str, context: Context) -> bool:
        '''Check if this parser can handle the input.'''
        ...

    def parse(self, input_text: str, context: Context) -> ParseResult:
        '''Parse input and return structured result.'''
        ...

# UI/PARSER: Custom parser implementation
from cli_patterns.ui.parser.protocols import Parser
from cli_patterns.ui.parser.types import Context, ParseResult, ParseError

class CustomParser:
    '''Custom parser implementing Parser protocol.'''

    def can_parse(self, input_text: str, context: Context) -> bool:
        '''Check if input matches custom syntax.'''
        return input_text.startswith("@") or "::" in input_text

    def parse(self, input_text: str, context: Context) -> ParseResult:
        '''Parse custom command syntax.'''
        if not self.can_parse(input_text, context):
            raise ParseError(
                message="Invalid custom syntax",
                error_type="INVALID_SYNTAX",
                input_text=input_text
            )

        # Parse logic here
        return ParseResult(
            command="custom",
            arguments=[],
            options=set(),
            metadata={},
            raw_input=input_text
        )

# UI/DESIGN: Component with design tokens
from rich.console import Console
from cli_patterns.ui.design.tokens import DesignTokens
from cli_patterns.ui.design.registry import ComponentRegistry

class ThemedComponent:
    '''Component using design system for rendering.'''

    def __init__(self, tokens: DesignTokens) -> None:
        self.tokens = tokens
        self.console = Console()

    def render_status(self, status: str, message: str) -> None:
        '''Render status message with appropriate tokens.'''
        if status == "success":
            style = self.tokens.resolve("status.success")
        elif status == "error":
            style = self.tokens.resolve("status.error")
        else:
            style = self.tokens.resolve("category.default")

        self.console.print(message, style=style)

# EXECUTION: Subprocess executor with theming
from cli_patterns.execution.subprocess_executor import SubprocessExecutor
from cli_patterns.ui.design.registry import get_component

class ThemedExecutor:
    '''Executor with themed output streaming.'''

    def __init__(self) -> None:
        self.executor = SubprocessExecutor()
        self.output_handler = get_component("output_handler")

    async def execute_with_theme(
        self,
        command: List[str],
        theme: str = "default"
    ) -> ActionResult:
        '''Execute command with themed output.'''
        async for line in self.executor.stream_output(command):
            if line.stream == "stdout":
                self.output_handler.display(
                    line.content,
                    token="output.stdout"
                )
            else:
                self.output_handler.display(
                    line.content,
                    token="output.stderr"
                )

        return ActionResult(
            success=self.executor.return_code == 0,
            stdout=self.executor.stdout,
            stderr=self.executor.stderr
        )

# PARSER PIPELINE: Composing multiple parsers
from cli_patterns.ui.parser.pipeline import ParserPipeline
from cli_patterns.ui.parser.text import TextParser
from cli_patterns.ui.parser.shell import ShellParser

class CommandInterface:
    '''Main command interface using parser pipeline.'''

    def __init__(self) -> None:
        self.pipeline = ParserPipeline()
        self._setup_parsers()

    def _setup_parsers(self) -> None:
        '''Configure parser pipeline with conditions.'''
        # Shell pass-through for ! commands
        self.pipeline.add_parser(
            ShellParser(),
            lambda i, c: i.startswith("!")
        )

        # Text parser as fallback
        self.pipeline.add_parser(
            TextParser(),
            lambda i, c: True  # Always can parse
        )

    async def process_input(
        self,
        input_text: str,
        context: Context
    ) -> ParseResult:
        '''Process user input through pipeline.'''
        return await self.pipeline.parse(input_text, context)
```

Report:
- Which tests now pass
- CLI Patterns compliance status:
  - Protocol contracts satisfied?
  - MyPy strict mode passing?
  - Component boundaries maintained?
  - Design tokens properly used?
- Code coverage for the component
- Type checking validation results
"
Subagent: general-purpose
```

### Step 3.2: Progress Tracking and Validation

After each component implementation:

```bash
# Run component-specific tests using markers
make test-parser     # Parser component tests
make test-executor   # Executor component tests
make test-design     # Design system tests

# Or run specific test files
PYTHONPATH=src python3 -m pytest tests/unit/ui/parser/ -v --tb=short

# Update TodoWrite with progress
# Example: "Implement parser tests (3/5 parsers complete)"

# Check coverage by component
PYTHONPATH=src python3 -m pytest tests/unit/ui/parser/ --cov=cli_patterns.ui.parser --cov-report=term-missing

# Validate MyPy strict compliance
make type-check

# Verify no regressions
make test-unit
```

### Step 3.3: Integration Validation

Once all unit tests pass, run integration tests:

```bash
# Run integration tests
make test-integration

# Run full test suite
make test

# Check overall coverage
make test-coverage
```

## Phase 4: Refactoring (Green to Clean)

### Step 4.1: Launch Refactoring Agent

Only after ALL tests pass:

**Task Tool Usage:**
```
Task: "Refactor implementation while maintaining green tests"
Prompt: "
You are the REFACTORING SPECIALIST. All tests are passing. Your role is to improve code quality.

CURRENT STATE:
- All tests passing
- Coverage at [X]%
- Working implementation

CLI PATTERNS REFACTORING GOALS:
1. ENHANCE protocol usage
   - Ensure all implementations satisfy protocols
   - Add runtime_checkable where beneficial
   - Extract common behavior to protocol defaults

2. IMPROVE type safety
   - Replace primitives with semantic types
   - Add discriminated unions where appropriate
   - Strengthen MyPy strict compliance

3. STRENGTHEN component boundaries
   - Clarify core/ui/execution separation
   - Remove cross-component dependencies
   - Improve protocol-based composition

4. OPTIMIZE design system usage
   - Consistent design token application
   - Theme inheritance optimization
   - Component registry utilization

5. ALIGN with CLI Patterns architecture
   - Stateless execution patterns
   - Composable parser pipeline
   - Protocol-based extensibility
   - Design system integration

CONSTRAINTS:
- Run tests after EVERY change
- If a test fails, revert immediately
- Keep commits atomic
- Document why each refactoring was done

VALIDATION:
After each refactoring:
- Run: make test
- Run: make typecheck
- Run: make lint
- Ensure all still pass

Report all refactorings made and their benefits.
"
Subagent: general-purpose
```

## Phase 5: Final Validation & Preparation

### Step 5.1: Comprehensive Validation

Run all quality checks in parallel:

**Launch validation agents in parallel:**

```python
# Single message with multiple Task tool calls:
[Task 1: Run full test suite with coverage]
[Task 2: Run MyPy strict type checking]
[Task 3: Validate component boundaries]
[Task 4: Check protocol compliance]
[Task 5: Run linting and formatting]
[Task 6: Verify marker-based test organization]
```

### Step 5.2: Documentation Update

Ensure all documentation is current:

```bash
# Update implementation documentation
Write docs/components/[component-name].md

# Update CLAUDE.md if new patterns introduced
MultiEdit CLAUDE.md

# Document new protocols if added
Write docs/protocols/[protocol-name].md

# Update README if user-facing changes
# Document design tokens if new ones added
```

### Step 5.3: Pre-Review Checklist

Complete the TodoWrite:

```
Final Status:
✓ Gather requirements and context
✓ Define test conditions with user
✓ Generate protocol-compliant test suite
✓ Make tests/unit/ui/parser/ pass (8/8 tests)
✓ Make tests/unit/execution/ pass (12/12 tests)
✓ Make tests/integration/ pass (5/5 tests)
✓ Validate MyPy strict compliance
✓ Refactor and optimize
✓ Run final validation suite
✓ Prepare for review
```

## Phase 6: Handoff Preparation

### Step 6.1: Create Implementation Summary

```markdown
## TDD Implementation Complete for [Issue-ID]

### CLI Patterns Implementation Complete

#### Architecture Compliance
- Protocol contracts: ✅ Satisfied
- MyPy strict mode: ✅ Passing
- Component boundaries: ✅ Maintained
- Design system: ✅ Integrated

#### Component Implementation
1. **Core Component**
   - Semantic types: [BranchId, ActionId, OptionKey]
   - Protocols: X implemented
   - Coverage: X%

2. **UI/Parser Component**
   - Parsers: X parsers (text, shell, custom)
   - Pipeline routing: ✅ Working
   - Registry: ✅ Fuzzy matching
   - Coverage: X%

3. **UI/Design Component**
   - Design tokens: ✅ Resolved
   - Themes: X themes configured
   - Components: X registered
   - Coverage: X%

4. **Execution Component**
   - Subprocess executor: ✅ Async
   - Output theming: ✅ Applied
   - Session state: ✅ Managed
   - Coverage: X%

### Quality Metrics
- Test Coverage: X% overall
- MyPy Strict: ✅ Clean (0 errors)
- Ruff Linting: ✅ Clean
- Black Formatting: ✅ Consistent
- Test Markers: ✅ Properly applied
- Performance: [async execution benchmarks]

### Ready for Review
The implementation is complete and ready for PR review process.
```

### Step 6.2: Suggest Next Steps

```markdown
## Recommended Next Steps

1. **Create Pull Request**
   ```bash
   gh pr create --title "feat: [description]" --body "[summary]"
   ```

2. **Run Review Process**
   ```bash
   # Using the review command
   /review:pr-review
   ```

3. **Component Testing**
   ```bash
   # Test all components
   make test-components
   ```

3. **Additional Testing** (if needed)
   - Manual testing scenarios
   - Load testing if applicable
   - User acceptance testing

4. **Future Enhancements**
   - [List any identified improvements]
   - [Technical debt to address]
   - [Performance optimizations possible]
```

## Important Implementation Principles

### Follow CLI Patterns TDD Strictly
- NEVER write implementation before tests
- NEVER violate protocol contracts
- NEVER skip MyPy strict type checking
- ALWAYS use semantic types over primitives
- ALWAYS implement protocols completely

### CLI Patterns Quality Gates
- Every component must have >80% coverage
- MyPy strict mode must pass (0 errors)
- All test markers must be properly applied
- Protocol contracts must be satisfied
- Component boundaries must be maintained
- Design tokens must be consistently used

### Work Incrementally
- Complete one module fully before starting another
- Commit after each passing test
- Keep the build green

### Collaborate Continuously
- Check in with user after test definition
- Report progress after each module
- Flag any architectural concerns immediately

### Document Decisions
- Why certain implementation choices were made
- Any deviations from original plan
- Performance trade-offs considered

## Error Recovery

If implementation gets stuck:

1. **Test Won't Pass**
   - Re-read test carefully
   - Check test assumptions
   - Consult with user if test seems incorrect
   - Document why test might need modification

2. **Performance Issues**
   - Run profiler to identify bottlenecks
   - Consider algorithmic improvements
   - Add performance tests for regression prevention

3. **Integration Failures**
   - Check module boundaries
   - Verify interface contracts
   - Review dependency injection
   - Consider mock objects for isolation

## Completion Checklist

Before declaring CLI Patterns implementation complete:
- [ ] All test conditions from Phase 1 are covered
- [ ] All component-specific tests are passing
- [ ] Architecture compliance validated:
  - [ ] Protocol contracts fully satisfied
  - [ ] MyPy strict mode passing (0 errors)
  - [ ] Component boundaries maintained (core/ui/execution)
  - [ ] Semantic types used throughout
  - [ ] Stateless execution verified
  - [ ] Design system properly integrated
- [ ] Testing standards met:
  - [ ] Test markers properly applied (unit, integration, parser, executor, design)
  - [ ] Fixtures and mocks appropriately used
  - [ ] Test isolation maintained
  - [ ] Coverage >80% per component
- [ ] Code quality verified:
  - [ ] make lint passes
  - [ ] make type-check passes
  - [ ] make format produces no changes
  - [ ] make test-components passes
- [ ] Documentation updated:
  - [ ] CLAUDE.md reflects new patterns
  - [ ] Protocol documentation added
  - [ ] Design token documentation current
- [ ] Ready for CLI Patterns PR review

Remember: The goal is not just working code, but CLI Patterns-compliant, well-tested code that:
- Implements protocol-based architecture for maximum extensibility
- Maintains MyPy strict mode compliance for type safety
- Uses semantic types to prevent type confusion
- Provides composable components through clear interfaces
- Integrates design system for consistent, beautiful terminal UIs
- Enables multiple interaction paradigms (text, shell, future additions)
- Serves as a foundation for building sophisticated CLI applications.