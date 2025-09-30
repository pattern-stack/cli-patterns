"""Tests for shell parser implementation."""

from __future__ import annotations

import pytest

from cli_patterns.ui.parser.parsers import ShellParser
from cli_patterns.ui.parser.types import Context, ParseError, ParseResult


class TestShellParserBasics:
    """Test basic ShellParser functionality."""

    @pytest.fixture
    def parser(self) -> ShellParser:
        """Create ShellParser instance for testing."""
        return ShellParser()

    @pytest.fixture
    def context(self) -> Context:
        """Create basic context for testing."""
        return Context(mode="interactive", history=[], session_state={})

    def test_parser_instantiation(self, parser: ShellParser) -> None:
        """Test that ShellParser can be instantiated."""
        assert parser is not None
        assert isinstance(parser, ShellParser)

    def test_parser_protocol_compliance(self, parser: ShellParser) -> None:
        """Test that ShellParser implements Parser protocol."""
        # Check that parser has all required protocol methods
        assert hasattr(parser, "can_parse")
        assert hasattr(parser, "parse")
        assert hasattr(parser, "get_suggestions")
        assert callable(parser.can_parse)
        assert callable(parser.parse)
        assert callable(parser.get_suggestions)

    def test_shell_command_detection(
        self, parser: ShellParser, context: Context
    ) -> None:
        """Test that shell commands are properly detected."""
        # Shell commands start with !
        assert parser.can_parse("!ls -la", context) is True
        assert parser.can_parse("!pwd", context) is True
        assert parser.can_parse("!echo hello", context) is True

        # Non-shell commands are rejected
        assert parser.can_parse("ls -la", context) is False
        assert parser.can_parse("regular command", context) is False
        assert parser.can_parse("help", context) is False

    def test_empty_input_handling(self, parser: ShellParser, context: Context) -> None:
        """Test handling of empty or whitespace input."""
        assert parser.can_parse("", context) is False
        assert parser.can_parse("   ", context) is False
        assert parser.can_parse("\t\n", context) is False

    def test_shell_prefix_only(self, parser: ShellParser, context: Context) -> None:
        """Test handling of shell prefix without command."""
        assert parser.can_parse("!", context) is False
        assert parser.can_parse("! ", context) is False
        assert parser.can_parse("!\t", context) is False


class TestShellParserBasicCommands:
    """Test parsing of basic shell commands."""

    @pytest.fixture
    def parser(self) -> ShellParser:
        return ShellParser()

    @pytest.fixture
    def context(self) -> Context:
        return Context("interactive", [], {})

    def test_simple_shell_command(self, parser: ShellParser, context: Context) -> None:
        """Test parsing simple shell command."""
        result = parser.parse("!ls", context)

        assert result.command == "!"
        assert result.shell_command == "ls"
        assert result.raw_input == "!ls"

    def test_shell_command_with_args(
        self, parser: ShellParser, context: Context
    ) -> None:
        """Test shell command with arguments."""
        result = parser.parse("!ls -la /tmp", context)

        assert result.command == "!"
        assert result.shell_command == "ls -la /tmp"
        assert result.raw_input == "!ls -la /tmp"

    def test_shell_command_with_flags(
        self, parser: ShellParser, context: Context
    ) -> None:
        """Test shell command with flags."""
        result = parser.parse("!ps aux", context)

        assert result.command == "!"
        assert result.shell_command == "ps aux"

    def test_complex_shell_command(self, parser: ShellParser, context: Context) -> None:
        """Test complex shell command."""
        result = parser.parse("!find . -name '*.py' -type f", context)

        assert result.command == "!"
        assert result.shell_command == "find . -name '*.py' -type f"

    @pytest.mark.parametrize(
        "shell_cmd,expected_command",
        [
            ("!pwd", "pwd"),
            ("!whoami", "whoami"),
            ("!date", "date"),
            ("!uname -a", "uname -a"),
            ("!echo hello world", "echo hello world"),
        ],
    )
    def test_parametrized_shell_commands(
        self,
        parser: ShellParser,
        context: Context,
        shell_cmd: str,
        expected_command: str,
    ) -> None:
        """Test various shell command patterns."""
        result = parser.parse(shell_cmd, context)
        assert result.command == "!"
        assert result.shell_command == expected_command


class TestShellParserComplexCommands:
    """Test parsing of complex shell commands with pipes and operators."""

    @pytest.fixture
    def parser(self) -> ShellParser:
        return ShellParser()

    @pytest.fixture
    def context(self) -> Context:
        return Context("interactive", [], {})

    def test_piped_command(self, parser: ShellParser, context: Context) -> None:
        """Test shell command with pipes."""
        result = parser.parse("!ps aux | grep python", context)

        assert result.command == "!"
        assert result.shell_command == "ps aux | grep python"
        assert "|" in result.shell_command

    def test_complex_pipe_chain(self, parser: ShellParser, context: Context) -> None:
        """Test complex pipe chain."""
        cmd = "!cat file.txt | grep pattern | sort | uniq -c"
        result = parser.parse(cmd, context)

        assert result.command == "!"
        assert result.shell_command == "cat file.txt | grep pattern | sort | uniq -c"

    def test_command_with_redirection(
        self, parser: ShellParser, context: Context
    ) -> None:
        """Test shell command with output redirection."""
        result = parser.parse("!echo hello > output.txt", context)

        assert result.command == "!"
        assert result.shell_command == "echo hello > output.txt"
        assert ">" in result.shell_command

    def test_command_with_input_redirection(
        self, parser: ShellParser, context: Context
    ) -> None:
        """Test shell command with input redirection."""
        result = parser.parse("!sort < input.txt", context)

        assert result.command == "!"
        assert result.shell_command == "sort < input.txt"
        assert "<" in result.shell_command

    def test_command_with_append_redirection(
        self, parser: ShellParser, context: Context
    ) -> None:
        """Test shell command with append redirection."""
        result = parser.parse("!echo data >> log.txt", context)

        assert result.command == "!"
        assert result.shell_command == "echo data >> log.txt"
        assert ">>" in result.shell_command

    def test_command_with_logical_operators(
        self, parser: ShellParser, context: Context
    ) -> None:
        """Test shell command with logical operators."""
        result = parser.parse("!mkdir test && cd test", context)

        assert result.command == "!"
        assert result.shell_command == "mkdir test && cd test"
        assert "&&" in result.shell_command

    def test_command_with_or_operator(
        self, parser: ShellParser, context: Context
    ) -> None:
        """Test shell command with OR operator."""
        result = parser.parse("!command1 || command2", context)

        assert result.command == "!"
        assert result.shell_command == "command1 || command2"
        assert "||" in result.shell_command

    def test_command_with_semicolon(
        self, parser: ShellParser, context: Context
    ) -> None:
        """Test shell command with semicolon separator."""
        result = parser.parse("!echo first; echo second", context)

        assert result.command == "!"
        assert result.shell_command == "echo first; echo second"
        assert ";" in result.shell_command

    @pytest.mark.parametrize(
        "shell_cmd,expected_operators",
        [
            ("!ps aux | head -10", ["|"]),
            ("!echo hello > file.txt", [">"]),
            ("!cat < input.txt", ["<"]),
            ("!make && make install", ["&&"]),
            ("!test -f file || echo missing", ["||"]),
            ("!cmd1; cmd2; cmd3", [";"]),
            ("!ls -la | grep txt | wc -l", ["|", "|"]),
        ],
    )
    def test_parametrized_operators(
        self,
        parser: ShellParser,
        context: Context,
        shell_cmd: str,
        expected_operators: list,
    ) -> None:
        """Test shell commands with various operators."""
        result = parser.parse(shell_cmd, context)
        assert result.command == "!"

        for operator in expected_operators:
            assert operator in result.shell_command


class TestShellParserQuotesAndSpecialChars:
    """Test handling of quotes and special characters in shell commands."""

    @pytest.fixture
    def parser(self) -> ShellParser:
        return ShellParser()

    @pytest.fixture
    def context(self) -> Context:
        return Context("interactive", [], {})

    def test_single_quotes_preserved(
        self, parser: ShellParser, context: Context
    ) -> None:
        """Test that single quotes are preserved."""
        result = parser.parse("!echo 'hello world'", context)

        assert result.command == "!"
        assert result.shell_command == "echo 'hello world'"
        assert "'" in result.shell_command

    def test_double_quotes_preserved(
        self, parser: ShellParser, context: Context
    ) -> None:
        """Test that double quotes are preserved."""
        result = parser.parse('!echo "hello world"', context)

        assert result.command == "!"
        assert result.shell_command == 'echo "hello world"'
        assert '"' in result.shell_command

    def test_mixed_quotes_preserved(
        self, parser: ShellParser, context: Context
    ) -> None:
        """Test that mixed quotes are preserved."""
        result = parser.parse("!echo \"single: 'quote'\" 'double: \"quote\"'", context)

        assert result.command == "!"
        assert "'" in result.shell_command
        assert '"' in result.shell_command

    def test_escaped_characters_preserved(
        self, parser: ShellParser, context: Context
    ) -> None:
        """Test that escaped characters are preserved."""
        result = parser.parse(r'!echo "escaped \"quote\""', context)

        assert result.command == "!"
        assert "\\" in result.shell_command or "escaped" in result.shell_command

    def test_special_characters_preserved(
        self, parser: ShellParser, context: Context
    ) -> None:
        """Test that special characters are preserved."""
        result = parser.parse("!echo 'special: !@#$%^&*()'", context)

        assert result.command == "!"
        assert "!@#$%^&*()" in result.shell_command

    def test_environment_variables_preserved(
        self, parser: ShellParser, context: Context
    ) -> None:
        """Test that environment variables are preserved."""
        result = parser.parse("!echo $HOME $USER", context)

        assert result.command == "!"
        assert result.shell_command == "echo $HOME $USER"
        assert "$HOME" in result.shell_command
        assert "$USER" in result.shell_command

    def test_glob_patterns_preserved(
        self, parser: ShellParser, context: Context
    ) -> None:
        """Test that glob patterns are preserved."""
        result = parser.parse("!ls *.py", context)

        assert result.command == "!"
        assert result.shell_command == "ls *.py"
        assert "*.py" in result.shell_command

    def test_complex_special_chars(self, parser: ShellParser, context: Context) -> None:
        """Test complex special character combinations."""
        result = parser.parse(
            "!find . -name '*.txt' -exec grep 'pattern' {} \\;", context
        )

        assert result.command == "!"
        assert "*.txt" in result.shell_command
        assert "{}" in result.shell_command


class TestShellParserErrorHandling:
    """Test ShellParser error handling."""

    @pytest.fixture
    def parser(self) -> ShellParser:
        return ShellParser()

    @pytest.fixture
    def context(self) -> Context:
        return Context("interactive", [], {})

    def test_empty_shell_command_error(
        self, parser: ShellParser, context: Context
    ) -> None:
        """Test that empty shell command raises error."""
        with pytest.raises(ParseError) as exc_info:
            parser.parse("!", context)

        error = exc_info.value
        assert error.error_type in ["EMPTY_SHELL_COMMAND", "INVALID_INPUT"]

    def test_whitespace_only_shell_command_error(
        self, parser: ShellParser, context: Context
    ) -> None:
        """Test that whitespace-only shell command raises error."""
        with pytest.raises(ParseError) as exc_info:
            parser.parse("!   ", context)

        error = exc_info.value
        assert error.error_type in ["EMPTY_SHELL_COMMAND", "INVALID_INPUT"]

    def test_non_shell_command_error(
        self, parser: ShellParser, context: Context
    ) -> None:
        """Test that non-shell commands raise error."""
        with pytest.raises(ParseError) as exc_info:
            parser.parse("regular command", context)

        error = exc_info.value
        assert error.error_type in ["NOT_SHELL_COMMAND", "INVALID_INPUT"]

    def test_error_suggestions(self, parser: ShellParser, context: Context) -> None:
        """Test that parse errors include helpful suggestions."""
        try:
            parser.parse("regular command", context)
        except ParseError as error:
            # Should suggest using ! prefix
            assert len(error.suggestions) > 0
            assert any("!" in suggestion for suggestion in error.suggestions)


class TestShellParserContextAwareness:
    """Test ShellParser context awareness."""

    @pytest.fixture
    def parser(self) -> ShellParser:
        return ShellParser()

    def test_different_modes(self, parser: ShellParser) -> None:
        """Test parser behavior in different modes."""
        interactive_context = Context("interactive", [], {})
        batch_context = Context("batch", [], {})
        debug_context = Context("debug", [], {})

        # Should work in all modes
        assert parser.can_parse("!ls", interactive_context) is True
        assert parser.can_parse("!ls", batch_context) is True
        assert parser.can_parse("!ls", debug_context) is True

    def test_history_awareness(self, parser: ShellParser) -> None:
        """Test that parser can access command history."""
        context_with_history = Context(
            mode="interactive",
            history=["!previous command", "another command"],
            session_state={},
        )

        # Parser should still work with history present
        assert parser.can_parse("!ls", context_with_history) is True
        result = parser.parse("!ls", context_with_history)
        assert result.command == "!"

    def test_session_state_awareness(self, parser: ShellParser) -> None:
        """Test that parser can access session state."""
        context_with_state = Context(
            mode="interactive",
            history=[],
            session_state={"shell": "bash", "cwd": "/tmp"},
        )

        # Parser should still work with session state
        assert parser.can_parse("!pwd", context_with_state) is True
        result = parser.parse("!pwd", context_with_state)
        assert result.command == "!"


class TestShellParserSuggestions:
    """Test ShellParser suggestion functionality."""

    @pytest.fixture
    def parser(self) -> ShellParser:
        return ShellParser()

    def test_empty_input_suggestions(self, parser: ShellParser) -> None:
        """Test suggestions for empty input."""
        suggestions = parser.get_suggestions("")
        assert isinstance(suggestions, list)
        # Should suggest shell prefix
        assert any("!" in suggestion for suggestion in suggestions)

    def test_partial_shell_prefix_suggestions(self, parser: ShellParser) -> None:
        """Test suggestions for partial shell prefix."""
        suggestions = parser.get_suggestions("!")
        assert isinstance(suggestions, list)
        # Should suggest common shell commands
        # At least some common commands should be suggested
        assert len(suggestions) > 0

    def test_partial_command_suggestions(self, parser: ShellParser) -> None:
        """Test suggestions for partial commands."""
        suggestions = parser.get_suggestions("!l")
        assert isinstance(suggestions, list)
        # Should suggest commands starting with 'l'
        assert any("ls" in suggestion for suggestion in suggestions)

    def test_suggestions_are_strings(self, parser: ShellParser) -> None:
        """Test that all suggestions are strings."""
        suggestions = parser.get_suggestions("!test")
        assert all(isinstance(s, str) for s in suggestions)

    def test_suggestions_unique(self, parser: ShellParser) -> None:
        """Test that suggestions don't contain duplicates."""
        suggestions = parser.get_suggestions("!c")
        assert len(suggestions) == len(set(suggestions))

    def test_suggestions_for_common_patterns(self, parser: ShellParser) -> None:
        """Test suggestions for common shell patterns."""
        test_patterns = ["!ps", "!grep", "!find", "!ls", "!cat"]

        for pattern in test_patterns:
            suggestions = parser.get_suggestions(pattern)
            assert isinstance(suggestions, list)
            # Should have reasonable suggestions or be empty


class TestShellParserRealWorldScenarios:
    """Test ShellParser with real-world shell command scenarios."""

    @pytest.fixture
    def parser(self) -> ShellParser:
        return ShellParser()

    @pytest.fixture
    def context(self) -> Context:
        return Context("interactive", [], {})

    def test_git_shell_commands(self, parser: ShellParser, context: Context) -> None:
        """Test git commands executed through shell."""
        commands = [
            "!git status",
            "!git log --oneline",
            "!git diff HEAD~1",
            "!git add .",
            "!git commit -m 'test commit'",
        ]

        for cmd in commands:
            assert parser.can_parse(cmd, context)
            result = parser.parse(cmd, context)
            assert result.command == "!"
            assert "git" in result.shell_command

    def test_system_monitoring_commands(
        self, parser: ShellParser, context: Context
    ) -> None:
        """Test system monitoring shell commands."""
        commands = [
            "!top -n 1",
            "!htop",
            "!ps aux | grep python",
            "!df -h",
            "!free -m",
            "!netstat -tulpn",
        ]

        for cmd in commands:
            assert parser.can_parse(cmd, context)
            result = parser.parse(cmd, context)
            assert result.command == "!"
            assert result.shell_command == cmd[1:]  # Without the ! prefix

    def test_file_operations_commands(
        self, parser: ShellParser, context: Context
    ) -> None:
        """Test file operation shell commands."""
        commands = [
            "!ls -la | grep '.py'",
            "!find . -name '*.txt'",
            "!tar -czf archive.tar.gz *.py",
            "!chmod +x script.sh",
            "!cp file1.txt file2.txt",
            "!mv old_name.txt new_name.txt",
        ]

        for cmd in commands:
            assert parser.can_parse(cmd, context)
            result = parser.parse(cmd, context)
            assert result.command == "!"

    def test_docker_commands(self, parser: ShellParser, context: Context) -> None:
        """Test Docker commands through shell."""
        commands = [
            "!docker ps",
            "!docker images",
            "!docker run -d nginx",
            "!docker exec -it container_name bash",
            "!docker-compose up -d",
        ]

        for cmd in commands:
            assert parser.can_parse(cmd, context)
            result = parser.parse(cmd, context)
            assert result.command == "!"
            assert "docker" in result.shell_command.lower()


class TestShellParserIntegration:
    """Integration tests for ShellParser."""

    @pytest.fixture
    def parser(self) -> ShellParser:
        return ShellParser()

    @pytest.fixture
    def rich_context(self) -> Context:
        return Context(
            mode="interactive",
            history=["!previous shell command", "regular command"],
            session_state={
                "shell": "bash",
                "user": "testuser",
                "cwd": "/home/testuser",
            },
        )

    def test_complete_workflow(
        self, parser: ShellParser, rich_context: Context
    ) -> None:
        """Test complete shell parsing workflow."""
        test_command = "!ps aux | grep python | wc -l"

        # Check if can parse
        can_parse = parser.can_parse(test_command, rich_context)
        assert can_parse is True

        # Parse command
        result = parser.parse(test_command, rich_context)
        assert result.command == "!"
        assert result.shell_command == "ps aux | grep python | wc -l"
        assert result.raw_input == test_command

        # Get suggestions
        suggestions = parser.get_suggestions("!ps")
        assert isinstance(suggestions, list)

    def test_edge_case_handling(
        self, parser: ShellParser, rich_context: Context
    ) -> None:
        """Test handling of edge cases."""
        edge_cases = [
            ("!  command  ", "command"),  # Extra whitespace
            ("!!!", "!!"),  # Multiple exclamations
            ("! echo 'hello world'", "echo 'hello world'"),  # Space after !
        ]

        for input_cmd, _expected_shell_cmd in edge_cases:
            if parser.can_parse(input_cmd, rich_context):
                result = parser.parse(input_cmd, rich_context)
                assert result.command == "!"
                # Shell command should be cleaned up appropriately

    def test_consistency_across_contexts(self, parser: ShellParser) -> None:
        """Test that parser behaves consistently across different contexts."""
        contexts = [
            Context("interactive", [], {}),
            Context("batch", ["prev"], {"mode": "batch"}),
            Context("debug", [], {"debug": True}),
        ]

        test_command = "!echo test"

        results = []
        for context in contexts:
            if parser.can_parse(test_command, context):
                result = parser.parse(test_command, context)
                results.append(result)

        # All results should have same basic structure
        if results:
            first_result = results[0]
            for result in results[1:]:
                assert result.command == first_result.command
                assert result.shell_command == first_result.shell_command
                assert result.raw_input == first_result.raw_input

    def test_protocol_compliance_integration(
        self, parser: ShellParser, rich_context: Context
    ) -> None:
        """Test complete protocol compliance in integration context."""
        # Check that parser has all required protocol methods
        assert hasattr(parser, "can_parse")
        assert hasattr(parser, "parse")
        assert hasattr(parser, "get_suggestions")
        assert callable(parser.can_parse)
        assert callable(parser.parse)
        assert callable(parser.get_suggestions)

        # All methods should work together
        test_input = "!ls -la"

        # can_parse should return boolean
        can_parse_result = parser.can_parse(test_input, rich_context)
        assert isinstance(can_parse_result, bool)

        # If can parse, then parse should work
        if can_parse_result:
            parse_result = parser.parse(test_input, rich_context)
            assert isinstance(parse_result, ParseResult)
            assert parse_result.raw_input == test_input

        # get_suggestions should always return list
        suggestions = parser.get_suggestions("!l")
        assert isinstance(suggestions, list)
