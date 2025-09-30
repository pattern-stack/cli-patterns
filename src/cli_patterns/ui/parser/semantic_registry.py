"""Semantic command registry using semantic types for type-safe command management.

This module provides SemanticCommandRegistry, which manages command metadata
using semantic types for enhanced type safety and better intellisense support.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from cli_patterns.core.parser_types import CommandId, FlagName, OptionKey


@dataclass
class CommandMetadata:
    """Metadata for a registered command using semantic types.

    Attributes:
        description: Human-readable command description
        category: Command category for grouping
        aliases: List of command aliases
        options: List of valid option keys for this command
        flags: List of valid flag names for this command
    """

    description: str
    category: str = "general"
    aliases: list[CommandId] = field(default_factory=list)
    options: list[OptionKey] = field(default_factory=list)
    flags: list[FlagName] = field(default_factory=list)


class SemanticCommandRegistry:
    """Registry for managing commands with semantic type safety.

    This registry stores command metadata using semantic types to provide
    type-safe operations for command registration, lookup, and suggestions.
    """

    def __init__(self) -> None:
        """Initialize empty command registry."""
        self._commands: dict[CommandId, CommandMetadata] = {}

    def register_command(
        self,
        command: CommandId,
        description: str,
        category: str = "general",
        aliases: Optional[list[CommandId]] = None,
        options: Optional[list[OptionKey]] = None,
        flags: Optional[list[FlagName]] = None,
    ) -> None:
        """Register a command with its metadata.

        Args:
            command: Semantic command ID to register
            description: Human-readable command description
            category: Command category for grouping
            aliases: List of command aliases
            options: List of valid option keys for this command
            flags: List of valid flag names for this command
        """
        metadata = CommandMetadata(
            description=description,
            category=category,
            aliases=aliases or [],
            options=options or [],
            flags=flags or [],
        )
        self._commands[command] = metadata

    def is_registered(self, command: CommandId) -> bool:
        """Check if a command is registered.

        Args:
            command: Semantic command ID to check

        Returns:
            True if command is registered, False otherwise
        """
        return command in self._commands

    def get_command_metadata(self, command: CommandId) -> Optional[CommandMetadata]:
        """Get metadata for a registered command.

        Args:
            command: Semantic command ID to get metadata for

        Returns:
            CommandMetadata if command is registered, None otherwise
        """
        return self._commands.get(command)

    def get_suggestions(
        self, partial: str, max_suggestions: int = 5
    ) -> list[CommandId]:
        """Get command suggestions for a partial input.

        Args:
            partial: Partial command string to match against
            max_suggestions: Maximum number of suggestions to return

        Returns:
            List of matching command IDs as suggestions
        """
        if not partial:
            return []

        partial_lower = partial.lower()
        exact_matches = []
        partial_matches = []

        # Separate exact prefix matches from partial matches
        for command in self._commands:
            command_str = str(command).lower()
            if command_str.startswith(partial_lower):
                exact_matches.append(command)
            elif partial_lower in command_str:
                partial_matches.append(command)

        # Combine exact matches first, then partial matches
        suggestions = exact_matches + partial_matches
        return suggestions[:max_suggestions]

    def get_all_commands(self) -> list[CommandId]:
        """Get all registered commands.

        Returns:
            List of all registered command IDs
        """
        return list(self._commands.keys())

    def get_commands_by_category(self, category: str) -> list[CommandId]:
        """Get all commands in a specific category.

        Args:
            category: Category name to filter by

        Returns:
            List of command IDs in the specified category
        """
        return [
            command
            for command, metadata in self._commands.items()
            if metadata.category == category
        ]
