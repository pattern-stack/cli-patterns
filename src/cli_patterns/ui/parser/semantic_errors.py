"""Semantic parse errors using semantic types for enhanced error handling.

This module provides SemanticParseError, which extends ParseError to include
semantic type information for better error reporting and recovery.
"""

from __future__ import annotations

from typing import Any, Optional

from cli_patterns.core.parser_types import CommandId, OptionKey
from cli_patterns.ui.parser.types import ParseError


class SemanticParseError(ParseError):
    """Exception raised during semantic command parsing with semantic type context.

    This extends ParseError to include semantic type information that can be
    used for better error reporting and recovery mechanisms.

    Attributes:
        message: Human-readable error message
        error_type: Type of parsing error
        suggestions: List of suggested corrections (semantic types, shadows base class)
        command: Command that caused the error (if applicable)
        invalid_option: Invalid option key (if applicable)
        valid_options: List of valid option keys (if applicable)
        required_role: Required role for command (if applicable)
        current_role: Current user role (if applicable)
        context_info: Additional context information
    """

    def __init__(
        self,
        error_type: str,
        message: str,
        suggestions: Optional[list[CommandId]] = None,
        command: Optional[CommandId] = None,
        invalid_option: Optional[OptionKey] = None,
        valid_options: Optional[list[OptionKey]] = None,
        required_role: Optional[str] = None,
        current_role: Optional[str] = None,
        context_info: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize SemanticParseError.

        Args:
            error_type: Type/category of error
            message: Error message
            suggestions: Optional list of command suggestions for fixing the error
            command: Command that caused the error
            invalid_option: Invalid option key that caused the error
            valid_options: List of valid option keys
            required_role: Required role for command execution
            current_role: Current user role
            context_info: Additional context information
        """
        # Convert semantic suggestions to strings for base class
        string_suggestions: Optional[list[str]] = (
            [str(cmd) for cmd in suggestions] if suggestions else None
        )
        super().__init__(error_type, message, string_suggestions)

        # Store semantic type information - we shadow the base class suggestions
        # This is intentional to provide semantic type access
        self.suggestions: list[CommandId] = suggestions or []  # type: ignore[assignment]
        self.command = command
        self.invalid_option = invalid_option
        self.valid_options = valid_options or []
        self.required_role = required_role
        self.current_role = current_role
        self.context_info = context_info or {}
