"""Tests for parser pipeline implementation."""

from __future__ import annotations

from unittest.mock import Mock

import pytest

from cli_patterns.ui.parser.pipeline import ParserPipeline
from cli_patterns.ui.parser.protocols import Parser
from cli_patterns.ui.parser.types import Context, ParseError, ParseResult


class TestParserPipeline:
    """Test ParserPipeline basic functionality."""

    @pytest.fixture
    def pipeline(self) -> ParserPipeline:
        """Create empty ParserPipeline for testing."""
        return ParserPipeline()

    @pytest.fixture
    def context(self) -> Context:
        """Create basic context for testing."""
        return Context(mode="interactive", history=[], session_state={})

    def test_pipeline_instantiation(self, pipeline: ParserPipeline) -> None:
        """Test that ParserPipeline can be instantiated."""
        assert pipeline is not None
        assert isinstance(pipeline, ParserPipeline)

    def test_empty_pipeline_parsing(
        self, pipeline: ParserPipeline, context: Context
    ) -> None:
        """Test that empty pipeline raises error."""
        with pytest.raises(ParseError) as exc_info:
            pipeline.parse("test input", context)

        error = exc_info.value
        assert error.error_type in ["NO_PARSERS", "PARSE_FAILED"]

    def test_add_parser_basic(self, pipeline: ParserPipeline) -> None:
        """Test adding a parser to pipeline."""
        mock_parser = Mock(spec=Parser)

        def condition(input, context):
            return True

        pipeline.add_parser(mock_parser, condition)

        # Should be able to add without error
        assert len(pipeline._parsers) == 1

    def test_add_multiple_parsers(self, pipeline: ParserPipeline) -> None:
        """Test adding multiple parsers."""
        parser1 = Mock(spec=Parser)
        parser2 = Mock(spec=Parser)
        parser3 = Mock(spec=Parser)

        def condition1(input, context):
            return input.startswith("cmd1")

        def condition2(input, context):
            return input.startswith("cmd2")

        def condition3(input, context):
            return True  # Fallback

        pipeline.add_parser(parser1, condition1)
        pipeline.add_parser(parser2, condition2)
        pipeline.add_parser(parser3, condition3)

        assert len(pipeline._parsers) == 3


class TestParserPipelineRouting:
    """Test parser routing logic."""

    @pytest.fixture
    def pipeline(self) -> ParserPipeline:
        return ParserPipeline()

    @pytest.fixture
    def context(self) -> Context:
        return Context("interactive", [], {})

    def test_parser_selection_by_condition(
        self, pipeline: ParserPipeline, context: Context
    ) -> None:
        """Test that correct parser is selected based on condition."""
        # Create mock parsers
        text_parser = Mock(spec=Parser)
        shell_parser = Mock(spec=Parser)

        # Configure mock behavior
        expected_result = ParseResult("test", [], set(), {}, "test input")
        text_parser.parse.return_value = expected_result

        # Add parsers with conditions
        pipeline.add_parser(shell_parser, lambda input, ctx: input.startswith("!"))
        pipeline.add_parser(text_parser, lambda input, ctx: not input.startswith("!"))

        # Test routing to text parser
        result = pipeline.parse("test input", context)

        # Text parser should have been called
        text_parser.parse.assert_called_once_with("test input", context)
        shell_parser.parse.assert_not_called()
        assert result == expected_result

    def test_parser_selection_shell_command(
        self, pipeline: ParserPipeline, context: Context
    ) -> None:
        """Test routing to shell parser for shell commands."""
        text_parser = Mock(spec=Parser)
        shell_parser = Mock(spec=Parser)

        # Configure shell parser
        expected_result = ParseResult("!", [], set(), {}, "!ls -la")
        expected_result.shell_command = "ls -la"
        shell_parser.parse.return_value = expected_result

        # Add parsers
        pipeline.add_parser(shell_parser, lambda input, ctx: input.startswith("!"))
        pipeline.add_parser(text_parser, lambda input, ctx: not input.startswith("!"))

        # Test routing to shell parser
        result = pipeline.parse("!ls -la", context)

        shell_parser.parse.assert_called_once_with("!ls -la", context)
        text_parser.parse.assert_not_called()
        assert result == expected_result

    def test_first_matching_parser_wins(
        self, pipeline: ParserPipeline, context: Context
    ) -> None:
        """Test that first matching parser is used."""
        parser1 = Mock(spec=Parser)
        parser2 = Mock(spec=Parser)
        parser3 = Mock(spec=Parser)

        # All conditions match
        def condition_all(input, ctx):
            return True

        expected_result = ParseResult("first", [], set(), {}, "test")
        parser1.parse.return_value = expected_result

        # Add parsers (order matters)
        pipeline.add_parser(parser1, condition_all)
        pipeline.add_parser(parser2, condition_all)
        pipeline.add_parser(parser3, condition_all)

        result = pipeline.parse("test", context)

        # Only first parser should be called
        parser1.parse.assert_called_once()
        parser2.parse.assert_not_called()
        parser3.parse.assert_not_called()
        assert result == expected_result

    def test_fallback_to_later_parser(
        self, pipeline: ParserPipeline, context: Context
    ) -> None:
        """Test fallback when first parser condition doesn't match."""
        specific_parser = Mock(spec=Parser)
        fallback_parser = Mock(spec=Parser)

        expected_result = ParseResult("fallback", [], set(), {}, "general command")
        fallback_parser.parse.return_value = expected_result

        # Add specific parser first, then fallback
        pipeline.add_parser(
            specific_parser, lambda input, ctx: input.startswith("specific")
        )
        pipeline.add_parser(fallback_parser, lambda input, ctx: True)

        result = pipeline.parse("general command", context)

        # Should skip specific parser and use fallback
        specific_parser.parse.assert_not_called()
        fallback_parser.parse.assert_called_once_with("general command", context)
        assert result == expected_result

    @pytest.mark.parametrize(
        "input_text,expected_parser_index",
        [
            ("!shell command", 0),  # Shell parser
            ("regular command", 1),  # Text parser
            ("help", 1),  # Text parser
            ("!echo hello", 0),  # Shell parser
        ],
    )
    def test_parametrized_routing(
        self,
        pipeline: ParserPipeline,
        context: Context,
        input_text: str,
        expected_parser_index: int,
    ) -> None:
        """Test routing with various input patterns."""
        shell_parser = Mock(spec=Parser)
        text_parser = Mock(spec=Parser)

        # Configure return values
        shell_result = ParseResult("!", [], set(), {}, input_text)
        text_result = ParseResult("text", [], set(), {}, input_text)

        shell_parser.parse.return_value = shell_result
        text_parser.parse.return_value = text_result

        parsers = [shell_parser, text_parser]
        conditions = [
            lambda input, ctx: input.startswith("!"),
            lambda input, ctx: not input.startswith("!"),
        ]

        # Add parsers
        for parser, condition in zip(parsers, conditions):
            pipeline.add_parser(parser, condition)

        pipeline.parse(input_text, context)

        # Check that correct parser was called
        expected_parser = parsers[expected_parser_index]
        expected_parser.parse.assert_called_once_with(input_text, context)


class TestParserPipelineConditions:
    """Test various condition types and patterns."""

    @pytest.fixture
    def pipeline(self) -> ParserPipeline:
        return ParserPipeline()

    @pytest.fixture
    def context(self) -> Context:
        return Context("interactive", [], {})

    def test_simple_prefix_condition(
        self, pipeline: ParserPipeline, context: Context
    ) -> None:
        """Test simple prefix-based condition."""
        parser = Mock(spec=Parser)
        parser.parse.return_value = ParseResult("test", [], set(), {}, "test input")

        def condition(input, ctx):
            return input.startswith("test")

        pipeline.add_parser(parser, condition)

        # Should match
        pipeline.parse("test input", context)
        parser.parse.assert_called_once()

        # Reset mock and test non-match
        parser.reset_mock()
        with pytest.raises(ParseError):
            pipeline.parse("other input", context)
        parser.parse.assert_not_called()

    def test_regex_based_condition(
        self, pipeline: ParserPipeline, context: Context
    ) -> None:
        """Test regex-based condition."""
        import re

        parser = Mock(spec=Parser)
        parser.parse.return_value = ParseResult("regex", [], set(), {}, "cmd123")

        # Condition matches commands followed by numbers
        def condition(input, ctx):
            return bool(re.match(r"^cmd\d+", input))

        pipeline.add_parser(parser, condition)

        # Should match
        pipeline.parse("cmd123", context)
        parser.parse.assert_called_once()

        # Should not match
        parser.reset_mock()
        with pytest.raises(ParseError):
            pipeline.parse("command", context)

    def test_context_aware_condition(self, pipeline: ParserPipeline) -> None:
        """Test condition that uses context information."""
        parser = Mock(spec=Parser)
        parser.parse.return_value = ParseResult("admin", [], set(), {}, "admin command")

        # Condition checks session state
        def condition(input, ctx):
            return ctx.session_state.get("user_role") == "admin"

        pipeline.add_parser(parser, condition)

        # Test with admin context
        admin_context = Context("interactive", [], {"user_role": "admin"})
        pipeline.parse("admin command", admin_context)
        parser.parse.assert_called_once()

        # Test with regular user context
        parser.reset_mock()
        user_context = Context("interactive", [], {"user_role": "user"})
        with pytest.raises(ParseError):
            pipeline.parse("admin command", user_context)

    def test_mode_based_condition(self, pipeline: ParserPipeline) -> None:
        """Test condition based on context mode."""
        debug_parser = Mock(spec=Parser)
        debug_parser.parse.return_value = ParseResult(
            "debug", [], set(), {}, "debug cmd"
        )

        def condition(input, ctx):
            return ctx.mode == "debug"

        pipeline.add_parser(debug_parser, condition)

        # Should work in debug mode
        debug_context = Context("debug", [], {})
        pipeline.parse("debug cmd", debug_context)
        debug_parser.parse.assert_called_once()

        # Should not work in other modes
        debug_parser.reset_mock()
        normal_context = Context("interactive", [], {})
        with pytest.raises(ParseError):
            pipeline.parse("debug cmd", normal_context)

    def test_complex_compound_condition(
        self, pipeline: ParserPipeline, context: Context
    ) -> None:
        """Test complex compound condition."""
        parser = Mock(spec=Parser)
        parser.parse.return_value = ParseResult("complex", [], set(), {}, "input")

        # Complex condition: starts with 'api' and context has auth token
        def condition(input, ctx):
            return (
                input.startswith("api")
                and "auth_token" in ctx.session_state
                and len(input.split()) > 1
            )

        pipeline.add_parser(parser, condition)

        # Should match
        auth_context = Context("interactive", [], {"auth_token": "abc123"})
        pipeline.parse("api get users", auth_context)
        parser.parse.assert_called_once()

        # Should not match - no auth token
        parser.reset_mock()
        no_auth_context = Context("interactive", [], {})
        with pytest.raises(ParseError):
            pipeline.parse("api get users", no_auth_context)


class TestParserPipelineContextPassing:
    """Test that context is properly passed through pipeline."""

    @pytest.fixture
    def pipeline(self) -> ParserPipeline:
        return ParserPipeline()

    def test_context_passed_to_condition(self, pipeline: ParserPipeline) -> None:
        """Test that context is passed to condition functions."""
        parser = Mock(spec=Parser)
        parser.parse.return_value = ParseResult("test", [], set(), {}, "input")

        # Condition that modifies context (for testing purposes)
        def condition_with_context(input: str, ctx: Context) -> bool:
            # Verify context has expected attributes
            assert hasattr(ctx, "mode")
            assert hasattr(ctx, "history")
            assert hasattr(ctx, "session_state")
            return input == "test"

        pipeline.add_parser(parser, condition_with_context)

        context = Context("test_mode", ["prev"], {"key": "value"})
        pipeline.parse("test", context)

        # Should succeed without assertion errors
        parser.parse.assert_called_once_with("test", context)

    def test_context_passed_to_parser(self, pipeline: ParserPipeline) -> None:
        """Test that original context is passed to parser."""
        parser = Mock(spec=Parser)
        parser.parse.return_value = ParseResult("test", [], set(), {}, "input")

        pipeline.add_parser(parser, lambda input, ctx: True)

        original_context = Context("original", ["cmd1", "cmd2"], {"user": "test"})
        pipeline.parse("test input", original_context)

        # Parser should receive the exact same context
        parser.parse.assert_called_once_with("test input", original_context)

    def test_context_not_modified_by_pipeline(self, pipeline: ParserPipeline) -> None:
        """Test that pipeline doesn't modify the original context."""
        parser = Mock(spec=Parser)
        parser.parse.return_value = ParseResult("test", [], set(), {}, "input")

        pipeline.add_parser(parser, lambda input, ctx: True)

        original_context = Context("mode", ["history"], {"state": "value"})
        original_mode = original_context.mode
        original_history = original_context.history.copy()
        original_state = original_context.session_state.copy()

        pipeline.parse("test", original_context)

        # Context should be unchanged
        assert original_context.mode == original_mode
        assert original_context.history == original_history
        assert original_context.session_state == original_state


class TestParserPipelineErrorHandling:
    """Test error handling in parser pipeline."""

    @pytest.fixture
    def pipeline(self) -> ParserPipeline:
        return ParserPipeline()

    @pytest.fixture
    def context(self) -> Context:
        return Context("interactive", [], {})

    def test_no_matching_parser_error(
        self, pipeline: ParserPipeline, context: Context
    ) -> None:
        """Test error when no parser matches."""
        parser1 = Mock(spec=Parser)
        parser2 = Mock(spec=Parser)

        # Conditions that don't match
        pipeline.add_parser(parser1, lambda input, ctx: input.startswith("special1"))
        pipeline.add_parser(parser2, lambda input, ctx: input.startswith("special2"))

        with pytest.raises(ParseError) as exc_info:
            pipeline.parse("nomatch", context)

        error = exc_info.value
        assert error.error_type in ["NO_MATCHING_PARSER", "PARSE_FAILED"]

    def test_parser_exception_propagation(
        self, pipeline: ParserPipeline, context: Context
    ) -> None:
        """Test that parser exceptions are propagated."""
        parser = Mock(spec=Parser)
        parser.parse.side_effect = ParseError("TEST_ERROR", "Test error message", [])

        pipeline.add_parser(parser, lambda input, ctx: True)

        with pytest.raises(ParseError) as exc_info:
            pipeline.parse("test", context)

        error = exc_info.value
        assert error.error_type == "TEST_ERROR"
        assert error.message == "Test error message"

    def test_condition_exception_handling(
        self, pipeline: ParserPipeline, context: Context
    ) -> None:
        """Test handling of exceptions in condition functions."""
        parser = Mock(spec=Parser)

        def failing_condition(input: str, ctx: Context) -> bool:
            raise ValueError("Condition failed")

        pipeline.add_parser(parser, failing_condition)

        # Should handle condition exceptions gracefully
        with pytest.raises(ParseError):
            pipeline.parse("test", context)

        # Should not call parser if condition fails
        parser.parse.assert_not_called()

    def test_multiple_condition_failures(
        self, pipeline: ParserPipeline, context: Context
    ) -> None:
        """Test handling when multiple conditions fail."""
        parser1 = Mock(spec=Parser)
        parser2 = Mock(spec=Parser)
        parser3 = Mock(spec=Parser)

        # All conditions raise exceptions
        def failing_condition1(input: str, ctx: Context) -> bool:
            raise ValueError("Condition 1 failed")

        def failing_condition2(input: str, ctx: Context) -> bool:
            raise RuntimeError("Condition 2 failed")

        def failing_condition3(input: str, ctx: Context) -> bool:
            return False  # This one just returns False

        pipeline.add_parser(parser1, failing_condition1)
        pipeline.add_parser(parser2, failing_condition2)
        pipeline.add_parser(parser3, failing_condition3)

        with pytest.raises(ParseError):
            pipeline.parse("test", context)

        # No parsers should be called
        parser1.parse.assert_not_called()
        parser2.parse.assert_not_called()
        parser3.parse.assert_not_called()


class TestParserPipelineAdvancedFeatures:
    """Test advanced pipeline features."""

    @pytest.fixture
    def pipeline(self) -> ParserPipeline:
        return ParserPipeline()

    def test_parser_priority_ordering(self, pipeline: ParserPipeline) -> None:
        """Test that parser priority is based on addition order."""
        high_priority = Mock(spec=Parser)
        medium_priority = Mock(spec=Parser)
        low_priority = Mock(spec=Parser)

        high_result = ParseResult("high", [], set(), {}, "test")
        high_priority.parse.return_value = high_result

        # All conditions match, but high priority should win
        def condition_all(input, ctx):
            return True

        # Add in priority order (first = highest priority)
        pipeline.add_parser(high_priority, condition_all)
        pipeline.add_parser(medium_priority, condition_all)
        pipeline.add_parser(low_priority, condition_all)

        context = Context("test", [], {})
        result = pipeline.parse("test", context)

        # Only high priority should be called
        high_priority.parse.assert_called_once()
        medium_priority.parse.assert_not_called()
        low_priority.parse.assert_not_called()
        assert result == high_result

    def test_conditional_parser_chains(self, pipeline: ParserPipeline) -> None:
        """Test complex conditional parser chains."""
        admin_parser = Mock(spec=Parser)
        user_parser = Mock(spec=Parser)
        guest_parser = Mock(spec=Parser)

        admin_result = ParseResult("admin", [], set(), {}, "admin cmd")
        user_result = ParseResult("user", [], set(), {}, "user cmd")
        guest_result = ParseResult("guest", [], set(), {}, "guest cmd")

        admin_parser.parse.return_value = admin_result
        user_parser.parse.return_value = user_result
        guest_parser.parse.return_value = guest_result

        # Add parsers with role-based conditions
        pipeline.add_parser(
            admin_parser, lambda input, ctx: ctx.session_state.get("role") == "admin"
        )
        pipeline.add_parser(
            user_parser, lambda input, ctx: ctx.session_state.get("role") == "user"
        )
        pipeline.add_parser(
            guest_parser,
            lambda input, ctx: ctx.session_state.get("role", "guest") == "guest",
        )

        # Test admin context
        admin_context = Context("interactive", [], {"role": "admin"})
        result = pipeline.parse("admin cmd", admin_context)
        assert result == admin_result

        # Test user context
        user_context = Context("interactive", [], {"role": "user"})
        result = pipeline.parse("user cmd", user_context)
        assert result == user_result

        # Test guest context (no role specified)
        guest_context = Context("interactive", [], {})
        result = pipeline.parse("guest cmd", guest_context)
        assert result == guest_result

    def test_dynamic_parser_selection(self, pipeline: ParserPipeline) -> None:
        """Test dynamic parser selection based on input patterns."""
        json_parser = Mock(spec=Parser)
        xml_parser = Mock(spec=Parser)
        text_parser = Mock(spec=Parser)

        json_result = ParseResult("json", [], set(), {}, '{"key": "value"}')
        xml_result = ParseResult("xml", [], set(), {}, "<root></root>")
        text_result = ParseResult("text", [], set(), {}, "plain text")

        json_parser.parse.return_value = json_result
        xml_parser.parse.return_value = xml_result
        text_parser.parse.return_value = text_result

        # Add parsers with content-based conditions
        pipeline.add_parser(
            json_parser,
            lambda input, ctx: input.strip().startswith("{")
            and input.strip().endswith("}"),
        )
        pipeline.add_parser(
            xml_parser,
            lambda input, ctx: input.strip().startswith("<")
            and input.strip().endswith(">"),
        )
        pipeline.add_parser(
            text_parser, lambda input, ctx: True  # Fallback for plain text
        )

        context = Context("interactive", [], {})

        # Test JSON input
        result = pipeline.parse('{"key": "value"}', context)
        assert result == json_result

        # Test XML input
        result = pipeline.parse("<root></root>", context)
        assert result == xml_result

        # Test plain text input
        result = pipeline.parse("plain text", context)
        assert result == text_result


class TestParserPipelineIntegration:
    """Integration tests for ParserPipeline."""

    def test_real_world_pipeline_setup(self) -> None:
        """Test realistic pipeline setup with multiple parser types."""
        from unittest.mock import create_autospec

        pipeline = ParserPipeline()

        # Create mock parsers that behave like real ones
        shell_parser = create_autospec(Parser)
        text_parser = create_autospec(Parser)
        help_parser = create_autospec(Parser)

        # Configure realistic return values
        shell_result = ParseResult("!", [], set(), {}, "!ls -la")
        shell_result.shell_command = "ls -la"
        text_result = ParseResult("echo", ["hello"], set(), {}, "echo hello")
        help_result = ParseResult("help", [], set(), {}, "help")

        shell_parser.parse.return_value = shell_result
        text_parser.parse.return_value = text_result
        help_parser.parse.return_value = help_result

        # Add parsers in realistic order
        pipeline.add_parser(help_parser, lambda input, ctx: input.strip() == "help")
        pipeline.add_parser(shell_parser, lambda input, ctx: input.startswith("!"))
        pipeline.add_parser(text_parser, lambda input, ctx: True)

        context = Context("interactive", [], {})

        # Test all parser types
        help_result_actual = pipeline.parse("help", context)
        assert help_result_actual == help_result

        shell_result_actual = pipeline.parse("!ls -la", context)
        assert shell_result_actual == shell_result

        text_result_actual = pipeline.parse("echo hello", context)
        assert text_result_actual == text_result

    def test_pipeline_with_error_recovery(self) -> None:
        """Test pipeline behavior with error recovery patterns."""
        pipeline = ParserPipeline()

        # First parser that might fail
        strict_parser = Mock(spec=Parser)
        strict_parser.parse.side_effect = ParseError(
            "STRICT_ERROR", "Strict parsing failed", []
        )

        # Fallback parser that's more lenient
        fallback_parser = Mock(spec=Parser)
        fallback_result = ParseResult("fallback", [], set(), {}, "input")
        fallback_parser.parse.return_value = fallback_result

        # Add parsers
        pipeline.add_parser(strict_parser, lambda input, ctx: len(input) > 5)
        pipeline.add_parser(fallback_parser, lambda input, ctx: True)

        context = Context("interactive", [], {})

        # Long input should try strict parser first, fail, then NOT try fallback
        # (because pipeline stops at first matching condition)
        with pytest.raises(ParseError):
            pipeline.parse("long input text", context)

        # Short input should go directly to fallback
        result = pipeline.parse("short", context)
        assert result == fallback_result
        fallback_parser.parse.assert_called_with("short", context)

    def test_end_to_end_pipeline_workflow(self) -> None:
        """Test complete end-to-end pipeline workflow."""
        pipeline = ParserPipeline()

        # Create realistic parser mocks
        shell_parser = Mock(spec=Parser)
        command_parser = Mock(spec=Parser)

        # Configure parsers
        shell_result = ParseResult("!", [], set(), {}, "!echo test")
        shell_result.shell_command = "echo test"
        command_result = ParseResult("status", [], set(), {}, "status")

        shell_parser.parse.return_value = shell_result
        command_parser.parse.return_value = command_result

        # Add to pipeline
        pipeline.add_parser(shell_parser, lambda input, ctx: input.startswith("!"))
        pipeline.add_parser(
            command_parser, lambda input, ctx: input in ["status", "help", "quit"]
        )

        # Create rich context
        context = Context(
            mode="interactive",
            history=["previous command"],
            session_state={"user": "testuser", "session_id": "12345"},
        )

        # Test shell command
        shell_result_actual = pipeline.parse("!echo test", context)
        assert shell_result_actual.command == "!"
        assert hasattr(shell_result_actual, "shell_command")

        # Test regular command
        command_result_actual = pipeline.parse("status", context)
        assert command_result_actual.command == "status"

        # Test unmatched input
        with pytest.raises(ParseError) as exc_info:
            pipeline.parse("unknown command", context)

        error = exc_info.value
        assert isinstance(error, ParseError)
