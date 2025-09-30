"""Semantic types for the parser system.

This module defines semantic types that provide type safety for the parser system
while maintaining MyPy strict mode compliance. These are simple NewType definitions
that prevent type confusion without adding runtime validation complexity.

The semantic types help distinguish between different string contexts:
- CommandId: Represents a command identifier
- OptionKey: Represents an option key name
- FlagName: Represents a flag name
- ArgumentValue: Represents an argument value
- ParseMode: Represents a parsing mode
- ContextKey: Represents a context state key

All types are backed by strings but provide semantic meaning at the type level.
"""

from __future__ import annotations

from typing import Any, NewType

from typing_extensions import TypeGuard

# Core semantic types for parser system
CommandId = NewType("CommandId", str)
"""Semantic type for command identifiers."""

OptionKey = NewType("OptionKey", str)
"""Semantic type for option key names."""

FlagName = NewType("FlagName", str)
"""Semantic type for flag names."""

ArgumentValue = NewType("ArgumentValue", str)
"""Semantic type for argument values."""

ParseMode = NewType("ParseMode", str)
"""Semantic type for parsing modes."""

ContextKey = NewType("ContextKey", str)
"""Semantic type for context state keys."""

# Type aliases for common collections using semantic types
CommandList = list[CommandId]
"""Type alias for lists of command IDs."""

CommandSet = set[CommandId]
"""Type alias for sets of command IDs."""

OptionDict = dict[OptionKey, ArgumentValue]
"""Type alias for option dictionaries."""

FlagSet = set[FlagName]
"""Type alias for sets of flags."""

ArgumentList = list[ArgumentValue]
"""Type alias for lists of arguments."""

ContextState = dict[ContextKey, str]
"""Type alias for context state dictionaries."""


# Factory functions for creating semantic types
def make_command_id(value: str, validate: bool = False) -> CommandId:
    """Create a CommandId from a string value.

    Args:
        value: String value to convert to CommandId
        validate: If True, validate the input (default: False for zero overhead)

    Returns:
        CommandId with semantic type safety

    Raises:
        ValueError: If validate=True and value is invalid
    """
    if validate:
        if not value or not value.strip():
            raise ValueError("Command ID cannot be empty")
        if len(value) > 100:
            raise ValueError("Command ID is too long (max 100 characters)")
    return CommandId(value)


def make_option_key(value: str, validate: bool = False) -> OptionKey:
    """Create an OptionKey from a string value.

    Args:
        value: String value to convert to OptionKey
        validate: If True, validate the input (default: False for zero overhead)

    Returns:
        OptionKey with semantic type safety

    Raises:
        ValueError: If validate=True and value is invalid
    """
    if validate:
        if not value or not value.strip():
            raise ValueError("Option key cannot be empty")
        if not value.startswith(("-", "/")):
            raise ValueError("Option key must start with '-' or '/'")
        if len(value) > 100:
            raise ValueError("Option key is too long (max 100 characters)")
    return OptionKey(value)


def make_flag_name(value: str, validate: bool = False) -> FlagName:
    """Create a FlagName from a string value.

    Args:
        value: String value to convert to FlagName
        validate: If True, validate the input (default: False for zero overhead)

    Returns:
        FlagName with semantic type safety

    Raises:
        ValueError: If validate=True and value is invalid
    """
    if validate:
        if not value or not value.strip():
            raise ValueError("Flag name cannot be empty")
        if not value.startswith(("-", "/")):
            raise ValueError("Flag name must start with '-' or '/'")
        if len(value) > 100:
            raise ValueError("Flag name is too long (max 100 characters)")
    return FlagName(value)


def make_argument_value(value: str, validate: bool = False) -> ArgumentValue:
    """Create an ArgumentValue from a string value.

    Args:
        value: String value to convert to ArgumentValue
        validate: If True, validate the input (default: False for zero overhead)

    Returns:
        ArgumentValue with semantic type safety

    Raises:
        ValueError: If validate=True and value is invalid
    """
    if validate:
        if value is None:
            raise ValueError("Argument value cannot be None")
        if len(value) > 1000:
            raise ValueError("Argument value is too long (max 1000 characters)")
    return ArgumentValue(value)


def make_parse_mode(value: str, validate: bool = False) -> ParseMode:
    """Create a ParseMode from a string value.

    Args:
        value: String value to convert to ParseMode
        validate: If True, validate the input (default: False for zero overhead)

    Returns:
        ParseMode with semantic type safety

    Raises:
        ValueError: If validate=True and value is invalid
    """
    if validate:
        if not value or not value.strip():
            raise ValueError("Parse mode cannot be empty")
        valid_modes = {"text", "shell", "semantic", "interactive", "batch"}
        if value not in valid_modes:
            raise ValueError(
                f"Invalid parse mode: {value}. Must be one of {valid_modes}"
            )
    return ParseMode(value)


def make_context_key(value: str, validate: bool = False) -> ContextKey:
    """Create a ContextKey from a string value.

    Args:
        value: String value to convert to ContextKey
        validate: If True, validate the input (default: False for zero overhead)

    Returns:
        ContextKey with semantic type safety

    Raises:
        ValueError: If validate=True and value is invalid
    """
    if validate:
        if not value or not value.strip():
            raise ValueError("Context key cannot be empty")
        if len(value) > 100:
            raise ValueError("Context key is too long (max 100 characters)")
    return ContextKey(value)


# Type guard functions for runtime type checking
def is_command_id(value: Any) -> TypeGuard[CommandId]:
    """Check if a value is a CommandId at runtime.

    Args:
        value: Value to check

    Returns:
        True if value is a CommandId (string type), False otherwise

    Note:
        This is a type guard function that helps with type narrowing.
        At runtime, CommandId is just a string, so this checks for string type.
    """
    return isinstance(value, str)


def is_option_key(value: Any) -> TypeGuard[OptionKey]:
    """Check if a value is an OptionKey at runtime.

    Args:
        value: Value to check

    Returns:
        True if value is an OptionKey (string type), False otherwise

    Note:
        This is a type guard function that helps with type narrowing.
        At runtime, OptionKey is just a string, so this checks for string type.
    """
    return isinstance(value, str)


def is_flag_name(value: Any) -> TypeGuard[FlagName]:
    """Check if a value is a FlagName at runtime.

    Args:
        value: Value to check

    Returns:
        True if value is a FlagName (string type), False otherwise

    Note:
        This is a type guard function that helps with type narrowing.
        At runtime, FlagName is just a string, so this checks for string type.
    """
    return isinstance(value, str)


def is_argument_value(value: Any) -> TypeGuard[ArgumentValue]:
    """Check if a value is an ArgumentValue at runtime.

    Args:
        value: Value to check

    Returns:
        True if value is an ArgumentValue (string type), False otherwise

    Note:
        This is a type guard function that helps with type narrowing.
        At runtime, ArgumentValue is just a string, so this checks for string type.
    """
    return isinstance(value, str)


def is_parse_mode(value: Any) -> TypeGuard[ParseMode]:
    """Check if a value is a ParseMode at runtime.

    Args:
        value: Value to check

    Returns:
        True if value is a ParseMode (string type), False otherwise

    Note:
        This is a type guard function that helps with type narrowing.
        At runtime, ParseMode is just a string, so this checks for string type.
    """
    return isinstance(value, str)


def is_context_key(value: Any) -> TypeGuard[ContextKey]:
    """Check if a value is a ContextKey at runtime.

    Args:
        value: Value to check

    Returns:
        True if value is a ContextKey (string type), False otherwise

    Note:
        This is a type guard function that helps with type narrowing.
        At runtime, ContextKey is just a string, so this checks for string type.
    """
    return isinstance(value, str)
