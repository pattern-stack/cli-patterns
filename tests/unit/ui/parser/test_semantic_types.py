"""Tests for semantic type usage in parser system.

This module tests how semantic types are used within the parser system,
including ParseResult, Context, and parser implementations that use
semantic types for type safety.
"""

from __future__ import annotations

from unittest.mock import Mock

import pytest

# Import existing parser types
from cli_patterns.ui.parser.types import Context, ParseError, ParseResult

# Import semantic types (these will fail initially)
try:
    from cli_patterns.core.parser_types import (
        ArgumentValue,
        CommandId,
        FlagName,
        make_argument_value,
        make_command_id,
        make_context_key,
        make_flag_name,
        make_option_key,
        make_parse_mode,
    )
    from cli_patterns.ui.parser.semantic_context import SemanticContext
    from cli_patterns.ui.parser.semantic_result import SemanticParseResult
except ImportError:
    # These imports will fail initially since the implementation doesn't exist
    pass

pytestmark = [pytest.mark.unit, pytest.mark.parser]


class TestSemanticParseResult:
    """Test ParseResult with semantic types."""

    def test_semantic_parse_result_creation(self) -> None:
        """
        GIVEN: Semantic types for command data
        WHEN: Creating a SemanticParseResult
        THEN: All semantic types are properly stored
        """
        cmd = make_command_id("git")
        args = [make_argument_value("commit"), make_argument_value("-m")]
        flags = {make_flag_name("verbose"), make_flag_name("all")}
        options = {
            make_option_key("message"): make_argument_value("Initial commit"),
            make_option_key("author"): make_argument_value("John Doe"),
        }

        result = SemanticParseResult(
            command=cmd,
            args=args,
            flags=flags,
            options=options,
            raw_input="git commit -m 'Initial commit' --author='John Doe' -va",
        )

        assert result.command == cmd
        assert result.args == args
        assert result.flags == flags
        assert result.options == options
        assert "git commit" in result.raw_input

    def test_semantic_parse_result_type_safety(self) -> None:
        """
        GIVEN: A SemanticParseResult
        WHEN: Accessing its components
        THEN: Type safety is maintained for all semantic types
        """
        result = SemanticParseResult(
            command=make_command_id("deploy"),
            args=[make_argument_value("production")],
            flags={make_flag_name("force")},
            options={make_option_key("region"): make_argument_value("us-west-2")},
            raw_input="deploy production --region=us-west-2 --force",
        )

        # Command type safety
        command: CommandId = result.command
        assert str(command) == "deploy"

        # Args type safety
        first_arg: ArgumentValue = result.args[0]
        assert str(first_arg) == "production"

        # Flags type safety
        flag_list: list[FlagName] = list(result.flags)
        assert str(flag_list[0]) == "force"

        # Options type safety
        region_key = make_option_key("region")
        region_value: ArgumentValue = result.options[region_key]
        assert str(region_value) == "us-west-2"

    def test_semantic_parse_result_conversion_from_regular(self) -> None:
        """
        GIVEN: A regular ParseResult
        WHEN: Converting to SemanticParseResult
        THEN: All string values are converted to semantic types
        """
        regular_result = ParseResult(
            command="help",
            args=["status", "verbose"],
            flags={"v", "h"},
            options={"format": "json", "output": "file.txt"},
            raw_input="help status verbose -vh --format=json --output=file.txt",
        )

        semantic_result = SemanticParseResult.from_parse_result(regular_result)

        # Check types are converted
        assert isinstance(semantic_result.command, str)  # Runtime check
        assert str(semantic_result.command) == "help"

        assert len(semantic_result.args) == 2
        assert str(semantic_result.args[0]) == "status"
        assert str(semantic_result.args[1]) == "verbose"

        assert len(semantic_result.flags) == 2
        flag_strs = {str(f) for f in semantic_result.flags}
        assert flag_strs == {"v", "h"}

        assert len(semantic_result.options) == 2
        option_items = {str(k): str(v) for k, v in semantic_result.options.items()}
        assert option_items == {"format": "json", "output": "file.txt"}

    def test_semantic_parse_result_method_compatibility(self) -> None:
        """
        GIVEN: A SemanticParseResult
        WHEN: Using utility methods
        THEN: All methods work with semantic types
        """
        result = SemanticParseResult(
            command=make_command_id("test"),
            args=[make_argument_value("arg1"), make_argument_value("arg2")],
            flags={make_flag_name("verbose")},
            options={make_option_key("output"): make_argument_value("file.txt")},
            raw_input="test arg1 arg2 --output=file.txt -v",
        )

        # Check if flag exists
        verbose_flag = make_flag_name("verbose")
        quiet_flag = make_flag_name("quiet")
        assert result.has_flag(verbose_flag)
        assert not result.has_flag(quiet_flag)

        # Get option value
        output_key = make_option_key("output")
        format_key = make_option_key("format")
        assert result.get_option(output_key) == make_argument_value("file.txt")
        assert result.get_option(format_key) is None

        # Get argument by index
        assert result.get_arg(0) == make_argument_value("arg1")
        assert result.get_arg(1) == make_argument_value("arg2")
        assert result.get_arg(2) is None


class TestSemanticContext:
    """Test Context with semantic types."""

    def test_semantic_context_creation(self) -> None:
        """
        GIVEN: Semantic types for context data
        WHEN: Creating a SemanticContext
        THEN: All semantic types are properly stored
        """
        mode = make_parse_mode("interactive")
        session_state = {
            make_context_key("user_id"): "12345",
            make_context_key("session_timeout"): "3600",
            make_context_key("debug_mode"): "true",
        }

        context = SemanticContext(mode=mode, history=[], session_state=session_state)

        assert context.mode == mode
        assert len(context.session_state) == 3

    def test_semantic_context_state_operations(self) -> None:
        """
        GIVEN: A SemanticContext
        WHEN: Performing state operations
        THEN: Semantic types are used for keys and values
        """
        context = SemanticContext(
            mode=make_parse_mode("batch"), history=[], session_state={}
        )

        # Set state with semantic key
        user_key = make_context_key("user_role")
        context.set_state(user_key, "admin")

        # Get state with semantic key
        role = context.get_state(user_key)
        assert role == "admin"

        # Check key exists
        assert context.has_state(user_key)

        # Non-existent key
        missing_key = make_context_key("missing")
        assert not context.has_state(missing_key)
        assert context.get_state(missing_key) is None
        assert context.get_state(missing_key, "default") == "default"

    def test_semantic_context_history_operations(self) -> None:
        """
        GIVEN: A SemanticContext
        WHEN: Working with command history
        THEN: History operations maintain semantic types
        """
        context = SemanticContext(
            mode=make_parse_mode("interactive"), history=[], session_state={}
        )

        # Add commands to history using semantic types
        cmd1 = make_command_id("help")
        cmd2 = make_command_id("status")
        cmd3 = make_command_id("deploy")

        context.add_to_history(cmd1)
        context.add_to_history(cmd2)
        context.add_to_history(cmd3)

        assert len(context.history) == 3
        assert context.history[0] == cmd1
        assert context.history[1] == cmd2
        assert context.history[2] == cmd3

        # Get recent commands
        recent = context.get_recent_commands(2)
        assert len(recent) == 2
        assert recent == [cmd2, cmd3]

    def test_semantic_context_conversion_from_regular(self) -> None:
        """
        GIVEN: A regular Context
        WHEN: Converting to SemanticContext
        THEN: All string values are converted to semantic types
        """
        regular_context = Context(
            mode="interactive",
            history=["help", "status"],
            session_state={"user": "john", "role": "admin"},
        )

        semantic_context = SemanticContext.from_context(regular_context)

        # Check mode conversion
        assert str(semantic_context.mode) == "interactive"

        # Check history conversion
        assert len(semantic_context.history) == 2
        assert str(semantic_context.history[0]) == "help"
        assert str(semantic_context.history[1]) == "status"

        # Check session state conversion
        assert len(semantic_context.session_state) == 2
        state_dict = {str(k): v for k, v in semantic_context.session_state.items()}
        assert "user" in state_dict
        assert "role" in state_dict
        assert state_dict["user"] == "john"
        assert state_dict["role"] == "admin"


class TestSemanticParserProtocol:
    """Test parser protocol implementations with semantic types."""

    def test_semantic_parser_can_parse(self) -> None:
        """
        GIVEN: A parser that works with semantic types
        WHEN: Checking if it can parse input
        THEN: The parser uses semantic context appropriately
        """
        from cli_patterns.ui.parser.semantic_parser import SemanticTextParser

        parser = SemanticTextParser()
        context = SemanticContext(
            mode=make_parse_mode("interactive"), history=[], session_state={}
        )

        # Basic text input
        assert parser.can_parse("help", context)
        assert parser.can_parse("git commit -m 'test'", context)
        assert not parser.can_parse("", context)
        assert not parser.can_parse("   ", context)

    def test_semantic_parser_parse_result(self) -> None:
        """
        GIVEN: A semantic parser
        WHEN: Parsing input
        THEN: The result uses semantic types throughout
        """
        from cli_patterns.ui.parser.semantic_parser import SemanticTextParser

        parser = SemanticTextParser()
        context = SemanticContext(
            mode=make_parse_mode("interactive"), history=[], session_state={}
        )

        result = parser.parse("git commit --message='Initial commit' -v", context)

        # Check result types
        assert isinstance(result, SemanticParseResult)
        assert str(result.command) == "git"
        assert str(result.args[0]) == "commit"

        # Check flags
        verbose_flag = make_flag_name("v")
        assert verbose_flag in result.flags

        # Check options
        message_key = make_option_key("message")
        assert message_key in result.options
        assert str(result.options[message_key]) == "Initial commit"

    def test_semantic_parser_suggestions(self) -> None:
        """
        GIVEN: A semantic parser
        WHEN: Getting suggestions
        THEN: Suggestions use semantic types for commands
        """
        from cli_patterns.ui.parser.semantic_parser import SemanticTextParser

        parser = SemanticTextParser()

        suggestions = parser.get_suggestions("hel")
        assert isinstance(suggestions, list)

        # Suggestions should be CommandIds
        for suggestion in suggestions:
            assert isinstance(suggestion, str)  # Runtime check

    def test_semantic_parser_error_handling(self) -> None:
        """
        GIVEN: A semantic parser
        WHEN: Encountering parsing errors
        THEN: Errors include semantic type information
        """
        from cli_patterns.ui.parser.semantic_parser import SemanticTextParser

        parser = SemanticTextParser()
        context = SemanticContext(
            mode=make_parse_mode("interactive"), history=[], session_state={}
        )

        with pytest.raises(ParseError) as exc_info:
            parser.parse("", context)

        error = exc_info.value
        assert error.error_type in ["EMPTY_INPUT", "INVALID_INPUT"]


class TestSemanticTypeRegistry:
    """Test command registry with semantic types."""

    def test_semantic_command_registry_registration(self) -> None:
        """
        GIVEN: A command registry that uses semantic types
        WHEN: Registering commands
        THEN: Commands are stored with semantic type keys
        """
        from cli_patterns.ui.parser.semantic_registry import SemanticCommandRegistry

        registry = SemanticCommandRegistry()

        # Register commands with semantic types
        help_cmd = make_command_id("help")
        status_cmd = make_command_id("status")
        deploy_cmd = make_command_id("deploy")

        registry.register_command(help_cmd, "Show help information")
        registry.register_command(status_cmd, "Show system status")
        registry.register_command(deploy_cmd, "Deploy application")

        assert registry.is_registered(help_cmd)
        assert registry.is_registered(status_cmd)
        assert registry.is_registered(deploy_cmd)

        unknown_cmd = make_command_id("unknown")
        assert not registry.is_registered(unknown_cmd)

    def test_semantic_command_registry_suggestions(self) -> None:
        """
        GIVEN: A populated semantic command registry
        WHEN: Getting command suggestions
        THEN: Suggestions are returned as semantic types
        """
        from cli_patterns.ui.parser.semantic_registry import SemanticCommandRegistry

        registry = SemanticCommandRegistry()

        # Register commands
        commands = ["help", "helm", "health", "status", "start"]
        for cmd_str in commands:
            cmd = make_command_id(cmd_str)
            registry.register_command(cmd, f"Description for {cmd_str}")

        # Get suggestions for partial match
        suggestions = registry.get_suggestions("hel")
        suggestion_strs = [str(cmd) for cmd in suggestions]

        assert "help" in suggestion_strs
        assert "helm" in suggestion_strs
        assert "health" not in suggestion_strs  # "hel" is not a substring of "health"
        assert "status" not in suggestion_strs
        assert "start" not in suggestion_strs

    def test_semantic_command_registry_metadata(self) -> None:
        """
        GIVEN: A semantic command registry with metadata
        WHEN: Retrieving command information
        THEN: Metadata is properly associated with semantic command types
        """
        from cli_patterns.ui.parser.semantic_registry import SemanticCommandRegistry

        registry = SemanticCommandRegistry()

        git_cmd = make_command_id("git")
        registry.register_command(
            git_cmd,
            description="Version control operations",
            category="tools",
            aliases=[make_command_id("g")],
            options=[
                make_option_key("branch"),
                make_option_key("message"),
                make_option_key("author"),
            ],
            flags=[
                make_flag_name("verbose"),
                make_flag_name("quiet"),
                make_flag_name("all"),
            ],
        )

        metadata = registry.get_command_metadata(git_cmd)
        assert metadata is not None
        assert metadata.description == "Version control operations"
        assert metadata.category == "tools"
        assert len(metadata.aliases) == 1
        assert len(metadata.options) == 3
        assert len(metadata.flags) == 3


class TestSemanticPipelineIntegration:
    """Test parser pipeline with semantic types."""

    def test_semantic_pipeline_routing(self) -> None:
        """
        GIVEN: A parser pipeline with semantic parsers
        WHEN: Routing input to appropriate parser
        THEN: Semantic types are maintained throughout the pipeline
        """
        from cli_patterns.ui.parser.semantic_parser import SemanticTextParser
        from cli_patterns.ui.parser.semantic_pipeline import SemanticParserPipeline

        pipeline = SemanticParserPipeline()
        text_parser = SemanticTextParser()

        # Add parser with semantic condition
        def text_condition(input_str: str, context: SemanticContext) -> bool:
            return not input_str.startswith("!")

        pipeline.add_parser(text_parser, text_condition)

        context = SemanticContext(
            mode=make_parse_mode("interactive"), history=[], session_state={}
        )

        result = pipeline.parse("help status", context)

        assert isinstance(result, SemanticParseResult)
        assert str(result.command) == "help"
        assert len(result.args) >= 1
        assert str(result.args[0]) == "status"

    def test_semantic_pipeline_context_passing(self) -> None:
        """
        GIVEN: A semantic parser pipeline
        WHEN: Processing input with context
        THEN: Semantic context is properly passed through the pipeline
        """
        from cli_patterns.ui.parser.semantic_pipeline import SemanticParserPipeline

        pipeline = SemanticParserPipeline()
        mock_parser = Mock()

        # Configure mock to return semantic result
        semantic_result = SemanticParseResult(
            command=make_command_id("test"),
            args=[],
            flags=set(),
            options={},
            raw_input="test",
        )
        mock_parser.parse.return_value = semantic_result

        def always_match(input_str: str, context: SemanticContext) -> bool:
            # Verify context is semantic
            assert isinstance(context.mode, str)  # Runtime check
            return True

        pipeline.add_parser(mock_parser, always_match)

        context = SemanticContext(
            mode=make_parse_mode("test"),
            history=[make_command_id("prev")],
            session_state={make_context_key("user"): "tester"},
        )

        pipeline.parse("test input", context)

        # Verify parser was called with semantic context
        mock_parser.parse.assert_called_once()
        call_args = mock_parser.parse.call_args
        passed_context = call_args[0][1]  # Second argument is context
        assert isinstance(passed_context, SemanticContext)


class TestSemanticTypeErrorHandling:
    """Test error handling with semantic types."""

    def test_semantic_parse_error_with_command_info(self) -> None:
        """
        GIVEN: A parsing error involving semantic types
        WHEN: Creating a ParseError with semantic information
        THEN: Error includes semantic type context
        """
        from cli_patterns.ui.parser.semantic_errors import SemanticParseError

        cmd = make_command_id("invalid-command")
        error = SemanticParseError(
            error_type="UNKNOWN_COMMAND",
            message=f"Unknown command: {cmd}",
            command=cmd,
            suggestions=[
                make_command_id("help"),
                make_command_id("status"),
            ],
        )

        assert error.command == cmd
        assert len(error.suggestions) == 2
        assert str(error.suggestions[0]) == "help"
        assert str(error.suggestions[1]) == "status"

    def test_semantic_parse_error_with_option_info(self) -> None:
        """
        GIVEN: A parsing error involving option types
        WHEN: Creating an error with option context
        THEN: Error includes semantic option information
        """
        from cli_patterns.ui.parser.semantic_errors import SemanticParseError

        invalid_option = make_option_key("invalid-option")
        error = SemanticParseError(
            error_type="UNKNOWN_OPTION",
            message=f"Unknown option: --{invalid_option}",
            invalid_option=invalid_option,
            valid_options=[
                make_option_key("output"),
                make_option_key("format"),
                make_option_key("verbose"),
            ],
        )

        assert error.invalid_option == invalid_option
        assert len(error.valid_options) == 3
        option_strs = [str(opt) for opt in error.valid_options]
        assert "output" in option_strs
        assert "format" in option_strs
        assert "verbose" in option_strs


class TestSemanticTypePerformance:
    """Test performance characteristics of semantic types."""

    def test_semantic_type_creation_performance(self) -> None:
        """
        GIVEN: Large numbers of semantic type creations
        WHEN: Creating many semantic types
        THEN: Performance is comparable to string operations
        """
        import time

        # Test string creation time
        start_time = time.time()
        [f"command_{i}" for i in range(1000)]
        string_time = time.time() - start_time

        # Test semantic type creation time
        start_time = time.time()
        semantic_commands = [make_command_id(f"command_{i}") for i in range(1000)]
        semantic_time = time.time() - start_time

        # Semantic types should have minimal overhead
        assert semantic_time < string_time * 10  # Allow 10x overhead for test stability
        assert len(semantic_commands) == 1000

    def test_semantic_type_collection_performance(self) -> None:
        """
        GIVEN: Semantic types in large collections
        WHEN: Performing collection operations
        THEN: Performance is comparable to regular string collections
        """
        import time

        # Create test data
        commands = [make_command_id(f"cmd_{i}") for i in range(1000)]
        options = {
            make_option_key(f"opt_{i}"): make_argument_value(f"val_{i}")
            for i in range(1000)
        }

        # Test set operations
        start_time = time.time()
        command_set = set(commands)
        set_time = time.time() - start_time

        # Test dict operations
        start_time = time.time()
        for key, _value in options.items():
            _ = options[key]
        dict_time = time.time() - start_time

        # Operations should complete in reasonable time
        assert set_time < 1.0  # Should be much faster than 1 second
        assert dict_time < 1.0
        assert len(command_set) == 1000
