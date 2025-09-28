"""Semantic context using semantic types for type safety.

This module provides SemanticContext, which is like Context but uses
semantic types instead of plain strings for enhanced type safety.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from cli_patterns.core.parser_types import (
    CommandId,
    CommandList,
    ContextKey,
    ContextState,
    ParseMode,
    make_command_id,
    make_context_key,
    make_parse_mode,
)
from cli_patterns.ui.parser.types import Context


@dataclass
class SemanticContext:
    """Parsing context containing session state and history using semantic types.

    This is the semantic type equivalent of Context, providing type safety
    for parsing context operations while maintaining the same structure.

    Attributes:
        mode: Current parsing mode (semantic type)
        history: Command history list (semantic types)
        session_state: Dictionary of session state data (semantic types)
        current_directory: Current working directory (optional)
    """

    mode: ParseMode = field(default_factory=lambda: make_parse_mode("text"))
    history: CommandList = field(default_factory=list)
    session_state: ContextState = field(default_factory=dict)
    current_directory: Optional[str] = None

    @classmethod
    def from_context(cls, context: Context) -> SemanticContext:
        """Create a SemanticContext from a regular Context.

        Args:
            context: Regular Context to convert

        Returns:
            SemanticContext with semantic types
        """
        return cls(
            mode=make_parse_mode(context.mode),
            history=[make_command_id(cmd) for cmd in context.history],
            session_state={
                make_context_key(key): value
                for key, value in context.session_state.items()
                if isinstance(
                    value, str
                )  # Only convert string values to maintain type safety
            },
            current_directory=context.current_directory,
        )

    def to_context(self) -> Context:
        """Convert this SemanticContext to a regular Context.

        Returns:
            Regular Context with string types
        """
        return Context(
            mode=str(self.mode),
            history=[str(cmd) for cmd in self.history],
            session_state={
                str(key): value for key, value in self.session_state.items()
            },
            current_directory=self.current_directory,
        )

    def add_to_history(self, command: CommandId) -> None:
        """Add command to history.

        Args:
            command: Semantic command to add to history
        """
        self.history.append(command)

    def get_recent_commands(self, count: int) -> CommandList:
        """Get the most recent commands from history.

        Args:
            count: Number of recent commands to retrieve

        Returns:
            List of recent commands (semantic types)
        """
        if count <= 0:
            return []
        return self.history[-count:]

    def get_state(
        self, key: ContextKey, default: Optional[str] = None
    ) -> Optional[str]:
        """Get session state value by key.

        Args:
            key: Semantic state key to retrieve
            default: Default value if key doesn't exist

        Returns:
            State value or default
        """
        return self.session_state.get(key, default)

    def set_state(self, key: ContextKey, value: Optional[str]) -> None:
        """Set session state value.

        Args:
            key: Semantic state key to set
            value: Value to set (None to remove key)
        """
        if value is None:
            self.session_state.pop(key, None)
        else:
            self.session_state[key] = value

    def has_state(self, key: ContextKey) -> bool:
        """Check if a state key exists.

        Args:
            key: Semantic state key to check

        Returns:
            True if key exists, False otherwise
        """
        return key in self.session_state

    def clear_history(self) -> None:
        """Clear command history."""
        self.history.clear()
