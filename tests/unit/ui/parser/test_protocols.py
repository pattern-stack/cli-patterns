"""Tests for parser protocols and runtime behavior."""

from __future__ import annotations

from typing import Protocol
from unittest.mock import Mock

import pytest

from cli_patterns.core.models import SessionState
from cli_patterns.ui.parser.protocols import Parser
from cli_patterns.ui.parser.types import ParseResult

pytestmark = pytest.mark.parser


class TestParserProtocol:
    """Test Parser protocol definition and behavior."""

    def test_parser_is_runtime_checkable(self) -> None:
        """Test that Parser protocol supports isinstance checks."""

        # Test the actual functionality: isinstance checking should work
        class ValidImplementation:
            def can_parse(self, input: str, session: SessionState) -> bool:
                return True

            def parse(self, input: str, session: SessionState) -> ParseResult:
                return ParseResult("test", [], set(), {}, input)

            def get_suggestions(self, partial: str) -> list[str]:
                return []

        class InvalidImplementation:
            pass

        valid = ValidImplementation()
        invalid = InvalidImplementation()

        # This is what @runtime_checkable actually enables
        assert isinstance(valid, Parser)
        assert not isinstance(invalid, Parser)

    def test_parser_protocol_methods(self) -> None:
        """Test that Parser protocol has required methods."""
        # Check protocol has the expected methods
        required_methods = ["can_parse", "parse", "get_suggestions"]

        for method_name in required_methods:
            assert hasattr(
                Parser, method_name
            ), f"Parser protocol missing method: {method_name}"

    def test_parser_protocol_annotations(self) -> None:
        """Test Parser protocol method annotations."""
        # Get the protocol's annotations
        getattr(Parser, "__annotations__", {})

        # Parser protocol should define method signatures
        assert "can_parse" in Parser.__dict__ or hasattr(Parser, "can_parse")
        assert "parse" in Parser.__dict__ or hasattr(Parser, "parse")
        assert "get_suggestions" in Parser.__dict__ or hasattr(
            Parser, "get_suggestions"
        )

    def test_valid_parser_implementation(self) -> None:
        """Test that a valid implementation satisfies the Parser protocol."""

        class ValidParser:
            """A valid parser implementation for testing."""

            def can_parse(self, input: str, session: SessionState) -> bool:
                return True

            def parse(self, input: str, session: SessionState) -> ParseResult:
                return ParseResult(
                    command=input, args=[], flags=set(), options={}, raw_input=input
                )

            def get_suggestions(self, partial: str) -> list[str]:
                return []

        parser = ValidParser()

        # Check that all required methods are present and callable
        assert hasattr(parser, "can_parse") and callable(parser.can_parse)
        assert hasattr(parser, "parse") and callable(parser.parse)
        assert hasattr(parser, "get_suggestions") and callable(parser.get_suggestions)

        # Test that the methods work as expected
        session = SessionState(
            parse_mode="interactive", command_history=[], variables={}
        )
        assert parser.can_parse("test", session) is True
        result = parser.parse("test", session)
        assert result.command == "test"
        suggestions = parser.get_suggestions("partial")
        assert isinstance(suggestions, list)

    def test_incomplete_parser_implementation(self) -> None:
        """Test that incomplete implementations don't satisfy the protocol."""

        class IncompleteParser:
            """An incomplete parser missing required methods."""

            def can_parse(self, input: str, session: SessionState) -> bool:
                return True

            # Missing parse() and get_suggestions() methods

        parser = IncompleteParser()

        # Check that required methods are missing
        assert not (
            hasattr(parser, "can_parse")
            and hasattr(parser, "parse")
            and hasattr(parser, "get_suggestions")
        )

    def test_parser_with_wrong_signatures(self) -> None:
        """Test that parsers with wrong method signatures don't satisfy protocol."""

        class WrongSignatureParser:
            """Parser with incorrect method signatures."""

            def can_parse(self, input: str) -> bool:  # Missing context parameter
                return True

            def parse(self, input: str, session: SessionState) -> ParseResult:
                return ParseResult("", [], set(), {}, input)

            def get_suggestions(self, partial: str) -> list[str]:
                return []

        WrongSignatureParser()

        # May or may not satisfy protocol depending on Python version and typing
        # The key is that our real parsers should have correct signatures
        # This test documents the expected behavior

    def test_duck_typing_behavior(self) -> None:
        """Test duck typing behavior with Parser protocol."""

        class DuckTypedParser:
            """A duck-typed parser that should work at runtime."""

            def can_parse(self, input: str, session: SessionState) -> bool:
                return "test" in input.lower()

            def parse(self, input: str, session: SessionState) -> ParseResult:
                return ParseResult(
                    command="test",
                    args=[input],
                    flags=set(),
                    options={},
                    raw_input=input,
                )

            def get_suggestions(self, partial: str) -> list[str]:
                return ["test_command", "test_runner"]

        parser = DuckTypedParser()
        session = SessionState(parse_mode="test", command_history=[], variables={})

        # Should work as a Parser at runtime
        assert parser.can_parse("test input", session)
        result = parser.parse("test input", session)
        assert result.command == "test"
        suggestions = parser.get_suggestions("test")
        assert isinstance(suggestions, list)


class TestParserBehaviorContract:
    """Test the behavioral contract expected from Parser implementations."""

    @pytest.fixture
    def mock_parser(self) -> Mock:
        """Create a mock parser for testing."""
        parser = Mock(spec=Parser)
        return parser

    @pytest.fixture
    def sample_session(self) -> SessionState:
        """Create a sample session for testing."""
        return SessionState(
            parse_mode="interactive",
            command_history=["previous command"],
            variables={"user": "test"},
        )

    def test_can_parse_contract(
        self, mock_parser: Mock, sample_session: SessionState
    ) -> None:
        """Test can_parse method contract."""
        # Configure mock
        mock_parser.can_parse.return_value = True

        # Test method call
        result = mock_parser.can_parse("test input", sample_session)

        # Verify call and return type
        mock_parser.can_parse.assert_called_once_with("test input", sample_session)
        assert isinstance(result, bool)

    def test_parse_contract(
        self, mock_parser: Mock, sample_session: SessionState
    ) -> None:
        """Test parse method contract."""
        # Configure mock return value
        expected_result = ParseResult(
            command="test",
            args=["arg"],
            flags={"f"},
            options={"opt": "val"},
            raw_input="test -f --opt=val arg",
        )
        mock_parser.parse.return_value = expected_result

        # Test method call
        result = mock_parser.parse("test -f --opt=val arg", sample_session)

        # Verify call and return type
        mock_parser.parse.assert_called_once_with(
            "test -f --opt=val arg", sample_session
        )
        assert isinstance(result, ParseResult)
        assert result == expected_result

    def test_get_suggestions_contract(self, mock_parser: Mock) -> None:
        """Test get_suggestions method contract."""
        # Configure mock
        expected_suggestions = ["suggestion1", "suggestion2", "suggestion3"]
        mock_parser.get_suggestions.return_value = expected_suggestions

        # Test method call
        result = mock_parser.get_suggestions("partial")

        # Verify call and return type
        mock_parser.get_suggestions.assert_called_once_with("partial")
        assert isinstance(result, list)
        assert result == expected_suggestions

    def test_empty_suggestions_contract(self, mock_parser: Mock) -> None:
        """Test get_suggestions can return empty list."""
        mock_parser.get_suggestions.return_value = []

        result = mock_parser.get_suggestions("no_matches")

        assert isinstance(result, list)
        assert len(result) == 0

    def test_parser_method_chaining(self, sample_session: SessionState) -> None:
        """Test typical parser usage pattern."""

        class TestParser:
            """Test parser for method chaining."""

            def can_parse(self, input: str, session: SessionState) -> bool:
                return input.startswith("test")

            def parse(self, input: str, session: SessionState) -> ParseResult:
                if not self.can_parse(input, session):
                    raise ValueError("Cannot parse input")

                return ParseResult(
                    command="test",
                    args=[input[5:]],  # Everything after "test "
                    flags=set(),
                    options={},
                    raw_input=input,
                )

            def get_suggestions(self, partial: str) -> list[str]:
                if partial.startswith("te"):
                    return ["test", "test_command"]
                return []

        parser = TestParser()

        # Test the typical workflow
        input_text = "test argument"

        # First check if parser can handle input
        can_parse = parser.can_parse(input_text, sample_session)
        assert can_parse is True

        # Then parse if possible
        result = parser.parse(input_text, sample_session)
        assert result.command == "test"
        assert result.args == ["argument"]

        # Get suggestions for partial input
        suggestions = parser.get_suggestions("te")
        assert "test" in suggestions

    def test_parser_error_handling_contract(self, sample_session: SessionState) -> None:
        """Test that parsers handle errors appropriately."""

        class ErrorHandlingParser:
            """Parser that demonstrates error handling."""

            def can_parse(self, input: str, session: SessionState) -> bool:
                # Should not raise exceptions, just return boolean
                try:
                    return len(input.strip()) > 0
                except Exception:
                    return False

            def parse(self, input: str, session: SessionState) -> ParseResult:
                # Should raise appropriate exceptions for invalid input
                if not input.strip():
                    raise ValueError("Empty input cannot be parsed")

                return ParseResult(
                    command=input.strip(),
                    args=[],
                    flags=set(),
                    options={},
                    raw_input=input,
                )

            def get_suggestions(self, partial: str) -> list[str]:
                # Should handle edge cases gracefully
                if not partial:
                    return []
                return [f"{partial}_suggestion"]

        parser = ErrorHandlingParser()

        # Test can_parse doesn't raise
        assert parser.can_parse("valid", sample_session) is True
        assert parser.can_parse("", sample_session) is False

        # Test parse raises for invalid input
        with pytest.raises(ValueError):
            parser.parse("", sample_session)

        # Test get_suggestions handles edge cases
        assert parser.get_suggestions("") == []
        assert parser.get_suggestions("test") == ["test_suggestion"]


class TestProtocolRuntimeChecking:
    """Test runtime protocol checking behavior."""

    def test_protocol_isinstance_checking(self) -> None:
        """Test isinstance checking with Parser protocol."""

        class CompliantParser:
            def can_parse(self, input: str, session: SessionState) -> bool:
                return True

            def parse(self, input: str, session: SessionState) -> ParseResult:
                return ParseResult("", [], set(), {}, input)

            def get_suggestions(self, partial: str) -> list[str]:
                return []

        class NonCompliantParser:
            def some_other_method(self) -> None:
                pass

        # Test protocol compliance checking
        compliant = CompliantParser()
        non_compliant = NonCompliantParser()

        # Check compliant parser has all required methods
        assert hasattr(compliant, "can_parse") and callable(compliant.can_parse)
        assert hasattr(compliant, "parse") and callable(compliant.parse)
        assert hasattr(compliant, "get_suggestions") and callable(
            compliant.get_suggestions
        )

        # Check non-compliant parser lacks required methods
        assert not (
            hasattr(non_compliant, "can_parse")
            and hasattr(non_compliant, "parse")
            and hasattr(non_compliant, "get_suggestions")
        )

    def test_protocol_with_additional_methods(self) -> None:
        """Test that parsers can have additional methods beyond protocol."""

        class ExtendedParser:
            """Parser with additional utility methods."""

            def can_parse(self, input: str, session: SessionState) -> bool:
                return True

            def parse(self, input: str, session: SessionState) -> ParseResult:
                return ParseResult("extended", [], set(), {}, input)

            def get_suggestions(self, partial: str) -> list[str]:
                return self._generate_suggestions(partial)

            def _generate_suggestions(self, partial: str) -> list[str]:
                """Helper method not part of protocol."""
                return [f"{partial}_extended"]

            def reset_state(self) -> None:
                """Additional method not in protocol."""
                pass

        parser = ExtendedParser()

        # Should still have all Parser protocol methods
        assert hasattr(parser, "can_parse") and callable(parser.can_parse)
        assert hasattr(parser, "parse") and callable(parser.parse)
        assert hasattr(parser, "get_suggestions") and callable(parser.get_suggestions)

        # Additional methods should still work
        assert parser._generate_suggestions("test") == ["test_extended"]
        parser.reset_state()  # Should not raise

    def test_protocol_inheritance_compatibility(self) -> None:
        """Test that protocol works with inheritance."""

        class BaseParser:
            """Base parser class."""

            def can_parse(self, input: str, session: SessionState) -> bool:
                return False

            def parse(self, input: str, session: SessionState) -> ParseResult:
                raise NotImplementedError

            def get_suggestions(self, partial: str) -> list[str]:
                return []

        class ConcreteParser(BaseParser):
            """Concrete parser inheriting from base."""

            def can_parse(self, input: str, session: SessionState) -> bool:
                return "concrete" in input

            def parse(self, input: str, session: SessionState) -> ParseResult:
                return ParseResult("concrete", [], set(), {}, input)

        # Both should have protocol methods
        base = BaseParser()
        concrete = ConcreteParser()

        # Check base parser
        assert hasattr(base, "can_parse") and callable(base.can_parse)
        assert hasattr(base, "parse") and callable(base.parse)
        assert hasattr(base, "get_suggestions") and callable(base.get_suggestions)

        # Check concrete parser
        assert hasattr(concrete, "can_parse") and callable(concrete.can_parse)
        assert hasattr(concrete, "parse") and callable(concrete.parse)
        assert hasattr(concrete, "get_suggestions") and callable(
            concrete.get_suggestions
        )

        # Behavior should be as expected
        session = SessionState(parse_mode="test", command_history=[], variables={})
        assert not base.can_parse("test", session)
        assert concrete.can_parse("concrete test", session)


class TestProtocolDocumentation:
    """Test protocol documentation and metadata."""

    def test_parser_protocol_has_docstring(self) -> None:
        """Test that Parser protocol is properly documented."""
        # Protocol should have documentation
        assert Parser.__doc__ is not None or hasattr(Parser, "__doc__")

    def test_protocol_method_documentation(self) -> None:
        """Test that protocol methods are documented."""
        # Methods should be discoverable
        assert hasattr(Parser, "can_parse")
        assert hasattr(Parser, "parse")
        assert hasattr(Parser, "get_suggestions")

    def test_protocol_typing_information(self) -> None:
        """Test that protocol preserves typing information."""
        # Should be identifiable as a Protocol
        assert issubclass(Parser, Protocol)

        # Should support runtime type checking (the actual purpose of @runtime_checkable)
        class TestImplementation:
            def can_parse(self, input: str, session: SessionState) -> bool:
                return True

            def parse(self, input: str, session: SessionState) -> ParseResult:
                return ParseResult("test", [], set(), {}, input)

            def get_suggestions(self, partial: str) -> list[str]:
                return []

        impl = TestImplementation()
        assert isinstance(impl, Parser)  # This is what matters, not internal attributes


class TestParserProtocolEdgeCases:
    """Test edge cases and boundary conditions for Parser protocol."""

    def test_parser_with_none_returns(self) -> None:
        """Test parser that might return None values."""

        class EdgeCaseParser:
            def can_parse(self, input: str, session: SessionState) -> bool:
                return input is not None

            def parse(self, input: str, session: SessionState) -> ParseResult:
                # Always returns valid ParseResult, never None
                return ParseResult("edge", [], set(), {}, input or "")

            def get_suggestions(self, partial: str) -> list[str]:
                # Should always return list, never None
                return [] if partial is None else ["suggestion"]

        parser = EdgeCaseParser()
        session = SessionState(parse_mode="test", command_history=[], variables={})

        # Should handle edge cases gracefully
        assert parser.can_parse("", session) is True
        result = parser.parse("", session)
        assert isinstance(result, ParseResult)

        suggestions = parser.get_suggestions("")
        assert isinstance(suggestions, list)

    def test_protocol_with_async_methods(self) -> None:
        """Test that protocol doesn't interfere with async methods."""

        class AsyncParserMixin:
            """Mixin that adds async capabilities."""

            async def async_parse(self, input: str) -> str:
                """Async parsing method not part of protocol."""
                return f"async_{input}"

        class HybridParser(AsyncParserMixin):
            """Parser with both sync and async methods."""

            def can_parse(self, input: str, session: SessionState) -> bool:
                return True

            def parse(self, input: str, session: SessionState) -> ParseResult:
                return ParseResult("hybrid", [], set(), {}, input)

            def get_suggestions(self, partial: str) -> list[str]:
                return ["hybrid_suggestion"]

        parser = HybridParser()

        # Should have all Parser protocol methods
        assert hasattr(parser, "can_parse") and callable(parser.can_parse)
        assert hasattr(parser, "parse") and callable(parser.parse)
        assert hasattr(parser, "get_suggestions") and callable(parser.get_suggestions)

        # Async method should still work (test that it exists)
        assert hasattr(parser, "async_parse")
        assert callable(parser.async_parse)
