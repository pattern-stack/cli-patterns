"""Semantic text parser using semantic types for enhanced type safety.

This module provides SemanticTextParser, which is like TextParser but works
with semantic types and provides semantic-aware parsing capabilities.
"""

from __future__ import annotations

import shlex
from typing import Optional

from cli_patterns.core.parser_types import (
    CommandId,
    make_argument_value,
    make_command_id,
    make_flag_name,
    make_option_key,
)
from cli_patterns.ui.parser.semantic_context import SemanticContext
from cli_patterns.ui.parser.semantic_errors import SemanticParseError
from cli_patterns.ui.parser.semantic_registry import SemanticCommandRegistry
from cli_patterns.ui.parser.semantic_result import SemanticParseResult


class SemanticTextParser:
    """Parser for standard text-based commands with semantic type support.

    Handles parsing of commands with arguments, short/long flags, and key-value options,
    returning semantic types for enhanced type safety and better intellisense support.
    """

    def __init__(self) -> None:
        """Initialize semantic text parser."""
        self._registry: Optional[SemanticCommandRegistry] = None

    def set_registry(self, registry: SemanticCommandRegistry) -> None:
        """Set the command registry for validation and suggestions.

        Args:
            registry: Semantic command registry to use
        """
        self._registry = registry

    def can_parse(self, input_str: str, context: SemanticContext) -> bool:
        """Check if input can be parsed by this semantic text parser.

        Args:
            input_str: Input string to check
            context: Semantic parsing context

        Returns:
            True if input is non-empty text that doesn't start with shell prefix
        """
        if not input_str or not input_str.strip():
            return False

        # Don't handle shell commands (those start with !)
        if input_str.lstrip().startswith("!"):
            return False

        return True

    def parse(self, input_str: str, context: SemanticContext) -> SemanticParseResult:
        """Parse text input into structured semantic command result.

        Args:
            input_str: Input string to parse
            context: Semantic parsing context

        Returns:
            SemanticParseResult with parsed command, args, flags, and options

        Raises:
            SemanticParseError: If parsing fails or command is unknown
        """
        if not self.can_parse(input_str, context):
            if not input_str.strip():
                raise SemanticParseError(
                    error_type="EMPTY_INPUT",
                    message="Empty input cannot be parsed",
                    suggestions=[make_command_id("help")],
                )
            else:
                raise SemanticParseError(
                    error_type="INVALID_INPUT",
                    message="Input cannot be parsed by text parser",
                    suggestions=[make_command_id("help")],
                )

        try:
            # Use shlex for proper quote handling
            tokens = shlex.split(input_str.strip())
        except ValueError as e:
            # Handle shlex errors (e.g., unmatched quotes)
            error_msg = str(e).replace("quotation", "quote")
            raise SemanticParseError(
                error_type="QUOTE_MISMATCH",
                message=f"Syntax error in command: {error_msg}",
                suggestions=[make_command_id("help")],
            ) from e

        if not tokens:
            raise SemanticParseError(
                error_type="EMPTY_INPUT",
                message="No command found after parsing",
                suggestions=[make_command_id("help")],
            )

        # First token is the command
        command_str = tokens[0]
        command = make_command_id(command_str)

        # Check if command is registered (if we have a registry)
        if self._registry and not self._registry.is_registered(command):
            suggestions = self._registry.get_suggestions(command_str, max_suggestions=3)
            if not suggestions:
                suggestions = [make_command_id("help")]

            raise SemanticParseError(
                error_type="UNKNOWN_COMMAND",
                message=f"Unknown command: {command_str}",
                command=command,
                suggestions=suggestions,
            )

        # Parse remaining tokens into args, flags, and options
        args = []
        flags = set()
        options = {}

        i = 1
        while i < len(tokens):
            token = tokens[i]

            if token.startswith("--"):
                # Long option handling
                if "=" in token:
                    # Format: --key=value
                    key_value = token[2:]  # Remove --
                    if "=" in key_value:
                        key, value = key_value.split("=", 1)
                        options[make_option_key(key)] = make_argument_value(value)
                else:
                    # Format: --key value (next token is value)
                    key = token[2:]  # Remove --
                    if i + 1 < len(tokens) and not tokens[i + 1].startswith("-"):
                        options[make_option_key(key)] = make_argument_value(
                            tokens[i + 1]
                        )
                        i += 1  # Skip the value token
                    else:
                        # Treat as flag if no value follows
                        flags.add(make_flag_name(key))

            elif token.startswith("-") and len(token) > 1:
                # Short flag(s) handling
                flag_chars = token[1:]  # Remove -
                for char in flag_chars:
                    flags.add(make_flag_name(char))

            else:
                # Regular argument
                args.append(make_argument_value(token))

            i += 1

        return SemanticParseResult(
            command=command,
            args=args,
            flags=flags,
            options=options,
            raw_input=input_str,
        )

    def get_suggestions(self, partial: str) -> list[CommandId]:
        """Get completion suggestions for partial input.

        Args:
            partial: Partial input to complete

        Returns:
            List of semantic command suggestions
        """
        if not self._registry:
            # Return some default suggestions if no registry
            defaults = ["help", "status", "version"]
            return [make_command_id(cmd) for cmd in defaults if cmd.startswith(partial)]

        return self._registry.get_suggestions(partial)
