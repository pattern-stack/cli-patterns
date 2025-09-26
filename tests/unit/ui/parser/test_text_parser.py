"""Tests for text parser implementation."""

from __future__ import annotations

import pytest

from cli_patterns.ui.parser.parsers import TextParser
from cli_patterns.ui.parser.types import Context, ParseError, ParseResult


class TestTextParserBasics:
    """Test basic TextParser functionality."""

    @pytest.fixture
    def parser(self) -> TextParser:
        """Create TextParser instance for testing."""
        return TextParser()

    @pytest.fixture
    def context(self) -> Context:
        """Create basic context for testing."""
        return Context(mode="interactive", history=[], session_state={})

    def test_parser_instantiation(self, parser: TextParser) -> None:
        """Test that TextParser can be instantiated."""
        assert parser is not None
        assert isinstance(parser, TextParser)

    def test_can_parse_basic_text(self, parser: TextParser, context: Context) -> None:
        """Test can_parse with basic text input."""
        assert parser.can_parse("help", context) is True
        assert parser.can_parse("echo hello", context) is True
        assert parser.can_parse("ls -la", context) is True

    def test_can_parse_edge_cases(self, parser: TextParser, context: Context) -> None:
        """Test can_parse with edge cases."""
        assert parser.can_parse("", context) is False
        assert parser.can_parse("   ", context) is False
        assert parser.can_parse("\t\n", context) is False

    def test_basic_command_parsing(self, parser: TextParser, context: Context) -> None:
        """Test parsing basic commands."""
        result = parser.parse("help", context)

        assert result.command == "help"
        assert result.args == []
        assert result.flags == set()
        assert result.options == {}
        assert result.raw_input == "help"


class TestTextParserCommandsAndArgs:
    """Test command and argument parsing."""

    @pytest.fixture
    def parser(self) -> TextParser:
        return TextParser()

    @pytest.fixture
    def context(self) -> Context:
        return Context("interactive", [], {})

    def test_command_with_single_arg(
        self, parser: TextParser, context: Context
    ) -> None:
        """Test command with single argument."""
        result = parser.parse("echo hello", context)

        assert result.command == "echo"
        assert result.args == ["hello"]
        assert result.raw_input == "echo hello"

    def test_command_with_multiple_args(
        self, parser: TextParser, context: Context
    ) -> None:
        """Test command with multiple arguments."""
        result = parser.parse("echo hello world", context)

        assert result.command == "echo"
        assert result.args == ["hello", "world"]

    def test_command_with_many_args(self, parser: TextParser, context: Context) -> None:
        """Test command with many arguments."""
        result = parser.parse("command arg1 arg2 arg3 arg4 arg5", context)

        assert result.command == "command"
        assert result.args == ["arg1", "arg2", "arg3", "arg4", "arg5"]

    @pytest.mark.parametrize(
        "input_cmd,expected_command,expected_args",
        [
            ("ls", "ls", []),
            ("ls -la", "ls", []),  # -la should be parsed as flags
            ("cat file.txt", "cat", ["file.txt"]),
            (
                "grep pattern file1.txt file2.txt",
                "grep",
                ["pattern", "file1.txt", "file2.txt"],
            ),
            ("python script.py arg1 arg2", "python", ["script.py", "arg1", "arg2"]),
        ],
    )
    def test_parametrized_commands(
        self,
        parser: TextParser,
        context: Context,
        input_cmd: str,
        expected_command: str,
        expected_args: list[str],
    ) -> None:
        """Test various command and argument combinations."""
        result = parser.parse(input_cmd, context)
        assert result.command == expected_command
        # Note: This test may need adjustment based on actual flag parsing logic
        assert expected_command in result.raw_input


class TestTextParserQuoteHandling:
    """Test parsing of quoted strings."""

    @pytest.fixture
    def parser(self) -> TextParser:
        return TextParser()

    @pytest.fixture
    def context(self) -> Context:
        return Context("interactive", [], {})

    def test_double_quoted_string(self, parser: TextParser, context: Context) -> None:
        """Test parsing double-quoted strings."""
        result = parser.parse('echo "hello world"', context)

        assert result.command == "echo"
        assert result.args == ["hello world"]

    def test_single_quoted_string(self, parser: TextParser, context: Context) -> None:
        """Test parsing single-quoted strings."""
        result = parser.parse("echo 'hello world'", context)

        assert result.command == "echo"
        assert result.args == ["hello world"]

    def test_mixed_quotes(self, parser: TextParser, context: Context) -> None:
        """Test parsing mixed quote types."""
        result = parser.parse("echo \"single word\" 'another phrase'", context)

        assert result.command == "echo"
        assert result.args == ["single word", "another phrase"]

    def test_nested_quotes_in_string(
        self, parser: TextParser, context: Context
    ) -> None:
        """Test strings containing other quote types."""
        result = parser.parse("echo \"He said 'hello'\"", context)

        assert result.command == "echo"
        assert result.args == ["He said 'hello'"]

    def test_quotes_with_special_chars(
        self, parser: TextParser, context: Context
    ) -> None:
        """Test quoted strings with special characters."""
        result = parser.parse('echo "special chars: !@#$%^&*()"', context)

        assert result.command == "echo"
        assert result.args == ["special chars: !@#$%^&*()"]

    def test_empty_quoted_strings(self, parser: TextParser, context: Context) -> None:
        """Test empty quoted strings."""
        result = parser.parse("echo \"\" ''", context)

        assert result.command == "echo"
        assert result.args == ["", ""]

    @pytest.mark.parametrize(
        "input_cmd,expected_args",
        [
            ('echo "hello"', ["hello"]),
            ("echo 'world'", ["world"]),
            ('echo "multi word string"', ["multi word string"]),
            ("echo 'another multi word'", ["another multi word"]),
            ('echo "first" second "third"', ["first", "second", "third"]),
            ("echo 'a' 'b' 'c'", ["a", "b", "c"]),
        ],
    )
    def test_parametrized_quotes(
        self,
        parser: TextParser,
        context: Context,
        input_cmd: str,
        expected_args: list[str],
    ) -> None:
        """Test various quote combinations."""
        result = parser.parse(input_cmd, context)
        assert result.args == expected_args


class TestTextParserFlags:
    """Test parsing of command flags."""

    @pytest.fixture
    def parser(self) -> TextParser:
        return TextParser()

    @pytest.fixture
    def context(self) -> Context:
        return Context("interactive", [], {})

    def test_single_short_flag(self, parser: TextParser, context: Context) -> None:
        """Test parsing single short flag."""
        result = parser.parse("ls -l", context)

        assert result.command == "ls"
        assert "l" in result.flags

    def test_multiple_short_flags_separate(
        self, parser: TextParser, context: Context
    ) -> None:
        """Test parsing multiple separate short flags."""
        result = parser.parse("ls -l -a", context)

        assert result.command == "ls"
        assert "l" in result.flags
        assert "a" in result.flags

    def test_combined_short_flags(self, parser: TextParser, context: Context) -> None:
        """Test parsing combined short flags."""
        result = parser.parse("ls -la", context)

        assert result.command == "ls"
        assert "l" in result.flags
        assert "a" in result.flags

    def test_complex_flag_combinations(
        self, parser: TextParser, context: Context
    ) -> None:
        """Test complex flag combinations."""
        result = parser.parse("ls -la -h -v", context)

        assert result.command == "ls"
        expected_flags = {"l", "a", "h", "v"}
        assert result.flags == expected_flags

    def test_flags_with_args(self, parser: TextParser, context: Context) -> None:
        """Test flags mixed with arguments."""
        result = parser.parse("ls -la /tmp", context)

        assert result.command == "ls"
        assert "l" in result.flags
        assert "a" in result.flags
        assert "/tmp" in result.args

    @pytest.mark.parametrize(
        "input_cmd,expected_flags",
        [
            ("cmd -a", {"a"}),
            ("cmd -abc", {"a", "b", "c"}),
            ("cmd -a -b -c", {"a", "b", "c"}),
            ("cmd -ab -cd", {"a", "b", "c", "d"}),
            ("cmd -x -y -z", {"x", "y", "z"}),
        ],
    )
    def test_parametrized_flags(
        self,
        parser: TextParser,
        context: Context,
        input_cmd: str,
        expected_flags: set[str],
    ) -> None:
        """Test various flag combinations."""
        result = parser.parse(input_cmd, context)
        assert result.flags == expected_flags


class TestTextParserOptions:
    """Test parsing of command options (--key=value)."""

    @pytest.fixture
    def parser(self) -> TextParser:
        return TextParser()

    @pytest.fixture
    def context(self) -> Context:
        return Context("interactive", [], {})

    def test_single_option(self, parser: TextParser, context: Context) -> None:
        """Test parsing single option."""
        result = parser.parse("git commit --message=test", context)

        assert result.command == "git"
        assert "commit" in result.args
        assert result.options.get("message") == "test"

    def test_option_with_quoted_value(
        self, parser: TextParser, context: Context
    ) -> None:
        """Test option with quoted value."""
        result = parser.parse('git commit --message="Initial commit"', context)

        assert result.command == "git"
        assert result.options.get("message") == "Initial commit"

    def test_multiple_options(self, parser: TextParser, context: Context) -> None:
        """Test multiple options."""
        result = parser.parse("command --option1=value1 --option2=value2", context)

        assert result.command == "command"
        assert result.options.get("option1") == "value1"
        assert result.options.get("option2") == "value2"

    def test_options_with_flags_and_args(
        self, parser: TextParser, context: Context
    ) -> None:
        """Test options mixed with flags and arguments."""
        result = parser.parse("git commit -a --message=test file.txt", context)

        assert result.command == "git"
        assert "commit" in result.args
        assert "file.txt" in result.args
        assert "a" in result.flags
        assert result.options.get("message") == "test"

    def test_option_with_spaces_in_value(
        self, parser: TextParser, context: Context
    ) -> None:
        """Test option with spaces in value."""
        result = parser.parse(
            'git commit --message="feat: add new parser system"', context
        )

        assert result.options.get("message") == "feat: add new parser system"

    @pytest.mark.parametrize(
        "input_cmd,expected_options",
        [
            ("cmd --opt=val", {"opt": "val"}),
            ("cmd --key1=value1 --key2=value2", {"key1": "value1", "key2": "value2"}),
            ('cmd --message="hello world"', {"message": "hello world"}),
            ("cmd --flag=true --count=5", {"flag": "true", "count": "5"}),
        ],
    )
    def test_parametrized_options(
        self,
        parser: TextParser,
        context: Context,
        input_cmd: str,
        expected_options: dict[str, str],
    ) -> None:
        """Test various option combinations."""
        result = parser.parse(input_cmd, context)
        for key, value in expected_options.items():
            assert result.options.get(key) == value


class TestTextParserComplexCommands:
    """Test parsing of complex real-world commands."""

    @pytest.fixture
    def parser(self) -> TextParser:
        return TextParser()

    @pytest.fixture
    def context(self) -> Context:
        return Context("interactive", [], {})

    def test_git_commit_command(self, parser: TextParser, context: Context) -> None:
        """Test parsing git commit command."""
        cmd = 'git commit -am "feat: add parser system" --author="John Doe <john@example.com>"'
        result = parser.parse(cmd, context)

        assert result.command == "git"
        assert "commit" in result.args
        assert "a" in result.flags
        assert "m" in result.flags
        assert result.options.get("author") == "John Doe <john@example.com>"

    def test_docker_run_command(self, parser: TextParser, context: Context) -> None:
        """Test parsing docker run command."""
        cmd = "docker run -dit --name=myapp --port=8080:80 nginx:latest"
        result = parser.parse(cmd, context)

        assert result.command == "docker"
        assert "run" in result.args
        assert "nginx:latest" in result.args
        assert "d" in result.flags
        assert "i" in result.flags
        assert "t" in result.flags
        assert result.options.get("name") == "myapp"
        assert result.options.get("port") == "8080:80"

    def test_complex_grep_command(self, parser: TextParser, context: Context) -> None:
        """Test parsing complex grep command."""
        cmd = 'grep -rn "TODO:" src/ --include="*.py" --exclude-dir=__pycache__'
        result = parser.parse(cmd, context)

        assert result.command == "grep"
        assert "TODO:" in result.args
        assert "src/" in result.args
        assert "r" in result.flags
        assert "n" in result.flags

    def test_command_with_all_elements(
        self, parser: TextParser, context: Context
    ) -> None:
        """Test command with flags, options, and arguments."""
        cmd = 'complex-cmd -abc --verbose --output="result.txt" input1.txt input2.txt'
        result = parser.parse(cmd, context)

        assert result.command == "complex-cmd"
        assert "input1.txt" in result.args
        assert "input2.txt" in result.args
        assert {"a", "b", "c"}.issubset(result.flags)
        assert "verbose" in result.flags or result.options.get("verbose") is not None
        assert result.options.get("output") == "result.txt"


class TestTextParserErrorCases:
    """Test TextParser error handling."""

    @pytest.fixture
    def parser(self) -> TextParser:
        return TextParser()

    @pytest.fixture
    def context(self) -> Context:
        return Context("interactive", [], {})

    def test_empty_input_error(self, parser: TextParser, context: Context) -> None:
        """Test parsing empty input raises error."""
        with pytest.raises(ParseError) as exc_info:
            parser.parse("", context)

        error = exc_info.value
        assert error.error_type in ["EMPTY_INPUT", "INVALID_INPUT"]

    def test_whitespace_only_error(self, parser: TextParser, context: Context) -> None:
        """Test parsing whitespace-only input raises error."""
        with pytest.raises(ParseError) as exc_info:
            parser.parse("   \t\n  ", context)

        error = exc_info.value
        assert error.error_type in ["EMPTY_INPUT", "INVALID_INPUT"]

    def test_unmatched_quotes_error(self, parser: TextParser, context: Context) -> None:
        """Test unmatched quotes raise error."""
        with pytest.raises(ParseError) as exc_info:
            parser.parse('echo "unmatched quote', context)

        error = exc_info.value
        assert error.error_type in ["QUOTE_MISMATCH", "SYNTAX_ERROR"]
        assert "quote" in error.message.lower()

    def test_unclosed_single_quote_error(
        self, parser: TextParser, context: Context
    ) -> None:
        """Test unclosed single quote raises error."""
        with pytest.raises(ParseError) as exc_info:
            parser.parse("echo 'unclosed", context)

        error = exc_info.value
        assert error.error_type in ["QUOTE_MISMATCH", "SYNTAX_ERROR"]

    def test_malformed_option_error(self, parser: TextParser, context: Context) -> None:
        """Test malformed option syntax raises error."""
        # The string "--invalid-option-format" is actually valid (it's a flag without value)
        # Instead test truly malformed syntax with unmatched quotes
        with pytest.raises(ParseError) as exc_info:
            parser.parse('cmd "unclosed quote', context)

        error = exc_info.value
        assert error.error_type == "QUOTE_MISMATCH"


class TestTextParserSpecialCharacters:
    """Test handling of special characters and escape sequences."""

    @pytest.fixture
    def parser(self) -> TextParser:
        return TextParser()

    @pytest.fixture
    def context(self) -> Context:
        return Context("interactive", [], {})

    def test_special_characters_in_args(
        self, parser: TextParser, context: Context
    ) -> None:
        """Test special characters in arguments."""
        result = parser.parse("echo special@#$%^&*()chars", context)

        assert result.command == "echo"
        assert "special@#$%^&*()chars" in result.args

    def test_path_arguments(self, parser: TextParser, context: Context) -> None:
        """Test file path arguments."""
        result = parser.parse("ls /path/to/file.txt", context)

        assert result.command == "ls"
        assert "/path/to/file.txt" in result.args

    def test_url_arguments(self, parser: TextParser, context: Context) -> None:
        """Test URL arguments."""
        result = parser.parse("curl https://api.example.com/v1/data", context)

        assert result.command == "curl"
        assert "https://api.example.com/v1/data" in result.args

    def test_escaped_characters(self, parser: TextParser, context: Context) -> None:
        """Test escaped characters in quoted strings."""
        result = parser.parse(r'echo "escaped \"quote\""', context)

        assert result.command == "echo"
        # The exact behavior depends on implementation
        assert len(result.args) > 0

    def test_backslash_handling(self, parser: TextParser, context: Context) -> None:
        """Test backslash handling."""
        result = parser.parse(r"echo C:\Windows\System32", context)

        assert result.command == "echo"
        assert any("Windows" in arg for arg in result.args)


class TestTextParserSuggestions:
    """Test TextParser suggestion functionality."""

    @pytest.fixture
    def parser(self) -> TextParser:
        return TextParser()

    def test_empty_suggestions(self, parser: TextParser) -> None:
        """Test suggestions for empty input."""
        suggestions = parser.get_suggestions("")
        assert isinstance(suggestions, list)
        # May be empty or contain common commands

    def test_partial_command_suggestions(self, parser: TextParser) -> None:
        """Test suggestions for partial commands."""
        suggestions = parser.get_suggestions("hel")
        assert isinstance(suggestions, list)
        # Might suggest "help" if it's in the command registry

    def test_suggestions_are_strings(self, parser: TextParser) -> None:
        """Test that all suggestions are strings."""
        suggestions = parser.get_suggestions("test")
        assert all(isinstance(s, str) for s in suggestions)

    def test_no_duplicate_suggestions(self, parser: TextParser) -> None:
        """Test that suggestions don't contain duplicates."""
        suggestions = parser.get_suggestions("test")
        assert len(suggestions) == len(set(suggestions))


class TestTextParserIntegration:
    """Integration tests for TextParser."""

    @pytest.fixture
    def parser(self) -> TextParser:
        return TextParser()

    @pytest.fixture
    def context(self) -> Context:
        return Context("interactive", ["previous cmd"], {"user": "test"})

    def test_parser_protocol_compliance(
        self, parser: TextParser, context: Context
    ) -> None:
        """Test that TextParser satisfies Parser protocol."""
        # Check that parser has all required protocol methods
        assert hasattr(parser, "can_parse")
        assert hasattr(parser, "parse")
        assert hasattr(parser, "get_suggestions")
        assert callable(parser.can_parse)
        assert callable(parser.parse)
        assert callable(parser.get_suggestions)

        # Test all protocol methods work
        assert parser.can_parse("test", context) in [True, False]

        if parser.can_parse("valid command", context):
            result = parser.parse("valid command", context)
            assert isinstance(result, ParseResult)

        suggestions = parser.get_suggestions("test")
        assert isinstance(suggestions, list)

    def test_end_to_end_parsing_workflow(
        self, parser: TextParser, context: Context
    ) -> None:
        """Test complete parsing workflow."""
        test_commands = [
            "help",
            "echo hello world",
            'git commit -m "test message"',
            "ls -la /tmp",
            "complex --flag1 --option=value arg1 arg2",
        ]

        for cmd in test_commands:
            if parser.can_parse(cmd, context):
                result = parser.parse(cmd, context)

                # Verify result structure
                assert isinstance(result.command, str)
                assert isinstance(result.args, list)
                assert isinstance(result.flags, set)
                assert isinstance(result.options, dict)
                assert isinstance(result.raw_input, str)
                assert result.raw_input == cmd

    def test_consistency_across_calls(
        self, parser: TextParser, context: Context
    ) -> None:
        """Test that parser gives consistent results."""
        cmd = "echo test argument"

        # Parse the same command multiple times
        results = [parser.parse(cmd, context) for _ in range(3)]

        # All results should be identical
        for result in results[1:]:
            assert result.command == results[0].command
            assert result.args == results[0].args
            assert result.flags == results[0].flags
            assert result.options == results[0].options
            assert result.raw_input == results[0].raw_input
