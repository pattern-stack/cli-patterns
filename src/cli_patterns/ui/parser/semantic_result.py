"""Semantic parse result using semantic types for type safety.

This module provides SemanticParseResult, which is like ParseResult but uses
semantic types instead of plain strings for enhanced type safety.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from cli_patterns.core.parser_types import (
    ArgumentList,
    ArgumentValue,
    CommandId,
    FlagName,
    FlagSet,
    OptionDict,
    OptionKey,
    make_argument_value,
    make_command_id,
    make_flag_name,
    make_option_key,
)
from cli_patterns.ui.parser.types import ParseResult


@dataclass
class SemanticParseResult:
    """Result of parsing user input into structured command data using semantic types.

    This is the semantic type equivalent of ParseResult, providing type safety
    for command parsing operations while maintaining the same structure.

    Attributes:
        command: The main command parsed from input (semantic type)
        args: List of positional arguments (semantic types)
        flags: Set of single-letter flags (semantic types)
        options: Dictionary of key-value options (semantic types)
        raw_input: Original input string
        shell_command: Shell command for shell parsers (optional)
    """

    command: CommandId
    args: ArgumentList = field(default_factory=list)
    flags: FlagSet = field(default_factory=set)
    options: OptionDict = field(default_factory=dict)
    raw_input: str = ""
    shell_command: Optional[str] = None

    @classmethod
    def from_parse_result(cls, result: ParseResult) -> SemanticParseResult:
        """Create a SemanticParseResult from a regular ParseResult.

        Args:
            result: Regular ParseResult to convert

        Returns:
            SemanticParseResult with semantic types
        """
        return cls(
            command=make_command_id(result.command),
            args=[make_argument_value(arg) for arg in result.args],
            flags={make_flag_name(flag) for flag in result.flags},
            options={
                make_option_key(key): make_argument_value(value)
                for key, value in result.options.items()
            },
            raw_input=result.raw_input,
            shell_command=result.shell_command,
        )

    def to_parse_result(self) -> ParseResult:
        """Convert this SemanticParseResult to a regular ParseResult.

        Returns:
            Regular ParseResult with string types
        """
        return ParseResult(
            command=str(self.command),
            args=[str(arg) for arg in self.args],
            flags={str(flag) for flag in self.flags},
            options={str(key): str(value) for key, value in self.options.items()},
            raw_input=self.raw_input,
            shell_command=self.shell_command,
        )

    def has_flag(self, flag: FlagName) -> bool:
        """Check if a flag is present.

        Args:
            flag: Semantic flag name to check

        Returns:
            True if flag is present, False otherwise
        """
        return flag in self.flags

    def get_option(self, key: OptionKey) -> Optional[ArgumentValue]:
        """Get option value by key safely.

        Args:
            key: Semantic option key to retrieve

        Returns:
            Option value or None if key doesn't exist
        """
        return self.options.get(key)

    def get_arg(self, index: int) -> Optional[ArgumentValue]:
        """Get positional argument by index safely.

        Args:
            index: Position index to retrieve

        Returns:
            Positional argument at index or None if index is out of range
        """
        if 0 <= index < len(self.args):
            return self.args[index]
        return None
