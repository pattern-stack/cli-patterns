"""Tests for error display components with design tokens."""

from __future__ import annotations

from unittest.mock import Mock

import pytest
from rich.console import Console
from rich.panel import Panel as RichPanel
from rich.text import Text

from cli_patterns.ui.design.components import ErrorDisplay
from cli_patterns.ui.design.tokens import (
    CategoryToken,
    DisplayMetadata,
    DisplayStyle,
    EmphasisToken,
    HierarchyToken,
    StatusToken,
)


@pytest.fixture
def console() -> Console:
    """Create Rich console for testing."""
    return Console(file=Mock(), width=80, height=24, force_terminal=True)


@pytest.fixture
def error_display() -> ErrorDisplay:
    """Create ErrorDisplay component for testing."""
    return ErrorDisplay()


@pytest.fixture
def display_metadata() -> DisplayMetadata:
    """Create display metadata for testing."""
    return DisplayMetadata(
        category=CategoryToken.CAT_3,
        hierarchy=HierarchyToken.PRIMARY,
        emphasis=EmphasisToken.STRONG,
    )


@pytest.fixture
def display_style() -> DisplayStyle:
    """Create display style for testing."""
    return DisplayStyle(
        category=CategoryToken.CAT_1,
        hierarchy=HierarchyToken.SECONDARY,
        emphasis=EmphasisToken.NORMAL,
        status=StatusToken.ERROR,
    )


class TestErrorDisplayInstantiation:
    """Test ErrorDisplay component instantiation."""

    def test_error_display_creation(self) -> None:
        """Test ErrorDisplay can be created with defaults."""
        display = ErrorDisplay()
        assert display is not None

    def test_error_display_default_tokens(self, error_display: ErrorDisplay) -> None:
        """Test ErrorDisplay has expected default token mappings."""
        assert error_display.border_category == CategoryToken.CAT_1
        assert error_display.title_hierarchy == HierarchyToken.PRIMARY
        assert error_display.title_emphasis == EmphasisToken.STRONG
        assert error_display.content_emphasis == EmphasisToken.NORMAL
        assert error_display.error_status == StatusToken.ERROR
        assert error_display.suggestion_emphasis == EmphasisToken.SUBTLE

    def test_error_display_custom_tokens(self) -> None:
        """Test ErrorDisplay can be customized with different tokens."""
        display = ErrorDisplay(
            border_category=CategoryToken.CAT_5,
            title_hierarchy=HierarchyToken.TERTIARY,
            title_emphasis=EmphasisToken.NORMAL,
            content_emphasis=EmphasisToken.SUBTLE,
            error_status=StatusToken.WARNING,
            suggestion_emphasis=EmphasisToken.STRONG,
        )

        assert display.border_category == CategoryToken.CAT_5
        assert display.title_hierarchy == HierarchyToken.TERTIARY
        assert display.title_emphasis == EmphasisToken.NORMAL
        assert display.content_emphasis == EmphasisToken.SUBTLE
        assert display.error_status == StatusToken.WARNING
        assert display.suggestion_emphasis == EmphasisToken.STRONG


class TestErrorDisplayStyling:
    """Test ErrorDisplay styling methods."""

    def test_create_error_title_style(
        self, error_display: ErrorDisplay, display_metadata: DisplayMetadata
    ) -> None:
        """Test creating error title style from metadata."""
        style = error_display.create_error_title_style(display_metadata)

        assert isinstance(style, DisplayStyle)
        assert style.category == display_metadata.category
        assert style.hierarchy == error_display.title_hierarchy
        assert style.emphasis == error_display.title_emphasis
        assert style.status == error_display.error_status

    def test_create_error_content_style(
        self, error_display: ErrorDisplay, display_metadata: DisplayMetadata
    ) -> None:
        """Test creating error content style from metadata."""
        style = error_display.create_error_content_style(display_metadata)

        assert isinstance(style, DisplayStyle)
        assert style.category == display_metadata.category
        assert style.hierarchy == display_metadata.hierarchy
        assert style.emphasis == error_display.content_emphasis
        assert style.status == error_display.error_status

    def test_create_suggestion_style(
        self, error_display: ErrorDisplay, display_metadata: DisplayMetadata
    ) -> None:
        """Test creating suggestion style from metadata."""
        style = error_display.create_suggestion_style(display_metadata)

        assert isinstance(style, DisplayStyle)
        assert style.category == display_metadata.category
        assert style.hierarchy == display_metadata.hierarchy
        assert style.emphasis == error_display.suggestion_emphasis
        assert style.status == StatusToken.INFO  # Suggestions use info status

    def test_create_border_style(
        self, error_display: ErrorDisplay, display_metadata: DisplayMetadata
    ) -> None:
        """Test creating border style from metadata."""
        style = error_display.create_border_style(display_metadata)

        assert isinstance(style, DisplayStyle)
        assert style.category == error_display.border_category
        assert style.hierarchy == display_metadata.hierarchy
        assert style.emphasis == display_metadata.emphasis
        assert style.status == error_display.error_status

    def test_style_methods_with_none_metadata(
        self, error_display: ErrorDisplay
    ) -> None:
        """Test style methods handle None metadata gracefully."""
        # Should use component defaults when metadata is None
        title_style = error_display.create_error_title_style(None)
        content_style = error_display.create_error_content_style(None)
        suggestion_style = error_display.create_suggestion_style(None)
        border_style = error_display.create_border_style(None)

        # All should return valid display styles using defaults
        assert isinstance(title_style, DisplayStyle)
        assert isinstance(content_style, DisplayStyle)
        assert isinstance(suggestion_style, DisplayStyle)
        assert isinstance(border_style, DisplayStyle)

        # Should use component's default tokens
        assert title_style.hierarchy == error_display.title_hierarchy
        assert content_style.emphasis == error_display.content_emphasis
        assert suggestion_style.emphasis == error_display.suggestion_emphasis
        assert border_style.category == error_display.border_category


class TestErrorDisplayRendering:
    """Test ErrorDisplay rendering methods."""

    def test_render_error_title(
        self, error_display: ErrorDisplay, console: Console
    ) -> None:
        """Test rendering error title with styling."""
        title_text = "SYNTAX_ERROR"
        style = DisplayStyle(
            category=CategoryToken.CAT_1,
            hierarchy=HierarchyToken.PRIMARY,
            emphasis=EmphasisToken.STRONG,
            status=StatusToken.ERROR,
        )

        result = error_display.render_error_title(title_text, style, console)

        assert isinstance(result, Text)
        assert title_text in result.plain

    def test_render_error_message(
        self, error_display: ErrorDisplay, console: Console
    ) -> None:
        """Test rendering error message with styling."""
        message_text = "Invalid command syntax detected"
        style = DisplayStyle(
            category=CategoryToken.CAT_2,
            hierarchy=HierarchyToken.SECONDARY,
            emphasis=EmphasisToken.NORMAL,
            status=StatusToken.ERROR,
        )

        result = error_display.render_error_message(message_text, style, console)

        assert isinstance(result, Text)
        assert message_text in result.plain

    def test_render_suggestions_list(
        self, error_display: ErrorDisplay, console: Console
    ) -> None:
        """Test rendering suggestions list with styling."""
        suggestions = ["help", "status", "version"]
        style = DisplayStyle(
            category=CategoryToken.CAT_3,
            hierarchy=HierarchyToken.TERTIARY,
            emphasis=EmphasisToken.SUBTLE,
            status=StatusToken.INFO,
        )

        result = error_display.render_suggestions_list(suggestions, style, console)

        assert isinstance(result, Text)
        result_str = result.plain
        for suggestion in suggestions:
            assert suggestion in result_str

    def test_render_suggestions_empty_list(
        self, error_display: ErrorDisplay, console: Console
    ) -> None:
        """Test rendering empty suggestions list."""
        suggestions: list[str] = []
        style = DisplayStyle(
            category=CategoryToken.CAT_1,
            hierarchy=HierarchyToken.PRIMARY,
            emphasis=EmphasisToken.NORMAL,
            status=StatusToken.INFO,
        )

        result = error_display.render_suggestions_list(suggestions, style, console)

        # Should return empty Text or None for empty suggestions
        if result is not None:
            assert isinstance(result, Text)
            assert result.plain.strip() == ""

    def test_render_error_panel(
        self, error_display: ErrorDisplay, console: Console
    ) -> None:
        """Test rendering complete error panel."""
        error_data = {
            "title": "COMMAND_NOT_FOUND",
            "message": "Command 'unknow' not found",
            "suggestions": ["unknown", "help"],
        }
        metadata = DisplayMetadata(category=CategoryToken.CAT_2)

        result = error_display.render_error_panel(error_data, metadata, console)

        assert isinstance(result, RichPanel)
        # Panel should contain all error information
        # Note: Exact panel structure depends on implementation


class TestErrorDisplayFormatting:
    """Test ErrorDisplay formatting methods."""

    def test_format_error_data_basic(self, error_display: ErrorDisplay) -> None:
        """Test formatting basic error data."""
        error_type = "VALIDATION_ERROR"
        message = "Invalid input format"
        suggestions = ["Check format", "See documentation"]

        formatted = error_display.format_error_data(error_type, message, suggestions)

        assert isinstance(formatted, dict)
        assert formatted["title"] == error_type
        assert formatted["message"] == message
        assert formatted["suggestions"] == suggestions

    def test_format_error_data_with_none_suggestions(
        self, error_display: ErrorDisplay
    ) -> None:
        """Test formatting error data with None suggestions."""
        error_type = "SIMPLE_ERROR"
        message = "Simple error message"
        suggestions = None

        formatted = error_display.format_error_data(error_type, message, suggestions)

        assert isinstance(formatted, dict)
        assert formatted["title"] == error_type
        assert formatted["message"] == message
        assert formatted["suggestions"] == []  # Should convert None to empty list

    def test_format_multiline_message(self, error_display: ErrorDisplay) -> None:
        """Test formatting multiline error messages."""
        error_type = "COMPLEX_ERROR"
        message = "Line 1 of error\nLine 2 of error\nLine 3 of error"
        suggestions = ["Fix line 1", "Fix line 2"]

        formatted = error_display.format_error_data(error_type, message, suggestions)

        assert isinstance(formatted, dict)
        assert "Line 1 of error" in formatted["message"]
        assert "Line 2 of error" in formatted["message"]
        assert "Line 3 of error" in formatted["message"]

    def test_format_special_characters(self, error_display: ErrorDisplay) -> None:
        """Test formatting error data with special characters."""
        error_type = "UNICODE_ERROR"
        message = "Error with üñíçødé characters and symbols: <>&'\"[]"
        suggestions = ["Check üñíçødé", "Escape symbols: <>&'\"[]"]

        formatted = error_display.format_error_data(error_type, message, suggestions)

        assert isinstance(formatted, dict)
        assert "üñíçødé" in formatted["message"]
        assert "<>&'\"[]" in formatted["message"]
        assert "üñíçødé" in str(formatted["suggestions"])


class TestErrorDisplayTextProcessing:
    """Test ErrorDisplay text processing utilities."""

    def test_truncate_long_text(self, error_display: ErrorDisplay) -> None:
        """Test truncating overly long error text."""
        long_text = "This is a very long error message " * 20
        max_length = 100

        truncated = error_display.truncate_text(long_text, max_length)

        assert len(truncated) <= max_length
        if len(long_text) > max_length:
            assert truncated.endswith("...")  # Should indicate truncation

    def test_truncate_short_text(self, error_display: ErrorDisplay) -> None:
        """Test truncating text shorter than limit."""
        short_text = "Short message"
        max_length = 100

        truncated = error_display.truncate_text(short_text, max_length)

        assert truncated == short_text  # Should remain unchanged

    def test_wrap_text_to_width(self, error_display: ErrorDisplay) -> None:
        """Test wrapping text to specific width."""
        long_line = "This is a very long line that should be wrapped to fit within the specified width limit"
        width = 40

        wrapped = error_display.wrap_text(long_line, width)

        assert isinstance(wrapped, list)
        for line in wrapped:
            assert len(line) <= width

    def test_wrap_text_with_existing_breaks(self, error_display: ErrorDisplay) -> None:
        """Test wrapping text that already has line breaks."""
        text_with_breaks = "Line 1\nLine 2 is longer than usual\nLine 3"
        width = 20

        wrapped = error_display.wrap_text(text_with_breaks, width)

        assert isinstance(wrapped, list)
        assert len(wrapped) >= 3  # At least as many lines as original breaks

    def test_sanitize_text_input(self, error_display: ErrorDisplay) -> None:
        """Test sanitizing text input for safe display."""
        unsafe_text = "Text with\ttabs\nand\rcarriage returns"

        sanitized = error_display.sanitize_text(unsafe_text)

        # Should handle control characters appropriately
        assert isinstance(sanitized, str)
        # Exact sanitization rules depend on implementation


class TestErrorDisplayThemeIntegration:
    """Test ErrorDisplay integration with theme system."""

    def test_apply_theme_to_error_display(
        self, error_display: ErrorDisplay, console: Console
    ) -> None:
        """Test applying theme styling to error display."""
        metadata = DisplayMetadata(
            category=CategoryToken.CAT_1,
            hierarchy=HierarchyToken.PRIMARY,
            emphasis=EmphasisToken.STRONG,
        )

        # Create styles using component methods
        title_style = error_display.create_error_title_style(metadata)
        content_style = error_display.create_error_content_style(metadata)

        # Styles should be properly formed for theme resolution
        assert title_style.status == error_display.error_status
        assert content_style.emphasis == error_display.content_emphasis

    def test_theme_token_resolution(self, error_display: ErrorDisplay) -> None:
        """Test that error display tokens can be resolved through theme system."""
        # This test verifies the tokens are valid for theme resolution
        # Actual resolution would happen in the theme registry

        tokens_to_test = [
            error_display.border_category,
            error_display.title_hierarchy,
            error_display.title_emphasis,
            error_display.content_emphasis,
            error_display.error_status,
            error_display.suggestion_emphasis,
        ]

        for token in tokens_to_test:
            # All tokens should be valid enum instances
            assert hasattr(token, "value")  # Enum characteristic
            assert isinstance(token.value, str)

    def test_display_style_creation_consistency(
        self, error_display: ErrorDisplay
    ) -> None:
        """Test that display style creation is consistent across methods."""
        metadata = DisplayMetadata(category=CategoryToken.CAT_3)

        title_style = error_display.create_error_title_style(metadata)
        content_style = error_display.create_error_content_style(metadata)
        suggestion_style = error_display.create_suggestion_style(metadata)
        border_style = error_display.create_border_style(metadata)

        # All should use the same base category from metadata
        assert title_style.category == metadata.category
        assert content_style.category == metadata.category
        assert suggestion_style.category == metadata.category
        # Border style uses component's border category, not metadata category
        assert border_style.category == error_display.border_category


class TestErrorDisplayEdgeCases:
    """Test ErrorDisplay edge cases and error handling."""

    def test_empty_error_type(self, error_display: ErrorDisplay) -> None:
        """Test handling empty error type."""
        formatted = error_display.format_error_data("", "Test message", [])

        assert formatted["title"] == ""
        assert formatted["message"] == "Test message"

    def test_empty_error_message(self, error_display: ErrorDisplay) -> None:
        """Test handling empty error message."""
        formatted = error_display.format_error_data("TEST_ERROR", "", ["suggestion"])

        assert formatted["title"] == "TEST_ERROR"
        assert formatted["message"] == ""
        assert formatted["suggestions"] == ["suggestion"]

    def test_very_long_suggestions(self, error_display: ErrorDisplay) -> None:
        """Test handling very long suggestion lists."""
        long_suggestions = [f"suggestion_{i}" for i in range(100)]

        formatted = error_display.format_error_data(
            "MANY_SUGGESTIONS", "Error with many suggestions", long_suggestions
        )

        assert len(formatted["suggestions"]) == 100
        assert all(
            suggestion.startswith("suggestion_")
            for suggestion in formatted["suggestions"]
        )

    def test_none_values_handling(self, error_display: ErrorDisplay) -> None:
        """Test handling None values in various contexts."""
        # Test with None message (should be handled gracefully)
        try:
            formatted = error_display.format_error_data("TEST", None, None)
            # If this doesn't raise an exception, verify the result
            assert isinstance(formatted, dict)
        except (TypeError, AttributeError):
            # If it does raise an exception, that's also acceptable behavior
            pass


@pytest.mark.design
@pytest.mark.parser
class TestErrorDisplayMarkers:
    """Test class to verify pytest markers work correctly."""

    def test_markers_applied(self) -> None:
        """Test that pytest markers are properly applied."""
        # This test exists to verify the marker system works
        assert True
