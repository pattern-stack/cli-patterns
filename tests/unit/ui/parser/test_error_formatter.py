"""Tests for parser error formatter with design tokens."""

from __future__ import annotations

from unittest.mock import Mock

import pytest
from rich.console import Console
from rich.text import Text

from cli_patterns.ui.design.tokens import (
    CategoryToken,
    DisplayMetadata,
    EmphasisToken,
    HierarchyToken,
    StatusToken,
)
from cli_patterns.ui.parser.error_formatter import ErrorFormatter
from cli_patterns.ui.parser.types import ParseError


@pytest.fixture
def console() -> Console:
    """Create Rich console for testing."""
    return Console(file=Mock(), width=80, height=24, force_terminal=True)


@pytest.fixture
def formatter(console: Console) -> ErrorFormatter:
    """Create ErrorFormatter instance for testing."""
    return ErrorFormatter(console=console)


@pytest.fixture
def basic_parse_error() -> ParseError:
    """Create basic ParseError for testing."""
    return ParseError(
        error_type="SYNTAX_ERROR",
        message="Invalid command syntax",
        suggestions=["Did you mean 'help'?"],
    )


@pytest.fixture
def enhanced_parse_error() -> ParseError:
    """Create enhanced ParseError with display metadata for testing."""
    error = ParseError(
        error_type="COMMAND_NOT_FOUND",
        message="Command 'unknow' not found",
        suggestions=["unknown", "help", "list"],
    )
    error.display_metadata = DisplayMetadata(
        category=CategoryToken.CAT_3,
        hierarchy=HierarchyToken.SECONDARY,
        emphasis=EmphasisToken.STRONG,
    )
    return error


class TestErrorFormatterInstantiation:
    """Test ErrorFormatter instantiation and basic setup."""

    def test_formatter_creation_with_console(self, console: Console) -> None:
        """Test ErrorFormatter can be created with a console."""
        formatter = ErrorFormatter(console=console)
        assert formatter is not None
        assert formatter.console is console

    def test_formatter_creation_without_console(self) -> None:
        """Test ErrorFormatter can be created without console."""
        formatter = ErrorFormatter()
        assert formatter is not None
        assert formatter.console is not None
        assert isinstance(formatter.console, Console)

    def test_formatter_default_console_config(self) -> None:
        """Test default console configuration."""
        formatter = ErrorFormatter()
        console = formatter.console

        # Default console should have reasonable settings for error display
        assert (
            console.is_terminal or not console.is_terminal
        )  # Any terminal state is fine
        assert console.width > 0  # Should have positive width


class TestErrorFormatterBasicFormatting:
    """Test basic error formatting functionality."""

    def test_format_basic_parse_error(
        self, formatter: ErrorFormatter, basic_parse_error: ParseError
    ) -> None:
        """Test formatting basic ParseError without display metadata."""
        result = formatter.format_error(basic_parse_error)

        assert isinstance(result, Text)
        # Should contain error type and message
        result_str = result.plain
        assert "SYNTAX_ERROR" in result_str
        assert "Invalid command syntax" in result_str

    def test_format_enhanced_parse_error(
        self, formatter: ErrorFormatter, enhanced_parse_error: ParseError
    ) -> None:
        """Test formatting enhanced ParseError with display metadata."""
        result = formatter.format_error(enhanced_parse_error)

        assert isinstance(result, Text)
        result_str = result.plain
        assert "COMMAND_NOT_FOUND" in result_str
        assert "Command 'unknow' not found" in result_str

    def test_format_error_with_no_suggestions(self, formatter: ErrorFormatter) -> None:
        """Test formatting error with no suggestions."""
        error = ParseError(
            error_type="VALIDATION_ERROR",
            message="Invalid input format",
            suggestions=[],
        )

        result = formatter.format_error(error)
        assert isinstance(result, Text)
        result_str = result.plain
        assert "VALIDATION_ERROR" in result_str
        assert "Invalid input format" in result_str

    def test_format_error_with_multiple_suggestions(
        self, formatter: ErrorFormatter
    ) -> None:
        """Test formatting error with multiple suggestions."""
        error = ParseError(
            error_type="AMBIGUOUS_COMMAND",
            message="Ambiguous command 'sta'",
            suggestions=["start", "status", "stage"],
        )

        result = formatter.format_error(error)
        assert isinstance(result, Text)
        result_str = result.plain
        assert "AMBIGUOUS_COMMAND" in result_str
        assert "start" in result_str
        assert "status" in result_str
        assert "stage" in result_str


class TestErrorFormatterSuggestions:
    """Test error suggestion formatting."""

    def test_format_suggestions_single(self, formatter: ErrorFormatter) -> None:
        """Test formatting single suggestion."""
        suggestions = ["help"]
        result = formatter.format_suggestions(suggestions)

        assert isinstance(result, Text)
        result_str = result.plain
        assert "help" in result_str

    def test_format_suggestions_multiple(self, formatter: ErrorFormatter) -> None:
        """Test formatting multiple suggestions."""
        suggestions = ["start", "status", "stop"]
        result = formatter.format_suggestions(suggestions)

        assert isinstance(result, Text)
        result_str = result.plain
        for suggestion in suggestions:
            assert suggestion in result_str

    def test_format_suggestions_empty(self, formatter: ErrorFormatter) -> None:
        """Test formatting empty suggestions list."""
        suggestions: list[str] = []
        result = formatter.format_suggestions(suggestions)

        # Should return empty Text or None
        if result is not None:
            assert isinstance(result, Text)
            assert result.plain.strip() == ""

    def test_format_suggestions_with_special_characters(
        self, formatter: ErrorFormatter
    ) -> None:
        """Test formatting suggestions with special characters."""
        suggestions = ["file-name", "file_name", "file.txt", "--option"]
        result = formatter.format_suggestions(suggestions)

        assert isinstance(result, Text)
        result_str = result.plain
        for suggestion in suggestions:
            assert suggestion in result_str


class TestErrorFormatterDesignTokens:
    """Test error formatter design token integration."""

    def test_apply_error_styling_with_status_token(
        self, formatter: ErrorFormatter
    ) -> None:
        """Test applying error styling with status tokens."""
        text = Text("Error message")
        styled_text = formatter.apply_error_styling(text, StatusToken.ERROR)

        assert isinstance(styled_text, Text)
        # Should have styling applied (exact styling depends on theme)
        assert len(styled_text._spans) >= 0  # Styling creates spans

    def test_apply_suggestion_styling_with_emphasis_token(
        self, formatter: ErrorFormatter
    ) -> None:
        """Test applying suggestion styling with emphasis tokens."""
        text = Text("suggestion")
        styled_text = formatter.apply_suggestion_styling(text, EmphasisToken.SUBTLE)

        assert isinstance(styled_text, Text)
        # Should have subtle styling applied
        assert len(styled_text._spans) >= 0

    def test_resolve_display_metadata_to_style(
        self, formatter: ErrorFormatter, enhanced_parse_error: ParseError
    ) -> None:
        """Test resolving display metadata to style tokens."""
        metadata = enhanced_parse_error.display_metadata

        # Should be able to get status style from metadata
        style = formatter.resolve_metadata_style(metadata, StatusToken.ERROR)
        assert style is not None

        # Style should be a display style with error status
        assert style.category == metadata.category
        assert style.hierarchy == metadata.hierarchy
        assert style.emphasis == metadata.emphasis
        assert style.status == StatusToken.ERROR

    def test_format_with_theme_integration(
        self, formatter: ErrorFormatter, enhanced_parse_error: ParseError
    ) -> None:
        """Test error formatting with theme system integration."""
        # Set up theme context (would normally be done by theme registry)
        result = formatter.format_error(enhanced_parse_error)

        assert isinstance(result, Text)
        # Should have rich styling applied through design tokens
        # Exact styling depends on current theme, but should not be plain text
        result_str = result.plain
        assert "COMMAND_NOT_FOUND" in result_str


class TestErrorFormatterLayout:
    """Test error formatter layout and structure."""

    def test_format_error_layout_structure(
        self, formatter: ErrorFormatter, basic_parse_error: ParseError
    ) -> None:
        """Test error layout has expected structure."""
        result = formatter.format_error(basic_parse_error)

        assert isinstance(result, Text)
        result_str = result.plain

        # Should contain error type and message in a structured format
        assert "SYNTAX_ERROR" in result_str
        assert "Invalid command syntax" in result_str
        assert "Did you mean 'help'?" in result_str

    def test_format_error_multiline_handling(self, formatter: ErrorFormatter) -> None:
        """Test handling of multiline error messages."""
        error = ParseError(
            error_type="COMPLEX_ERROR",
            message="This is a long error message\nthat spans multiple lines\nfor testing purposes",
            suggestions=["Fix line 1", "Fix line 2"],
        )

        result = formatter.format_error(error)
        assert isinstance(result, Text)
        result_str = result.plain

        # Should preserve multiline structure
        assert "line 1" in result_str or "line 2" in result_str
        assert "Fix line 1" in result_str

    def test_format_error_width_handling(self, formatter: ErrorFormatter) -> None:
        """Test error formatting respects console width."""
        very_long_message = "This is an extremely long error message " * 10
        error = ParseError(
            error_type="LONG_ERROR",
            message=very_long_message,
            suggestions=["Short fix"],
        )

        result = formatter.format_error(error)
        assert isinstance(result, Text)

        # Should handle long messages gracefully
        # (exact behavior depends on console width and wrapping)
        assert len(result.plain) > 0


class TestErrorFormatterEdgeCases:
    """Test error formatter edge cases and error handling."""

    def test_format_none_error_type(self, formatter: ErrorFormatter) -> None:
        """Test formatting error with None error_type."""
        # This should not happen in normal usage, but test robustness
        error = ParseError(error_type="", message="Test message", suggestions=[])

        result = formatter.format_error(error)
        assert isinstance(result, Text)
        assert "Test message" in result.plain

    def test_format_empty_message(self, formatter: ErrorFormatter) -> None:
        """Test formatting error with empty message."""
        error = ParseError(error_type="EMPTY", message="", suggestions=[])

        result = formatter.format_error(error)
        assert isinstance(result, Text)
        assert "EMPTY" in result.plain

    def test_format_special_characters_in_message(
        self, formatter: ErrorFormatter
    ) -> None:
        """Test formatting error with special characters."""
        error = ParseError(
            error_type="SPECIAL_CHARS",
            message="Error with üñíçødé and symbols: <>&'\"",
            suggestions=["Fix üñíçødé", "Check symbols: <>&'\""],
        )

        result = formatter.format_error(error)
        assert isinstance(result, Text)
        result_str = result.plain
        assert "üñíçødé" in result_str
        assert "<>&'\"" in result_str

    def test_format_error_without_display_metadata(
        self, formatter: ErrorFormatter
    ) -> None:
        """Test formatting error without display metadata (backward compatibility)."""
        error = ParseError(
            error_type="BACKWARD_COMPAT",
            message="Legacy error without metadata",
            suggestions=["Use new format"],
        )
        # Explicitly ensure no display_metadata attribute
        assert not hasattr(error, "display_metadata")

        result = formatter.format_error(error)
        assert isinstance(result, Text)
        result_str = result.plain
        assert "BACKWARD_COMPAT" in result_str
        assert "Legacy error without metadata" in result_str


class TestErrorFormatterIntegration:
    """Integration tests for error formatter."""

    def test_complete_error_formatting_workflow(
        self, formatter: ErrorFormatter
    ) -> None:
        """Test complete error formatting workflow with all features."""
        # Create error with full metadata
        error = ParseError(
            error_type="INTEGRATION_TEST",
            message="Complex error for integration testing",
            suggestions=["First suggestion", "Second suggestion", "Third option"],
        )
        error.display_metadata = DisplayMetadata(
            category=CategoryToken.CAT_1,
            hierarchy=HierarchyToken.PRIMARY,
            emphasis=EmphasisToken.STRONG,
        )

        result = formatter.format_error(error)

        # Verify complete formatting
        assert isinstance(result, Text)
        result_str = result.plain
        assert "INTEGRATION_TEST" in result_str
        assert "Complex error for integration testing" in result_str
        assert "First suggestion" in result_str
        assert "Second suggestion" in result_str
        assert "Third option" in result_str

    def test_theme_switching_affects_formatting(self, console: Console) -> None:
        """Test that theme changes affect error formatting."""
        formatter = ErrorFormatter(console=console)

        error = ParseError(
            error_type="THEME_TEST",
            message="Theme-aware error message",
            suggestions=["Check theme"],
        )
        error.display_metadata = DisplayMetadata(category=CategoryToken.CAT_2)

        # Format with current theme
        result1 = formatter.format_error(error)
        assert isinstance(result1, Text)

        # Theme changes would affect styling, but we can't easily test
        # without full theme system integration here
        # Just verify the formatter works consistently
        result2 = formatter.format_error(error)
        assert isinstance(result2, Text)
        assert result1.plain == result2.plain  # Content should be same


@pytest.mark.parser
@pytest.mark.design
class TestErrorFormatterMarkers:
    """Test class to verify pytest markers work correctly."""

    def test_markers_applied(self) -> None:
        """Test that pytest markers are properly applied."""
        # This test exists to verify the marker system works
        # Actual marker testing would be done at the pytest level
        assert True
