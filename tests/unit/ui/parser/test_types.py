"""Tests for parser types and data structures."""

from __future__ import annotations

from typing import Any

import pytest

from cli_patterns.ui.parser.types import (
    CommandArgs,
    Context,
    ParseError,
    ParseResult,
)

pytestmark = pytest.mark.parser


class TestParseResult:
    """Test ParseResult dataclass."""

    def test_basic_creation(self) -> None:
        """Test basic ParseResult creation."""
        result = ParseResult(
            command="echo",
            args=["hello", "world"],
            flags={"v"},
            options={"output": "file.txt"},
            raw_input="echo -v --output=file.txt hello world",
        )

        assert result.command == "echo"
        assert result.args == ["hello", "world"]
        assert result.flags == {"v"}
        assert result.options == {"output": "file.txt"}
        assert result.raw_input == "echo -v --output=file.txt hello world"

    def test_empty_creation(self) -> None:
        """Test ParseResult with minimal data."""
        result = ParseResult(
            command="help", args=[], flags=set(), options={}, raw_input="help"
        )

        assert result.command == "help"
        assert result.args == []
        assert result.flags == set()
        assert result.options == {}
        assert result.raw_input == "help"

    def test_complex_flags_and_options(self) -> None:
        """Test ParseResult with complex flags and options."""
        result = ParseResult(
            command="git",
            args=["commit"],
            flags={"a", "v", "s"},
            options={
                "message": "Initial commit",
                "author": "John Doe <john@example.com>",
                "date": "2024-01-01",
            },
            raw_input='git commit -avs --message="Initial commit" --author="John Doe <john@example.com>" --date="2024-01-01"',
        )

        assert result.command == "git"
        assert result.args == ["commit"]
        assert result.flags == {"a", "v", "s"}
        assert result.options["message"] == "Initial commit"
        assert result.options["author"] == "John Doe <john@example.com>"
        assert result.options["date"] == "2024-01-01"

    def test_type_validation(self) -> None:
        """Test that ParseResult validates types correctly."""
        # Should work with proper types
        result = ParseResult(
            command="test",
            args=["arg1", "arg2"],
            flags={"f1", "f2"},
            options={"opt": "val"},
            raw_input="test command",
        )

        assert isinstance(result.args, list)
        assert isinstance(result.flags, set)
        assert isinstance(result.options, dict)

    def test_immutability_characteristics(self) -> None:
        """Test that ParseResult behaves as expected for immutability."""
        result = ParseResult(
            command="test",
            args=["arg"],
            flags={"flag"},
            options={"key": "value"},
            raw_input="test",
        )

        # Original values should be accessible
        assert result.command == "test"
        assert "arg" in result.args
        assert "flag" in result.flags
        assert result.options["key"] == "value"

    @pytest.mark.parametrize(
        "command,args,flags,options,raw",
        [
            ("ls", [], set(), {}, "ls"),
            (
                "grep",
                ["pattern", "file.txt"],
                {"i", "n"},
                {},
                "grep -in pattern file.txt",
            ),
            (
                "docker",
                ["run"],
                {"d", "t"},
                {"name": "container", "port": "8080:80"},
                "docker run -dt --name=container --port=8080:80",
            ),
            ("", [], set(), {}, ""),  # Empty command
        ],
    )
    def test_parametrized_creation(
        self,
        command: str,
        args: list[str],
        flags: set[str],
        options: dict[str, str],
        raw: str,
    ) -> None:
        """Test ParseResult creation with various parameter combinations."""
        result = ParseResult(
            command=command, args=args, flags=flags, options=options, raw_input=raw
        )

        assert result.command == command
        assert result.args == args
        assert result.flags == flags
        assert result.options == options
        assert result.raw_input == raw


class TestCommandArgs:
    """Test CommandArgs class for handling positional and named arguments."""

    def test_positional_args_only(self) -> None:
        """Test CommandArgs with only positional arguments."""
        args = CommandArgs(positional=["file1.txt", "file2.txt"])

        assert args.positional == ["file1.txt", "file2.txt"]
        assert args.named == {}
        assert len(args.positional) == 2

    def test_named_args_only(self) -> None:
        """Test CommandArgs with only named arguments."""
        args = CommandArgs(
            positional=[], named={"input": "file.txt", "output": "result.txt"}
        )

        assert args.positional == []
        assert args.named == {"input": "file.txt", "output": "result.txt"}
        assert len(args.named) == 2

    def test_mixed_args(self) -> None:
        """Test CommandArgs with both positional and named arguments."""
        args = CommandArgs(
            positional=["command", "subcommand"],
            named={"verbose": "true", "config": "/path/to/config.yaml"},
        )

        assert args.positional == ["command", "subcommand"]
        assert args.named["verbose"] == "true"
        assert args.named["config"] == "/path/to/config.yaml"

    def test_empty_args(self) -> None:
        """Test CommandArgs with no arguments."""
        args = CommandArgs(positional=[], named={})

        assert args.positional == []
        assert args.named == {}

    def test_access_patterns(self) -> None:
        """Test various ways to access arguments."""
        args = CommandArgs(
            positional=["first", "second", "third"],
            named={"key1": "value1", "key2": "value2"},
        )

        # Positional access
        assert args.positional[0] == "first"
        assert args.positional[-1] == "third"

        # Named access
        assert args.named.get("key1") == "value1"
        assert args.named.get("nonexistent") is None

    def test_argument_types(self) -> None:
        """Test that arguments handle different types correctly."""
        args = CommandArgs(
            positional=["string_arg", "123", "true"],
            named={"string_param": "text", "number_param": "42", "bool_param": "false"},
        )

        # All values should be strings (parsing is separate concern)
        assert isinstance(args.positional[0], str)
        assert isinstance(args.named["number_param"], str)
        assert args.named["number_param"] == "42"

    @pytest.mark.parametrize(
        "positional,named",
        [
            ([], {}),
            (["single"], {}),
            ([], {"single": "value"}),
            (["pos1", "pos2"], {"named1": "val1"}),
            (["a", "b", "c", "d", "e"], {"x": "1", "y": "2", "z": "3"}),
        ],
    )
    def test_parametrized_creation(
        self, positional: list[str], named: dict[str, str]
    ) -> None:
        """Test CommandArgs with various combinations."""
        args = CommandArgs(positional=positional, named=named)

        assert args.positional == positional
        assert args.named == named


class TestParseError:
    """Test ParseError exception class."""

    def test_basic_error(self) -> None:
        """Test basic ParseError creation."""
        error = ParseError(
            error_type="SYNTAX_ERROR",
            message="Invalid command syntax",
            suggestions=["Did you mean 'help'?"],
        )

        assert error.error_type == "SYNTAX_ERROR"
        assert error.message == "Invalid command syntax"
        assert error.suggestions == ["Did you mean 'help'?"]

    def test_error_without_suggestions(self) -> None:
        """Test ParseError without suggestions."""
        error = ParseError(
            error_type="COMMAND_NOT_FOUND",
            message="Command 'unknow' not found",
            suggestions=[],
        )

        assert error.error_type == "COMMAND_NOT_FOUND"
        assert error.message == "Command 'unknow' not found"
        assert error.suggestions == []

    def test_error_inheritance(self) -> None:
        """Test that ParseError is a proper Exception."""
        error = ParseError(
            error_type="TEST_ERROR", message="Test message", suggestions=[]
        )

        assert isinstance(error, Exception)
        # Should be raiseable
        with pytest.raises(ParseError) as exc_info:
            raise error

        raised_error = exc_info.value
        assert raised_error.error_type == "TEST_ERROR"
        assert raised_error.message == "Test message"

    def test_error_with_multiple_suggestions(self) -> None:
        """Test ParseError with multiple suggestions."""
        error = ParseError(
            error_type="AMBIGUOUS_COMMAND",
            message="Ambiguous command 'sta'",
            suggestions=["start", "status", "stage"],
        )

        assert len(error.suggestions) == 3
        assert "start" in error.suggestions
        assert "status" in error.suggestions
        assert "stage" in error.suggestions

    def test_error_str_representation(self) -> None:
        """Test string representation of ParseError."""
        error = ParseError(
            error_type="VALIDATION_ERROR",
            message="Invalid argument format",
            suggestions=["Check the documentation"],
        )

        # Should have meaningful string representation
        error_str = str(error)
        assert "VALIDATION_ERROR" in error_str or "Invalid argument format" in error_str

    @pytest.mark.parametrize(
        "error_type,message,suggestions",
        [
            ("EMPTY_INPUT", "No input provided", []),
            ("QUOTE_MISMATCH", "Unmatched quotes", ["Check quote pairing"]),
            ("INVALID_FLAG", "Unknown flag '-x'", ["Available flags: -h, -v"]),
            ("MISSING_ARGUMENT", "Required argument missing", ["Provide a file path"]),
        ],
    )
    def test_parametrized_errors(
        self, error_type: str, message: str, suggestions: list[str]
    ) -> None:
        """Test ParseError with various error scenarios."""
        error = ParseError(
            error_type=error_type, message=message, suggestions=suggestions
        )

        assert error.error_type == error_type
        assert error.message == message
        assert error.suggestions == suggestions


class TestContext:
    """Test Context class for parser state management."""

    def test_basic_context_creation(self) -> None:
        """Test basic Context creation."""
        context = Context(
            mode="interactive",
            history=["previous command", "another command"],
            session_state={"user": "john", "cwd": "/home/john"},
        )

        assert context.mode == "interactive"
        assert context.history == ["previous command", "another command"]
        assert context.session_state == {"user": "john", "cwd": "/home/john"}

    def test_empty_context(self) -> None:
        """Test Context with minimal data."""
        context = Context(mode="batch", history=[], session_state={})

        assert context.mode == "batch"
        assert context.history == []
        assert context.session_state == {}

    def test_context_with_rich_history(self) -> None:
        """Test Context with extensive command history."""
        history = [
            "git status",
            "git add .",
            "git commit -m 'Initial commit'",
            "git push origin main",
            "ls -la",
        ]

        context = Context(
            mode="interactive",
            history=history,
            session_state={"branch": "main", "repo": "/path/to/repo"},
        )

        assert len(context.history) == 5
        assert context.history[-1] == "ls -la"
        assert context.session_state["branch"] == "main"

    def test_context_with_complex_session_state(self) -> None:
        """Test Context with complex session state."""
        session_state = {
            "user": {
                "name": "John Doe",
                "id": 12345,
                "permissions": ["read", "write", "execute"],
            },
            "environment": {
                "PATH": "/usr/bin:/bin",
                "HOME": "/home/john",
                "SHELL": "/bin/bash",
            },
            "preferences": {"theme": "dark", "verbose": True, "auto_complete": True},
        }

        context = Context(
            mode="advanced", history=["config --list"], session_state=session_state
        )

        assert context.session_state["user"]["name"] == "John Doe"
        assert context.session_state["environment"]["SHELL"] == "/bin/bash"
        assert context.session_state["preferences"]["theme"] == "dark"

    def test_different_modes(self) -> None:
        """Test Context with different operating modes."""
        modes = ["interactive", "batch", "script", "debug", "test"]

        for mode in modes:
            context = Context(
                mode=mode,
                history=[f"command in {mode} mode"],
                session_state={"current_mode": mode},
            )

            assert context.mode == mode
            assert context.session_state["current_mode"] == mode

    def test_history_operations(self) -> None:
        """Test common operations on command history."""
        initial_history = ["cmd1", "cmd2", "cmd3"]
        context = Context(
            mode="interactive",
            history=initial_history.copy(),  # Copy to avoid mutation
            session_state={},
        )

        # History should be accessible
        assert len(context.history) == 3
        assert context.history[0] == "cmd1"
        assert context.history[-1] == "cmd3"

        # Should be able to iterate
        commands = list(context.history)
        assert commands == initial_history

    @pytest.mark.parametrize(
        "mode,history,session",
        [
            ("interactive", [], {}),
            ("batch", ["batch_cmd"], {"batch": True}),
            ("debug", ["debug --verbose", "status"], {"debug_level": 2}),
            ("test", ["run tests", "check results"], {"test_suite": "unit"}),
        ],
    )
    def test_parametrized_contexts(
        self, mode: str, history: list[str], session: dict[str, Any]
    ) -> None:
        """Test Context creation with various parameter combinations."""
        context = Context(mode=mode, history=history, session_state=session)

        assert context.mode == mode
        assert context.history == history
        assert context.session_state == session


class TestTypeIntegration:
    """Integration tests across all parser types."""

    def test_complete_parse_workflow(self) -> None:
        """Test complete workflow using all types together."""
        # Create context
        context = Context(
            mode="interactive",
            history=["previous command"],
            session_state={"user": "test_user"},
        )

        # Create command args
        args = CommandArgs(
            positional=["file.txt"], named={"format": "json", "verbose": "true"}
        )

        # Create parse result
        result = ParseResult(
            command="process",
            args=args.positional,
            flags={"v"},  # verbose flag
            options=args.named,
            raw_input="process -v --format=json --verbose=true file.txt",
        )

        # Verify integration
        assert result.command == "process"
        assert result.args == args.positional
        assert result.options == args.named
        assert context.mode == "interactive"

    def test_error_handling_integration(self) -> None:
        """Test error handling across type system."""
        context = Context(
            mode="strict", history=[], session_state={"strict_mode": True}
        )

        # Test that we can create and raise parse errors
        error = ParseError(
            error_type="INTEGRATION_TEST",
            message="Test error for integration",
            suggestions=["This is a test"],
        )

        with pytest.raises(ParseError) as exc_info:
            raise error

        raised = exc_info.value
        assert raised.error_type == "INTEGRATION_TEST"
        assert context.session_state["strict_mode"] is True

    def test_complex_command_parsing_types(self) -> None:
        """Test types working together for complex commands."""
        # Simulate a complex git command parse result
        result = ParseResult(
            command="git",
            args=["commit"],
            flags={"a", "s", "v"},
            options={
                "message": "feat: add new parser types with full test coverage",
                "author": "Test User <test@example.com>",
            },
            raw_input='git commit -asv --message="feat: add new parser types with full test coverage" --author="Test User <test@example.com>"',
        )

        # Verify complex parsing
        assert result.command == "git"
        assert "commit" in result.args
        assert "a" in result.flags and "s" in result.flags and "v" in result.flags
        assert "message" in result.options
        assert "author" in result.options

        # Create context that might have influenced this parse
        context = Context(
            mode="git_integration",
            history=["git status", "git add ."],
            session_state={"git_repo": True, "current_branch": "feature/parser-types"},
        )

        assert context.session_state["git_repo"] is True
        assert len(context.history) == 2

    def test_type_consistency(self) -> None:
        """Test that all types maintain consistent behavior."""
        # All types should handle empty/minimal cases
        empty_result = ParseResult("", [], set(), {}, "")
        empty_args = CommandArgs([], {})
        empty_context = Context("", [], {})

        assert empty_result.command == ""
        assert empty_args.positional == []
        assert empty_context.mode == ""

        # All should handle their expected types correctly
        assert isinstance(empty_result.flags, set)
        assert isinstance(empty_args.named, dict)
        assert isinstance(empty_context.history, list)
