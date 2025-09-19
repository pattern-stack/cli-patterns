# ADR-005: Type System Design

## Status
Accepted

## Context
Python's type system has evolved significantly, and we wanted to leverage it fully for CLI Patterns. We needed to decide how comprehensively to use typing features and which patterns to adopt.

## Decision
We will implement a **comprehensive type system** using:
- **NewType** for semantic types (`BranchId`, `ActionId`, etc.)
- **Discriminated unions** for action and option types
- **Pydantic models** for validation and serialization
- **Runtime protocols** for extensibility
- **MyPy strict mode** for type checking
- **Generic types** where appropriate

## Consequences

### Positive
- **Type safety**: Catch errors at development time
- **Self-documenting**: Types serve as documentation
- **IDE support**: Full autocomplete and type hints
- **Refactoring safety**: Type checker catches breaking changes
- **Runtime validation**: Pydantic validates at runtime
- **Rust migration**: Types map cleanly to Rust

### Negative
- **Learning curve**: Developers need to understand advanced typing
- **Verbosity**: More code for type definitions
- **MyPy strictness**: Can be frustrating initially
- **Performance**: Some runtime overhead from validation

### Neutral
- Industry best practice for modern Python
- Aligns with Pattern Stack's type-safety philosophy

## Implementation

### Semantic Types
```python
BranchId = NewType('BranchId', str)
ActionId = NewType('ActionId', str)
OptionKey = NewType('OptionKey', str)
```

### Discriminated Unions
```python
class BashActionConfig(ActionConfig):
    type: Literal["bash"] = "bash"
    command: str

class PythonActionConfig(ActionConfig):
    type: Literal["python"] = "python"
    function_name: str

ActionConfigUnion = Union[BashActionConfig, PythonActionConfig]
```

### Runtime Protocols
```python
@runtime_checkable
class ActionExecutor(Protocol):
    async def execute(
        self,
        config: ActionConfigUnion,
        state: SessionState
    ) -> ActionResult:
        ...
```

### Validation
```python
class BranchConfig(StrictModel):
    id: BranchId
    name: str = Field(..., min_length=1)

    @validator('id')
    def validate_id(cls, v: BranchId) -> BranchId:
        if not v:
            raise ValueError("Branch ID cannot be empty")
        return v
```

## References
- PRD Section 5.3: Type Safety Requirements
- cli-pattern-plan.md: Complete type system specification