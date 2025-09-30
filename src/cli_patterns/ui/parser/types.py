"""Core types for the parser system."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Optional

from rich.console import Group, RenderableType
from rich.text import Text

from cli_patterns.ui.design.tokens import HierarchyToken, StatusToken

if TYPE_CHECKING:
    pass


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
        display_metadata: Optional display metadata for enhanced formatting
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
        # display_metadata is optional and can be set after creation
        # This maintains backward compatibility while enabling enhanced formatting

    def __str__(self) -> str:
        """String representation of the error."""
        return f"{self.error_type}: {self.message}"

    def __rich__(self) -> RenderableType:
        """Rich rendering protocol implementation for automatic themed display.

        Returns:
            RenderableType (Group) containing styled error message and suggestions
        """
        # Map error_type to StatusToken
        status_token = self._get_status_token()

        # Create styled error message
        error_text = Text()
        error_text.append(
            f"{self.error_type}: ", style=self._get_status_style(status_token)
        )
        error_text.append(self.message)

        # Create suggestions list with hierarchy styling (limit to 3)
        renderables: list[RenderableType] = [error_text]

        if self.suggestions:
            # Add "Did you mean:" prompt
            prompt_text = Text(
                "\n\nDid you mean:", style=self._get_status_style(StatusToken.INFO)
            )
            renderables.append(prompt_text)

            # Add up to 3 suggestions with hierarchy styling
            for idx, suggestion in enumerate(self.suggestions[:3]):
                hierarchy = self._get_suggestion_hierarchy(idx)
                suggestion_text = Text()
                suggestion_text.append(
                    f"\n  • {suggestion}", style=self._get_hierarchy_style(hierarchy)
                )
                renderables.append(suggestion_text)

        return Group(*renderables)

    def _get_status_token(self) -> StatusToken:
        """Map error_type to appropriate StatusToken.

        Returns:
            StatusToken based on error_type
        """
        error_type_lower = self.error_type.lower()

        if "syntax" in error_type_lower:
            return StatusToken.ERROR
        elif (
            "unknown_command" in error_type_lower
            or "command_not_found" in error_type_lower
        ):
            return StatusToken.WARNING
        elif (
            "invalid_args" in error_type_lower or "invalid_argument" in error_type_lower
        ):
            return StatusToken.ERROR
        elif "deprecated" in error_type_lower:
            return StatusToken.WARNING
        else:
            # Default to ERROR for unknown error types
            return StatusToken.ERROR

    def _get_suggestion_hierarchy(self, index: int) -> HierarchyToken:
        """Get hierarchy token for suggestion based on ranking.

        Args:
            index: Position in suggestions list (0-based)

        Returns:
            HierarchyToken indicating visual importance
        """
        if index == 0:
            return HierarchyToken.PRIMARY  # Best match
        elif index == 1:
            return HierarchyToken.SECONDARY  # Good match
        else:
            return HierarchyToken.TERTIARY  # Possible match

    def _get_status_style(self, status: StatusToken) -> str:
        """Get Rich style string for StatusToken.

        Args:
            status: StatusToken to convert to style

        Returns:
            Rich style string
        """
        if status == StatusToken.ERROR:
            return "bold red"
        elif status == StatusToken.WARNING:
            return "bold yellow"
        elif status == StatusToken.INFO:
            return "blue"
        elif status == StatusToken.SUCCESS:
            return "bold green"
        elif status == StatusToken.RUNNING:
            return "cyan"
        elif status == StatusToken.MUTED:
            return "dim"
        else:
            return "default"

    def _get_hierarchy_style(self, hierarchy: HierarchyToken) -> str:
        """Get Rich style string for HierarchyToken.

        Args:
            hierarchy: HierarchyToken to convert to style

        Returns:
            Rich style string
        """
        if hierarchy == HierarchyToken.PRIMARY:
            return "bold"
        elif hierarchy == HierarchyToken.SECONDARY:
            return "default"
        elif hierarchy == HierarchyToken.TERTIARY:
            return "dim"
        elif hierarchy == HierarchyToken.QUATERNARY:
            return "dim italic"
        else:
            return "default"


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
