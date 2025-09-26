"""Core types for the parser system."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class ParseResult:
    """Result of parsing user input into structured command data.

    Attributes:
        command: The main command parsed from input
        args: List of positional arguments
        flags: Set of single-letter flags (without dashes)
        options: Dictionary of key-value options
        raw_input: Original input string
        shell_command: Shell command for shell parsers (optional)
    """

    command: str
    args: list[str] = field(default_factory=list)
    flags: set[str] = field(default_factory=set)
    options: dict[str, str] = field(default_factory=dict)
    raw_input: str = ""
    shell_command: Optional[str] = None


@dataclass
class CommandArgs:
    """Structured container for command arguments.

    Attributes:
        positional: List of positional arguments in order
        named: Dictionary of named arguments (key-value pairs)
        flags: Set of boolean flags
    """

    positional: list[str] = field(default_factory=list)
    named: dict[str, str] = field(default_factory=dict)
    flags: set[str] = field(default_factory=set)

    def get_positional(
        self, index: int, default: Optional[str] = None
    ) -> Optional[str]:
        """Get positional argument by index safely.

        Args:
            index: Position index to retrieve
            default: Default value if index is out of range

        Returns:
            Positional argument at index or default value
        """
        if 0 <= index < len(self.positional):
            return self.positional[index]
        return default

    def get_named(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get named argument by key safely.

        Args:
            key: Named argument key
            default: Default value if key doesn't exist

        Returns:
            Named argument value or default value
        """
        return self.named.get(key, default)

    def has_flag(self, flag: str) -> bool:
        """Check if a flag is present.

        Args:
            flag: Flag name to check

        Returns:
            True if flag is present, False otherwise
        """
        return flag in self.flags


class ParseError(Exception):
    """Exception raised during command parsing.

    Attributes:
        message: Human-readable error message
        error_type: Type of parsing error
        suggestions: List of suggested corrections
    """

    def __init__(
        self, error_type: str, message: str, suggestions: Optional[list[str]] = None
    ) -> None:
        """Initialize ParseError.

        Args:
            error_type: Type/category of error
            message: Error message
            suggestions: Optional list of suggestions for fixing the error
        """
        super().__init__(message)
        self.error_type = error_type
        self.message = message
        self.suggestions = suggestions or []

    def __str__(self) -> str:
        """String representation of the error."""
        return f"{self.error_type}: {self.message}"


@dataclass
class Context:
    """Parsing context containing session state and history.

    Attributes:
        mode: Current parsing mode (e.g., 'interactive', 'batch')
        history: Command history list
        session_state: Dictionary of session state data
        current_directory: Current working directory (optional)
    """

    mode: str = "text"
    history: list[str] = field(default_factory=list)
    session_state: dict[str, Any] = field(default_factory=dict)
    current_directory: Optional[str] = None

    def add_to_history(self, command: str) -> None:
        """Add command to history.

        Args:
            command: Command string to add to history
        """
        self.history.append(command)

    def get_state(self, key: str, default: Any = None) -> Any:
        """Get session state value by key.

        Args:
            key: State key to retrieve
            default: Default value if key doesn't exist

        Returns:
            State value or default
        """
        return self.session_state.get(key, default)

    def set_state(self, key: str, value: Any) -> None:
        """Set session state value.

        Args:
            key: State key to set
            value: Value to set
        """
        self.session_state[key] = value

    def clear_history(self) -> None:
        """Clear command history."""
        self.history.clear()
