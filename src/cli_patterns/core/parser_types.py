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

from typing import NewType

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
def make_command_id(value: str) -> CommandId:
    """Create a CommandId from a string value.

    Args:
        value: String value to convert to CommandId

    Returns:
        CommandId with semantic type safety
    """
    return CommandId(value)


def make_option_key(value: str) -> OptionKey:
    """Create an OptionKey from a string value.

    Args:
        value: String value to convert to OptionKey

    Returns:
        OptionKey with semantic type safety
    """
    return OptionKey(value)


def make_flag_name(value: str) -> FlagName:
    """Create a FlagName from a string value.

    Args:
        value: String value to convert to FlagName

    Returns:
        FlagName with semantic type safety
    """
    return FlagName(value)


def make_argument_value(value: str) -> ArgumentValue:
    """Create an ArgumentValue from a string value.

    Args:
        value: String value to convert to ArgumentValue

    Returns:
        ArgumentValue with semantic type safety
    """
    return ArgumentValue(value)


def make_parse_mode(value: str) -> ParseMode:
    """Create a ParseMode from a string value.

    Args:
        value: String value to convert to ParseMode

    Returns:
        ParseMode with semantic type safety
    """
    return ParseMode(value)


def make_context_key(value: str) -> ContextKey:
    """Create a ContextKey from a string value.

    Args:
        value: String value to convert to ContextKey

    Returns:
        ContextKey with semantic type safety
    """
    return ContextKey(value)
