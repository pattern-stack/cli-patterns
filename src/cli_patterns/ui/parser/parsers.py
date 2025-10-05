"""Parser implementations for text and shell commands."""

from __future__ import annotations

import shlex

from cli_patterns.core.models import SessionState
from cli_patterns.ui.parser.types import ParseError, ParseResult


class TextParser:
    """Parser for standard text-based commands with flags and options.

    Handles parsing of commands with arguments, short/long flags, and key-value options.
    Supports proper quote handling using shlex for shell-like parsing.
    """

    def can_parse(self, input: str, session: SessionState) -> bool:
        """Check if input can be parsed by this text parser.

        Args:
            input: Input string to check
            session: Current session state

        Returns:
            True if input is non-empty text that doesn't start with shell prefix
        """
        if not input or not input.strip():
            return False

        # Don't handle shell commands (those start with !)
        if input.lstrip().startswith("!"):
            return False

        return True

    def parse(self, input: str, session: SessionState) -> ParseResult:
        """Parse text input into structured command result.

        Args:
            input: Input string to parse
            session: Current session state

        Returns:
            ParseResult with parsed command, args, flags, and options

        Raises:
            ParseError: If parsing fails (e.g., unmatched quotes, empty input)
        """
        if not self.can_parse(input, session):
            if not input.strip():
                raise ParseError(
                    error_type="EMPTY_INPUT",
                    message="Empty input cannot be parsed",
                    suggestions=["Enter a command to execute"],
                )
            else:
                raise ParseError(
                    error_type="INVALID_INPUT",
                    message="Input cannot be parsed by text parser",
                    suggestions=["Check command format"],
                )

        try:
            # Use shlex for proper quote handling
            tokens = shlex.split(input.strip())
        except ValueError as e:
            # Handle shlex errors (e.g., unmatched quotes)
            error_msg = str(e).replace("quotation", "quote")
            raise ParseError(
                error_type="QUOTE_MISMATCH",
                message=f"Syntax error in command: {error_msg}",
                suggestions=["Check quote pairing", "Escape special characters"],
            ) from e

        if not tokens:
            raise ParseError(
                error_type="EMPTY_INPUT",
                message="No command found after parsing",
                suggestions=["Enter a valid command"],
            )

        # First token is the command
        command = tokens[0]

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
                        options[key] = value
                else:
                    # Format: --key value (next token is value)
                    key = token[2:]  # Remove --
                    if i + 1 < len(tokens) and not tokens[i + 1].startswith("-"):
                        options[key] = tokens[i + 1]
                        i += 1  # Skip the value token
                    else:
                        # Treat as flag if no value follows
                        flags.add(key)

            elif token.startswith("-") and len(token) > 1:
                # Short flag(s) handling
                flag_chars = token[1:]  # Remove -
                for char in flag_chars:
                    flags.add(char)

            else:
                # Regular argument
                args.append(token)

            i += 1

        return ParseResult(
            command=command, args=args, flags=flags, options=options, raw_input=input
        )

    def get_suggestions(self, partial: str) -> list[str]:
        """Get completion suggestions for partial input.

        Args:
            partial: Partial input to complete

        Returns:
            List of completion suggestions (empty for base implementation)
        """
        # Base implementation returns no suggestions
        # This could be extended to provide command suggestions
        return []


class ShellParser:
    """Parser for shell commands prefixed with '!'.

    Handles commands that should be executed directly in the shell,
    preserving the full command after the '!' prefix.
    """

    def can_parse(self, input: str, session: SessionState) -> bool:
        """Check if input is a shell command.

        Args:
            input: Input string to check
            session: Current session state

        Returns:
            True if input starts with '!' and has content after it
        """
        if not input or not input.strip():
            return False

        stripped = input.strip()

        # Must start with ! and have content after it
        if not stripped.startswith("!"):
            return False

        # Must have content after the !
        shell_content = stripped[1:].strip()
        return len(shell_content) > 0

    def parse(self, input: str, session: SessionState) -> ParseResult:
        """Parse shell command input.

        Args:
            input: Input string starting with '!'
            session: Current session state

        Returns:
            ParseResult with '!' as command and shell command preserved

        Raises:
            ParseError: If input is not a valid shell command
        """
        if not self.can_parse(input, session):
            if not input.strip():
                raise ParseError(
                    error_type="EMPTY_INPUT",
                    message="Empty input cannot be parsed",
                    suggestions=["Enter a shell command prefixed with '!'"],
                )
            elif not input.strip().startswith("!"):
                raise ParseError(
                    error_type="NOT_SHELL_COMMAND",
                    message="Not a shell command (must start with '!')",
                    suggestions=["Use '!' prefix for shell commands"],
                )
            else:
                raise ParseError(
                    error_type="EMPTY_SHELL_COMMAND",
                    message="Shell command prefix found but no command specified",
                    suggestions=["Add a command after the '!' prefix"],
                )

        stripped = input.strip()
        shell_command = stripped[1:].strip()  # Remove ! prefix

        return ParseResult(
            command="!",
            args=[],  # Shell parser doesn't break down the shell command
            flags=set(),
            options={},
            raw_input=input,
            shell_command=shell_command,
        )

    def get_suggestions(self, partial: str) -> list[str]:
        """Get completion suggestions for partial shell input.

        Args:
            partial: Partial input to complete

        Returns:
            List of shell command suggestions
        """
        # Base implementation for shell commands
        if not partial.startswith("!"):
            # For empty or non-shell input, suggest shell prefix
            return ["!ls", "!pwd", "!ps", "!grep", "!find"]

        # Could suggest common shell commands
        shell_partial = partial[1:].strip()
        if not shell_partial:
            return ["!ls", "!pwd", "!ps", "!grep", "!find"]

        common_commands = [
            "ls",
            "pwd",
            "ps",
            "grep",
            "find",
            "cat",
            "less",
            "head",
            "tail",
        ]
        suggestions = []

        for cmd in common_commands:
            if cmd.startswith(shell_partial):
                suggestions.append(f"!{cmd}")

        return suggestions
