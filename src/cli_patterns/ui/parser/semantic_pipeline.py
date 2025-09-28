"""Semantic parser pipeline for routing input to semantic parsers.

This module provides SemanticParserPipeline, which routes input to semantic parsers
that work with semantic types and contexts for enhanced type safety.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional, Protocol, runtime_checkable

from cli_patterns.core.parser_types import CommandId
from cli_patterns.ui.parser.semantic_context import SemanticContext
from cli_patterns.ui.parser.semantic_errors import SemanticParseError
from cli_patterns.ui.parser.semantic_result import SemanticParseResult


@runtime_checkable
class SemanticParser(Protocol):
    """Protocol defining the interface for semantic command parsers.

    Semantic parsers work with semantic types and contexts to provide
    enhanced type safety for command parsing operations.
    """

    def can_parse(self, input_str: str, context: SemanticContext) -> bool:
        """Determine if this parser can handle the given input.

        Args:
            input_str: Raw input string to evaluate
            context: Current semantic parsing context

        Returns:
            True if this parser can handle the input, False otherwise
        """
        ...

    def parse(self, input_str: str, context: SemanticContext) -> SemanticParseResult:
        """Parse the input string into a structured SemanticParseResult.

        Args:
            input_str: Raw input string to parse
            context: Current semantic parsing context

        Returns:
            SemanticParseResult containing parsed command, args, flags, and options

        Raises:
            SemanticParseError: If parsing fails or input is invalid
        """
        ...

    def get_suggestions(self, partial: str) -> list[CommandId]:
        """Get completion suggestions for partial input.

        Args:
            partial: Partial input string to complete

        Returns:
            List of suggested semantic command completions
        """
        ...


@dataclass
class _SemanticParserEntry:
    """Internal entry for storing semantic parser with metadata."""

    parser: SemanticParser
    condition: Optional[Callable[[str, SemanticContext], bool]]
    priority: int


class SemanticParserPipeline:
    """Pipeline for routing input to appropriate semantic parsers.

    The pipeline maintains a list of semantic parsers with optional conditions and priorities.
    When parsing input, it tries each parser in order until one succeeds, maintaining
    semantic type safety throughout the process.
    """

    def __init__(self) -> None:
        """Initialize empty semantic parser pipeline."""
        self._parsers: list[_SemanticParserEntry] = []

    def add_parser(
        self,
        parser: SemanticParser,
        condition: Optional[Callable[[str, SemanticContext], bool]] = None,
        priority: int = 0,
    ) -> None:
        """Add a semantic parser to the pipeline.

        Args:
            parser: Semantic parser instance to add
            condition: Optional condition function that returns True if parser should handle input
            priority: Priority for ordering (higher numbers = higher priority, default 0)
        """
        entry = _SemanticParserEntry(
            parser=parser, condition=condition, priority=priority
        )
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

    def remove_parser(self, parser: SemanticParser) -> bool:
        """Remove a semantic parser from the pipeline.

        Args:
            parser: Semantic parser instance to remove

        Returns:
            True if parser was found and removed, False otherwise
        """
        for i, entry in enumerate(self._parsers):
            if entry.parser is parser:
                self._parsers.pop(i)
                return True
        return False

    def parse(self, input_str: str, context: SemanticContext) -> SemanticParseResult:
        """Parse input using the first matching semantic parser in the pipeline.

        Args:
            input_str: Input string to parse
            context: Semantic parsing context

        Returns:
            SemanticParseResult from the first parser that can handle the input

        Raises:
            SemanticParseError: If no parser can handle the input or parsing fails
        """
        if not self._parsers:
            raise SemanticParseError(
                error_type="NO_PARSERS",
                message="No parsers available in pipeline",
                suggestions=[],
            )

        matching_parsers = []
        condition_errors = []

        # Find all parsers that can handle the input
        for entry in self._parsers:
            try:
                # Check condition if provided
                if entry.condition is not None:
                    if not entry.condition(input_str, context):
                        continue

                # Check if parser can handle the input
                if hasattr(entry.parser, "can_parse"):
                    if entry.parser.can_parse(input_str, context):
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

            raise SemanticParseError(
                error_type="NO_MATCHING_PARSER",
                message=error_msg,
                suggestions=[],
            )

        # Try the first matching parser (highest priority)
        parser_entry = matching_parsers[0]

        try:
            return parser_entry.parser.parse(input_str, context)
        except SemanticParseError:
            # Re-raise semantic parse errors from the parser
            raise
        except Exception as e:
            # Convert other exceptions to SemanticParseError
            raise SemanticParseError(
                error_type="PARSER_ERROR",
                message=f"Parser failed: {str(e)}",
                suggestions=[],
            ) from e

    def clear(self) -> None:
        """Clear all parsers from the pipeline."""
        self._parsers.clear()

    @property
    def parser_count(self) -> int:
        """Get the number of parsers in the pipeline."""
        return len(self._parsers)
