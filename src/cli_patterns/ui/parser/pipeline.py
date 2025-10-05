"""Parser pipeline for routing input to appropriate parsers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

from cli_patterns.core.models import SessionState
from cli_patterns.ui.parser.protocols import Parser
from cli_patterns.ui.parser.types import ParseError, ParseResult


@dataclass
class _ParserEntry:
    """Internal entry for storing parser with metadata."""

    parser: Parser
    condition: Optional[Callable[[str, SessionState], bool]]
    priority: int


class ParserPipeline:
    """Pipeline for routing input to the appropriate parser.

    The pipeline maintains a list of parsers with optional conditions and priorities.
    When parsing input, it tries each parser in order until one succeeds.
    """

    def __init__(self) -> None:
        """Initialize empty parser pipeline."""
        self._parsers: list[_ParserEntry] = []

    def add_parser(
        self,
        parser: Parser,
        condition: Optional[Callable[[str, SessionState], bool]] = None,
        priority: int = 0,
    ) -> None:
        """Add a parser to the pipeline.

        Args:
            parser: Parser instance to add
            condition: Optional condition function that returns True if parser should handle input
            priority: Priority for ordering (higher numbers = higher priority, default 0)
        """
        entry = _ParserEntry(parser=parser, condition=condition, priority=priority)
        self._parsers.append(entry)

        # Sort by priority (higher numbers first), maintaining insertion order for same priority
        self._parsers.sort(
            key=lambda x: (
                -x.priority,
                (
                    self._parsers.index(x)
                    if x in self._parsers[:-1]
                    else len(self._parsers)
                ),
            )
        )

    def remove_parser(self, parser: Parser) -> bool:
        """Remove a parser from the pipeline.

        Args:
            parser: Parser instance to remove

        Returns:
            True if parser was found and removed, False otherwise
        """
        for i, entry in enumerate(self._parsers):
            if entry.parser is parser:
                self._parsers.pop(i)
                return True
        return False

    def parse(self, input_str: str, session: SessionState) -> ParseResult:
        """Parse input using the first matching parser in the pipeline.

        Args:
            input_str: Input string to parse
            session: Current session state

        Returns:
            ParseResult from the first parser that can handle the input

        Raises:
            ParseError: If no parser can handle the input or parsing fails
        """
        if not self._parsers:
            raise ParseError(
                error_type="NO_PARSERS",
                message="No parsers available in pipeline",
                suggestions=["Add parsers to the pipeline"],
            )

        matching_parsers = []
        condition_errors = []

        # Find all parsers that can handle the input
        for entry in self._parsers:
            try:
                # Check condition if provided
                if entry.condition is not None:
                    if not entry.condition(input_str, session):
                        continue

                # Check if parser can handle the input
                if hasattr(entry.parser, "can_parse"):
                    if entry.parser.can_parse(input_str, session):
                        matching_parsers.append(entry)
                else:
                    # If no can_parse method, assume it can handle it
                    matching_parsers.append(entry)

            except Exception as e:
                # Condition function failed, skip this parser
                condition_errors.append(f"Condition failed for parser: {e}")
                continue

        if not matching_parsers:
            error_msg = "No parser can handle the input"
            if condition_errors:
                error_msg += f". Condition errors: {'; '.join(condition_errors)}"

            raise ParseError(
                error_type="NO_MATCHING_PARSER",
                message=error_msg,
                suggestions=[
                    "Check input format",
                    "Add appropriate parser to pipeline",
                ],
            )

        # Try the first matching parser (highest priority)
        parser_entry = matching_parsers[0]

        try:
            return parser_entry.parser.parse(input_str, session)
        except ParseError:
            # Re-raise parse errors from the parser
            raise
        except Exception as e:
            # Convert other exceptions to ParseError
            raise ParseError(
                error_type="PARSER_ERROR",
                message=f"Parser failed: {str(e)}",
                suggestions=["Check input format", "Try a different parser"],
            ) from e

    def clear(self) -> None:
        """Clear all parsers from the pipeline."""
        self._parsers.clear()

    @property
    def parser_count(self) -> int:
        """Get the number of parsers in the pipeline."""
        return len(self._parsers)
