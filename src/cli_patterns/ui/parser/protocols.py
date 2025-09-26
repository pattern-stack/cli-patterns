"""Parser protocol definitions."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

# Always import types that are needed for runtime checking
from cli_patterns.ui.parser.types import Context, ParseResult


@runtime_checkable
class Parser(Protocol):
    """Protocol defining the interface for command parsers.

    Parsers are responsible for analyzing input text and converting it
    into structured ParseResult objects that can be used by the command
    execution system.
    """

    def can_parse(self, input: str, context: Context) -> bool:
        """Determine if this parser can handle the given input.

        Args:
            input: Raw input string to evaluate
            context: Current parsing context with mode, history, and state

        Returns:
            True if this parser can handle the input, False otherwise
        """
        ...

    def parse(self, input: str, context: Context) -> ParseResult:
        """Parse the input string into a structured ParseResult.

        Args:
            input: Raw input string to parse
            context: Current parsing context with mode, history, and state

        Returns:
            ParseResult containing parsed command, args, flags, and options

        Raises:
            ParseError: If parsing fails or input is invalid
        """
        ...

    def get_suggestions(self, partial: str) -> list[str]:
        """Get completion suggestions for partial input.

        Args:
            partial: Partial input string to complete

        Returns:
            List of suggested completions for the partial input
        """
        ...


# Explicitly set the runtime checkable attribute for older Python versions
Parser.__runtime_checkable__ = True
