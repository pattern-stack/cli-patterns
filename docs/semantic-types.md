# Semantic Types Guide

## Overview

CLI Patterns uses semantic types to provide compile-time type safety and prevent type confusion in the parser system. These types use Python's `NewType` feature to create distinct types at compile time with zero runtime overhead.

## Core Semantic Types

### Command and Parser Types
- `CommandId`: Unique identifier for commands (e.g., "help", "run", "test")
- `OptionKey`: Command option keys (e.g., "--verbose", "--output")
- `FlagName`: Boolean flag names (e.g., "--debug", "--quiet")
- `ArgumentValue`: String argument values
- `ParseMode`: Parser mode identifiers (e.g., "text", "shell", "semantic")
- `ContextKey`: Context variable keys for parser state

## When to Use Semantic Types

### Use Semantic Types When:
- Defining command identifiers in registries
- Passing option keys between parser components
- Storing parser context values
- Building parse results with typed fields
- Creating command suggestions and error messages

### Use Regular Strings When:
- Displaying user-facing messages
- Working with raw input before parsing
- Interfacing with external libraries
- Performance-critical hot paths (though overhead is minimal)

## Migration Guide

### Converting Existing Code

#### Before (using plain strings):
```python
def register_command(name: str, handler: Callable) -> None:
    commands[name] = handler

def parse_command(input: str) -> tuple[str, dict[str, str]]:
    command = input.split()[0]
    options = parse_options(input)
    return command, options
```

#### After (using semantic types):
```python
from cli_patterns.core.parser_types import CommandId, OptionKey, make_command_id, make_option_key

def register_command(name: CommandId, handler: Callable) -> None:
    commands[name] = handler

def parse_command(input: str) -> tuple[CommandId, dict[OptionKey, str]]:
    command = make_command_id(input.split()[0])
    options = {make_option_key(k): v for k, v in parse_options(input).items()}
    return command, options
```

### Conversion Methods

The semantic parser components provide bidirectional conversion:

```python
from cli_patterns.ui.parser.semantic_result import SemanticParseResult
from cli_patterns.ui.parser.types import ParseResult

# Convert from regular to semantic
regular_result = ParseResult(command="help", options={"verbose": "true"})
semantic_result = SemanticParseResult.from_parse_result(regular_result)

# Convert from semantic to regular
regular_again = semantic_result.to_parse_result()
```

## Factory Functions

Use factory functions to create semantic types:

```python
from cli_patterns.core.parser_types import (
    make_command_id,
    make_option_key,
    make_flag_name,
    make_argument_value,
    make_parse_mode,
    make_context_key
)

# Creating semantic types
cmd = make_command_id("help")
opt = make_option_key("--verbose")
flag = make_flag_name("--debug")
arg = make_argument_value("output.txt")
mode = make_parse_mode("semantic")
ctx_key = make_context_key("current_command")
```

## Type Aliases for Collections

Use provided type aliases for better readability:

```python
from cli_patterns.core.parser_types import CommandList, OptionDict, FlagSet

# Type-safe collections
commands: CommandList = [make_command_id("help"), make_command_id("run")]
options: OptionDict = {make_option_key("--output"): "file.txt"}
flags: FlagSet = {make_flag_name("--verbose"), make_flag_name("--debug")}
```

## Working with SemanticParseResult

The `SemanticParseResult` class provides a type-safe parse result:

```python
from cli_patterns.ui.parser.semantic_result import SemanticParseResult
from cli_patterns.core.parser_types import make_command_id, make_option_key

# Creating a semantic parse result
result = SemanticParseResult(
    command=make_command_id("test"),
    options={make_option_key("--coverage"): "true"},
    arguments=["test_file.py"],
    mode=make_parse_mode("text")
)

# Accessing typed fields
cmd: CommandId = result.command
opts: dict[OptionKey, str] = result.options
```

## Error Handling with Semantic Types

The `SemanticParseError` provides rich error context:

```python
from cli_patterns.ui.parser.semantic_errors import SemanticParseError
from cli_patterns.core.parser_types import make_command_id, make_option_key

# Creating semantic errors
error = SemanticParseError(
    message="Unknown option",
    command=make_command_id("test"),
    invalid_option=make_option_key("--unknown"),
    valid_options=[make_option_key("--verbose"), make_option_key("--output")],
    suggestions=[make_command_id("test")]
)

# Accessing semantic fields
cmd: CommandId = error.command
invalid: OptionKey = error.invalid_option
valid: list[OptionKey] = error.valid_options
```

## Best Practices

### 1. Use Factory Functions
Always use factory functions rather than direct type casting:
```python
# Good
cmd = make_command_id("help")

# Avoid
cmd = CommandId("help")  # Works but less clear
```

### 2. Maintain Type Consistency
Keep semantic types throughout your parser pipeline:
```python
def process_command(cmd: CommandId) -> CommandId:
    # Process and return same type
    return cmd

# Don't mix types unnecessarily
def process_command(cmd: CommandId) -> str:  # Avoid unless needed
    return str(cmd)
```

### 3. Use Type Aliases
Leverage type aliases for complex types:
```python
from cli_patterns.core.parser_types import CommandList, OptionDict

def get_commands() -> CommandList:
    return [make_command_id("help"), make_command_id("run")]

def get_options() -> OptionDict:
    return {make_option_key("--verbose"): "true"}
```

### 4. Document Type Conversions
When converting between semantic and regular types, document why:
```python
# Convert to string for display to user
display_name = str(command_id)

# Convert from user input to semantic type
command_id = make_command_id(user_input.strip())
```

## Extending the Type System

To add new semantic types:

1. Define the type in `core/parser_types.py`:
```python
from typing import NewType

# Define new semantic type
ConfigKey = NewType('ConfigKey', str)

# Add factory function
def make_config_key(value: str) -> ConfigKey:
    return ConfigKey(value)

# Add type alias if needed
ConfigDict = dict[ConfigKey, str]
```

2. Add conversion support if needed:
```python
class SemanticConfig:
    def __init__(self, config: dict[ConfigKey, str]):
        self.config = config

    @classmethod
    def from_dict(cls, config: dict[str, str]) -> 'SemanticConfig':
        return cls({make_config_key(k): v for k, v in config.items()})

    def to_dict(self) -> dict[str, str]:
        return {str(k): v for k, v in self.config.items()}
```

## Performance Considerations

Semantic types have **zero runtime overhead** because:
- `NewType` creates aliases at compile time only
- No runtime type checking or validation
- Type information is erased after compilation
- Factory functions are simple identity functions

## IDE Support

Semantic types improve IDE experience:
- Autocomplete shows only valid operations for each type
- Type checking catches mixing of incompatible types
- Better documentation through meaningful type names
- Refactoring tools understand type relationships

## Troubleshooting

### Common Issues

1. **Type Mismatch Errors**
```python
# Error: Cannot assign str to CommandId
cmd: CommandId = "help"  # ❌

# Fix: Use factory function
cmd: CommandId = make_command_id("help")  # ✅
```

2. **Missing Conversions**
```python
# Error: dict[str, str] not compatible with OptionDict
options: OptionDict = {"--verbose": "true"}  # ❌

# Fix: Convert keys to semantic types
options: OptionDict = {make_option_key("--verbose"): "true"}  # ✅
```

3. **JSON Serialization**
```python
import json
from cli_patterns.core.parser_types import CommandId, make_command_id

cmd = make_command_id("help")

# Semantic types serialize as strings
json_str = json.dumps({"command": cmd})  # Works fine

# Deserialize needs conversion
data = json.loads(json_str)
cmd = make_command_id(data["command"])  # Convert back to semantic type
```

## Further Reading

- [Python NewType Documentation](https://docs.python.org/3/library/typing.html#newtype)
- [MyPy Documentation on NewType](https://mypy.readthedocs.io/en/stable/more_types.html#newtypes)
- [CLI Patterns Architecture Guide](../CLAUDE.md)