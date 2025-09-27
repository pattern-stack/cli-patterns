"""Command registry for managing available commands and providing suggestions."""

from __future__ import annotations

import difflib
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any, Callable, Optional

# No longer need ParseError import for registry validation


@dataclass
class CommandMetadata:
    """Metadata for a registered command.

    Attributes:
        name: Primary command name
        description: Human-readable description
        aliases: List of alternative names for the command
        category: Command category for grouping
        hidden: Whether command should be hidden from normal listings
        handler: Optional function to handle command execution
    """

    name: str
    description: str = ""
    aliases: list[str] = field(default_factory=list)
    category: str = "general"
    hidden: bool = False
    handler: Optional[Callable[..., Any]] = None

    def __post_init__(self) -> None:
        """Validate command metadata after initialization."""
        if not self.name or not self.name.strip():
            raise ValueError("Command name cannot be empty")

    def __str__(self) -> str:
        """String representation of command metadata."""
        alias_str = f" (aliases: {', '.join(self.aliases)})" if self.aliases else ""
        return f"{self.name}: {self.description}{alias_str}"


class CommandRegistry:
    """Registry for managing available commands and providing completion suggestions.

    The registry maintains a collection of commands with metadata including
    aliases, descriptions, and categories. It provides lookup capabilities
    and intelligent suggestions for typos and partial matches.
    """

    def __init__(self, cache_size: int = 128) -> None:
        """Initialize empty command registry.

        Args:
            cache_size: Maximum number of entries to cache for suggestion lookups.
                       Set to 0 to disable caching.
        """
        self._commands: dict[str, CommandMetadata] = {}
        self._aliases: dict[str, str] = {}  # alias -> command_name mapping
        self._categories: set[str] = set()

        # Create cached version of suggestion computation if caching is enabled
        if cache_size > 0:
            self._cached_suggestions: Callable[[str, int], list[str]] = lru_cache(
                maxsize=cache_size
            )(self._compute_suggestions)
        else:
            # No caching - use direct computation
            self._cached_suggestions = self._compute_suggestions

    def register(self, metadata: CommandMetadata) -> None:
        """Register a command with the registry.

        Args:
            metadata: Command metadata to register

        Raises:
            ParseError: If command name conflicts with existing command or alias
        """
        # Check for name conflicts
        if metadata.name in self._commands:
            raise ValueError(f"Command '{metadata.name}' is already registered")

        if metadata.name in self._aliases:
            existing_cmd = self._aliases[metadata.name]
            raise ValueError(
                f"Command name '{metadata.name}' conflicts with alias for '{existing_cmd}'"
            )

        # Check for alias conflicts
        for alias in metadata.aliases:
            if alias in self._commands:
                raise ValueError(f"Alias '{alias}' conflicts with existing command")
            if alias in self._aliases:
                existing_cmd = self._aliases[alias]
                raise ValueError(
                    f"Alias '{alias}' is already used by command '{existing_cmd}'"
                )

        # Register the command
        self._commands[metadata.name] = metadata

        # Register aliases
        for alias in metadata.aliases:
            self._aliases[alias] = metadata.name

        # Track category
        self._categories.add(metadata.category)

        # Clear suggestion cache since command set has changed
        if hasattr(self, "_cached_suggestions") and hasattr(
            self._cached_suggestions, "cache_clear"
        ):
            self._cached_suggestions.cache_clear()

    def register_command(self, metadata: CommandMetadata) -> None:
        """Register a command (alias for register method).

        Args:
            metadata: Command metadata to register
        """
        self.register(metadata)

    def unregister(self, name: str) -> bool:
        """Unregister a command from the registry.

        Args:
            name: Name of command to unregister

        Returns:
            True if command was found and removed, False otherwise
        """
        if name not in self._commands:
            return False

        metadata = self._commands[name]

        # Remove aliases
        for alias in metadata.aliases:
            self._aliases.pop(alias, None)

        # Remove command
        del self._commands[name]

        # Clean up category if no other commands use it
        if not any(
            cmd.category == metadata.category for cmd in self._commands.values()
        ):
            self._categories.discard(metadata.category)

        # Clear suggestion cache since command set has changed
        if hasattr(self, "_cached_suggestions") and hasattr(
            self._cached_suggestions, "cache_clear"
        ):
            self._cached_suggestions.cache_clear()

        return True

    def get(self, name: str) -> Optional[CommandMetadata]:
        """Get command metadata by name or alias.

        Args:
            name: Command name or alias to look up

        Returns:
            CommandMetadata if found, None otherwise
        """
        # Direct command name lookup
        if name in self._commands:
            return self._commands[name]

        # Alias lookup
        if name in self._aliases:
            command_name = self._aliases[name]
            return self._commands.get(command_name)

        return None

    def lookup_command(self, name: str) -> Optional[CommandMetadata]:
        """Look up command by name or alias (case-insensitive).

        Args:
            name: Command name or alias to look up

        Returns:
            CommandMetadata if found, None otherwise
        """
        if not name:
            return None

        # Try exact match first
        result = self.get(name)
        if result is not None:
            return result

        # Try case-insensitive match
        name_lower = name.lower()

        # Check command names (case-insensitive)
        for cmd_name, metadata in self._commands.items():
            if cmd_name.lower() == name_lower:
                return metadata

        # Check aliases (case-insensitive)
        for alias, cmd_name in self._aliases.items():
            if alias.lower() == name_lower:
                return self._commands.get(cmd_name)

        return None

    def list_commands(self, category: Optional[str] = None) -> list[CommandMetadata]:
        """List all registered commands, optionally filtered by category.

        Args:
            category: Optional category filter

        Returns:
            List of CommandMetadata objects
        """
        commands = list(self._commands.values())

        if category is not None:
            commands = [cmd for cmd in commands if cmd.category == category]

        # Sort by name for consistent output
        return sorted(commands, key=lambda cmd: cmd.name)

    def get_categories(self) -> list[str]:
        """Get list of all command categories.

        Returns:
            Sorted list of category names
        """
        return sorted(self._categories)

    def get_suggestions(self, partial: str, limit: int = 5) -> list[str]:
        """Get command name suggestions based on partial input.

        Uses an LRU cache to improve performance for repeated lookups.
        Cache is automatically cleared when commands are registered/unregistered.

        Args:
            partial: Partial command name
            limit: Maximum number of suggestions to return

        Returns:
            List of suggested command names
        """
        return self._cached_suggestions(partial, limit)

    def _compute_suggestions(self, partial: str, limit: int) -> list[str]:
        """Compute command name suggestions based on partial input.

        This is the internal method that performs the actual suggestion computation.
        It is wrapped with an LRU cache for performance.

        Args:
            partial: Partial command name
            limit: Maximum number of suggestions to return

        Returns:
            List of suggested command names
        """
        if not partial:
            # Return most common commands for empty input
            common_commands = ["help", "list", "status", "config", "quit"]
            available = [cmd for cmd in common_commands if cmd in self._commands]
            return available[:limit]

        suggestions = []
        partial_lower = partial.lower()

        # Collect all possible names (commands + aliases)
        all_names = set(self._commands.keys()) | set(self._aliases.keys())

        # Exact prefix matches (highest priority)
        prefix_matches = [
            name for name in all_names if name.lower().startswith(partial_lower)
        ]

        # Fuzzy matches using difflib
        fuzzy_matches = difflib.get_close_matches(
            partial, all_names, n=limit * 2, cutoff=0.4
        )

        # Combine and deduplicate while preserving order
        seen = set()
        for matches in [prefix_matches, fuzzy_matches]:
            for match in matches:
                if match not in seen:
                    suggestions.append(match)
                    seen.add(match)
                if len(suggestions) >= limit:
                    break
            if len(suggestions) >= limit:
                break

        return suggestions[:limit]

    def get_typo_suggestions(self, typo: str) -> list[str]:
        """Get suggestions for potential typos in command names.

        Args:
            typo: Potentially misspelled command name

        Returns:
            List of suggested corrections
        """
        return self.get_suggestions(typo, limit=10)
