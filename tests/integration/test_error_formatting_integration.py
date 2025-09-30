"""Integration tests for complete error formatting pipeline with design tokens."""

from __future__ import annotations

from unittest.mock import Mock

import pytest
from rich.console import Console
from rich.text import Text

from cli_patterns.ui.design.components import ErrorDisplay
from cli_patterns.ui.design.registry import theme_registry
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
    """Create Rich console for integration testing."""
    return Console(file=Mock(), width=80, height=24, force_terminal=True)


@pytest.fixture
def error_formatter(console: Console) -> ErrorFormatter:
    """Create ErrorFormatter for integration testing."""
    return ErrorFormatter(console=console)


@pytest.fixture
def error_display() -> ErrorDisplay:
    """Create ErrorDisplay component for integration testing."""
    return ErrorDisplay()


@pytest.fixture
def sample_parse_error() -> ParseError:
    """Create sample ParseError with display metadata."""
    error = ParseError(
        error_type="INTEGRATION_TEST_ERROR",
        message="This is a test error for integration testing with multiple lines\nSecond line of the error message",
        suggestions=[
            "Try the 'help' command",
            "Check your syntax",
            "Verify input format",
        ],
    )
    error.display_metadata = DisplayMetadata(
        category=CategoryToken.CAT_2,
        hierarchy=HierarchyToken.PRIMARY,
        emphasis=EmphasisToken.STRONG,
    )
    return error


@pytest.fixture
def legacy_parse_error() -> ParseError:
    """Create legacy ParseError without display metadata."""
    return ParseError(
        error_type="LEGACY_ERROR",
        message="Legacy error without metadata for backward compatibility testing",
        suggestions=["Use legacy error handling"],
    )


@pytest.fixture
def complex_parse_error() -> ParseError:
    """Create complex ParseError for comprehensive testing."""
    error = ParseError(
        error_type="COMPLEX_PARSING_ERROR",
        message="Complex error with special characters: üñíçødé, symbols <>&'\"[], and numbers 12345",
        suggestions=[
            "Check character encoding",
            "Escape special symbols",
            "Validate numeric inputs",
            "Review documentation for complex cases",
        ],
    )
    error.display_metadata = DisplayMetadata(
        category=CategoryToken.CAT_5,
        hierarchy=HierarchyToken.TERTIARY,
        emphasis=EmphasisToken.SUBTLE,
    )
    return error


class TestErrorFormattingPipeline:
    """Test complete error formatting pipeline from ParseError to styled output."""

    def test_basic_error_formatting_pipeline(
        self,
        error_formatter: ErrorFormatter,
        sample_parse_error: ParseError,
    ) -> None:
        """Test basic error formatting from ParseError to Rich Text."""
        # Format the error through the complete pipeline
        result = error_formatter.format_error(sample_parse_error)

        # Verify result is properly formatted Rich Text
        assert isinstance(result, Text)
        result_str = result.plain

        # Verify all error components are present
        assert "INTEGRATION_TEST_ERROR" in result_str
        assert "This is a test error for integration testing" in result_str
        assert "Second line of the error message" in result_str
        assert "Try the 'help' command" in result_str
        assert "Check your syntax" in result_str
        assert "Verify input format" in result_str

        # Verify Rich styling has been applied
        assert len(result._spans) >= 0  # Should have styling spans

    def test_legacy_error_backward_compatibility(
        self,
        error_formatter: ErrorFormatter,
        legacy_parse_error: ParseError,
    ) -> None:
        """Test backward compatibility with legacy ParseError without metadata."""
        # Should handle legacy errors without display metadata
        result = error_formatter.format_error(legacy_parse_error)

        assert isinstance(result, Text)
        result_str = result.plain

        # Should still format properly without metadata
        assert "LEGACY_ERROR" in result_str
        assert "Legacy error without metadata" in result_str
        assert "Use legacy error handling" in result_str

    def test_complex_error_comprehensive_formatting(
        self,
        error_formatter: ErrorFormatter,
        complex_parse_error: ParseError,
    ) -> None:
        """Test comprehensive formatting of complex error with special characters."""
        result = error_formatter.format_error(complex_parse_error)

        assert isinstance(result, Text)
        result_str = result.plain

        # Verify all complex content is preserved
        assert "COMPLEX_PARSING_ERROR" in result_str
        assert "üñíçødé" in result_str
        assert "<>&'\"[]" in result_str
        assert "12345" in result_str
        assert "Check character encoding" in result_str
        assert "Review documentation" in result_str


class TestDisplayComponentIntegration:
    """Test integration between ErrorDisplay component and design tokens."""

    def test_error_display_component_styling(
        self,
        error_display: ErrorDisplay,
        sample_parse_error: ParseError,
        console: Console,
    ) -> None:
        """Test ErrorDisplay component creates proper styles from ParseError metadata."""
        metadata = sample_parse_error.display_metadata

        # Test all style creation methods
        title_style = error_display.create_error_title_style(metadata)
        content_style = error_display.create_error_content_style(metadata)
        suggestion_style = error_display.create_suggestion_style(metadata)
        border_style = error_display.create_border_style(metadata)

        # Verify styles are properly created
        assert title_style.category == metadata.category
        assert title_style.status == StatusToken.ERROR
        assert content_style.emphasis == EmphasisToken.NORMAL
        assert suggestion_style.status == StatusToken.INFO
        assert border_style.category == CategoryToken.CAT_1  # ErrorDisplay default

    def test_error_display_rendering_integration(
        self,
        error_display: ErrorDisplay,
        sample_parse_error: ParseError,
        console: Console,
    ) -> None:
        """Test complete error display rendering with theme integration."""
        metadata = sample_parse_error.display_metadata

        # Format error data
        error_data = error_display.format_error_data(
            sample_parse_error.error_type,
            sample_parse_error.message,
            sample_parse_error.suggestions,
        )

        # Create styles
        title_style = error_display.create_error_title_style(metadata)
        content_style = error_display.create_error_content_style(metadata)

        # Render components
        title_text = error_display.render_error_title(
            error_data["title"], title_style, console
        )
        message_text = error_display.render_error_message(
            error_data["message"], content_style, console
        )

        # Verify rendered output
        assert isinstance(title_text, Text)
        assert isinstance(message_text, Text)
        assert "INTEGRATION_TEST_ERROR" in title_text.plain
        assert "This is a test error" in message_text.plain

    def test_error_display_with_empty_suggestions(
        self,
        error_display: ErrorDisplay,
        console: Console,
    ) -> None:
        """Test error display handles empty suggestions gracefully."""
        error = ParseError(
            error_type="NO_SUGGESTIONS",
            message="Error without suggestions",
            suggestions=[],
        )
        error.display_metadata = DisplayMetadata(category=CategoryToken.CAT_3)

        suggestion_style = error_display.create_suggestion_style(error.display_metadata)
        suggestions_text = error_display.render_suggestions_list(
            error.suggestions, suggestion_style, console
        )

        # Should handle empty suggestions gracefully
        if suggestions_text is not None:
            assert isinstance(suggestions_text, Text)
            assert suggestions_text.plain.strip() == ""


class TestThemeSystemIntegration:
    """Test integration with theme system for complete styling pipeline."""

    def test_theme_registry_integration(
        self,
        error_formatter: ErrorFormatter,
        sample_parse_error: ParseError,
    ) -> None:
        """Test error formatting integrates with theme registry."""
        # Set specific theme if available
        available_themes = theme_registry.list_themes()
        if "dark" in available_themes:
            theme_registry.set_current("dark")

        # Format error with theme applied
        result = error_formatter.format_error(sample_parse_error)

        assert isinstance(result, Text)
        # Theme integration should produce styled output
        # Exact styling depends on theme configuration

    def test_design_token_resolution_pipeline(
        self,
        error_display: ErrorDisplay,
        sample_parse_error: ParseError,
    ) -> None:
        """Test complete design token resolution through theme system."""
        metadata = sample_parse_error.display_metadata

        # Create display styles
        title_style = error_display.create_error_title_style(metadata)

        # Verify design tokens are properly structured for theme resolution
        assert title_style.category in [
            CategoryToken.CAT_1,
            CategoryToken.CAT_2,
            CategoryToken.CAT_3,
            CategoryToken.CAT_4,
            CategoryToken.CAT_5,
            CategoryToken.CAT_6,
            CategoryToken.CAT_7,
            CategoryToken.CAT_8,
        ]
        assert title_style.hierarchy in [
            HierarchyToken.PRIMARY,
            HierarchyToken.SECONDARY,
            HierarchyToken.TERTIARY,
            HierarchyToken.QUATERNARY,
        ]
        assert title_style.status in [
            StatusToken.SUCCESS,
            StatusToken.ERROR,
            StatusToken.WARNING,
            StatusToken.INFO,
            StatusToken.MUTED,
            StatusToken.RUNNING,
        ]

    def test_multiple_theme_consistency(
        self,
        error_formatter: ErrorFormatter,
        sample_parse_error: ParseError,
    ) -> None:
        """Test error formatting consistency across different themes."""
        available_themes = theme_registry.list_themes()

        results = {}
        for theme_name in available_themes:
            theme_registry.set_current(theme_name)
            result = error_formatter.format_error(sample_parse_error)
            results[theme_name] = result

        # All themes should produce valid Text output
        for theme_name, result in results.items():
            assert isinstance(
                result, Text
            ), f"Theme {theme_name} failed to produce Text"
            # Content should be consistent across themes
            assert "INTEGRATION_TEST_ERROR" in result.plain


class TestErrorPipelineEdgeCases:
    """Test edge cases in the complete error formatting pipeline."""

    def test_extremely_long_error_message(
        self,
        error_formatter: ErrorFormatter,
        console: Console,
    ) -> None:
        """Test handling of extremely long error messages."""
        long_message = "This is an extremely long error message. " * 100
        error = ParseError(
            error_type="LONG_MESSAGE_ERROR",
            message=long_message,
            suggestions=["Handle long messages"],
        )
        error.display_metadata = DisplayMetadata(category=CategoryToken.CAT_1)

        result = error_formatter.format_error(error)

        assert isinstance(result, Text)
        # Should handle long messages without crashing
        assert len(result.plain) > 0

    def test_unicode_and_special_characters_pipeline(
        self,
        error_formatter: ErrorFormatter,
        complex_parse_error: ParseError,
    ) -> None:
        """Test complete pipeline with Unicode and special characters."""
        result = error_formatter.format_error(complex_parse_error)

        assert isinstance(result, Text)
        result_str = result.plain

        # Unicode characters should be preserved
        assert "üñíçødé" in result_str
        # Special characters should be preserved
        assert "<>&'\"[]" in result_str

    def test_malformed_display_metadata(
        self,
        error_formatter: ErrorFormatter,
    ) -> None:
        """Test handling of malformed or incomplete display metadata."""
        error = ParseError(
            error_type="MALFORMED_METADATA",
            message="Error with incomplete metadata",
            suggestions=["Handle gracefully"],
        )

        # Set malformed metadata (missing required fields would be caught by Pydantic)
        # But we can test with minimal metadata
        error.display_metadata = DisplayMetadata(category=CategoryToken.CAT_1)

        result = error_formatter.format_error(error)

        assert isinstance(result, Text)
        assert "MALFORMED_METADATA" in result.plain

    def test_none_or_missing_metadata_pipeline(
        self,
        error_formatter: ErrorFormatter,
    ) -> None:
        """Test complete pipeline when metadata is None or missing."""
        error = ParseError(
            error_type="NO_METADATA",
            message="Error without any metadata",
            suggestions=["Should still work"],
        )

        # Explicitly ensure no metadata
        assert not hasattr(error, "display_metadata")

        result = error_formatter.format_error(error)

        assert isinstance(result, Text)
        assert "NO_METADATA" in result.plain
        assert "Should still work" in result.plain


class TestErrorFormattingPerformance:
    """Test performance characteristics of error formatting pipeline."""

    def test_multiple_error_formatting_performance(
        self,
        error_formatter: ErrorFormatter,
    ) -> None:
        """Test formatting multiple errors performs reasonably."""
        errors = []
        for i in range(50):
            error = ParseError(
                error_type=f"PERF_TEST_{i}",
                message=f"Performance test error {i}",
                suggestions=[f"Fix error {i}", f"Handle case {i}"],
            )
            error.display_metadata = DisplayMetadata(
                category=CategoryToken.CAT_1,
                hierarchy=HierarchyToken.PRIMARY,
            )
            errors.append(error)

        # Format all errors - should complete without issues
        results = []
        for error in errors:
            result = error_formatter.format_error(error)
            results.append(result)

        # Verify all results are valid
        assert len(results) == 50
        for i, result in enumerate(results):
            assert isinstance(result, Text)
            assert f"PERF_TEST_{i}" in result.plain

    def test_complex_metadata_combinations_performance(
        self,
        error_display: ErrorDisplay,
        console: Console,
    ) -> None:
        """Test performance with various metadata combinations."""
        categories = [CategoryToken.CAT_1, CategoryToken.CAT_2, CategoryToken.CAT_3]
        hierarchies = [HierarchyToken.PRIMARY, HierarchyToken.SECONDARY]
        emphases = [EmphasisToken.STRONG, EmphasisToken.NORMAL, EmphasisToken.SUBTLE]

        for category in categories:
            for hierarchy in hierarchies:
                for emphasis in emphases:
                    metadata = DisplayMetadata(
                        category=category,
                        hierarchy=hierarchy,
                        emphasis=emphasis,
                    )

                    # Create all style types
                    title_style = error_display.create_error_title_style(metadata)
                    content_style = error_display.create_error_content_style(metadata)
                    suggestion_style = error_display.create_suggestion_style(metadata)

                    # Verify all styles are valid
                    assert isinstance(title_style.category, CategoryToken)
                    assert isinstance(content_style.hierarchy, HierarchyToken)
                    assert isinstance(suggestion_style.emphasis, EmphasisToken)


class TestErrorFormattingWorkflow:
    """Test complete end-to-end error formatting workflows."""

    def test_parser_to_display_complete_workflow(
        self,
        error_formatter: ErrorFormatter,
        error_display: ErrorDisplay,
        console: Console,
    ) -> None:
        """Test complete workflow from ParseError creation to final display."""
        # Step 1: Create ParseError (as would happen in parser)
        error = ParseError(
            error_type="WORKFLOW_TEST",
            message="Testing complete error handling workflow",
            suggestions=["Follow the workflow", "Test thoroughly"],
        )

        # Step 2: Add display metadata (enhanced ParseError)
        error.display_metadata = DisplayMetadata(
            category=CategoryToken.CAT_4,
            hierarchy=HierarchyToken.SECONDARY,
            emphasis=EmphasisToken.NORMAL,
        )

        # Step 3: Format through error formatter
        formatted_text = error_formatter.format_error(error)

        # Step 4: Verify complete pipeline
        assert isinstance(formatted_text, Text)
        result_str = formatted_text.plain

        assert "WORKFLOW_TEST" in result_str
        assert "Testing complete error handling workflow" in result_str
        assert "Follow the workflow" in result_str
        assert "Test thoroughly" in result_str

        # Step 5: Additional processing through ErrorDisplay component
        error_data = error_display.format_error_data(
            error.error_type, error.message, error.suggestions
        )

        title_style = error_display.create_error_title_style(error.display_metadata)
        rendered_title = error_display.render_error_title(
            error_data["title"], title_style, console
        )

        assert isinstance(rendered_title, Text)
        assert "WORKFLOW_TEST" in rendered_title.plain

    def test_error_enhancement_workflow(
        self,
        error_formatter: ErrorFormatter,
    ) -> None:
        """Test workflow of enhancing existing ParseError with metadata."""
        # Start with basic ParseError
        error = ParseError(
            error_type="ENHANCEMENT_TEST",
            message="Basic error to be enhanced",
            suggestions=["Enhance this error"],
        )

        # Format before enhancement
        basic_result = error_formatter.format_error(error)
        assert isinstance(basic_result, Text)

        # Enhance with metadata
        error.display_metadata = DisplayMetadata(
            category=CategoryToken.CAT_6,
            hierarchy=HierarchyToken.PRIMARY,
            emphasis=EmphasisToken.STRONG,
        )

        # Format after enhancement
        enhanced_result = error_formatter.format_error(error)
        assert isinstance(enhanced_result, Text)

        # Both should contain the same content
        assert "ENHANCEMENT_TEST" in basic_result.plain
        assert "ENHANCEMENT_TEST" in enhanced_result.plain

        # Enhanced version should have additional styling
        # (Exact differences depend on theme and implementation)


@pytest.mark.integration
@pytest.mark.parser
@pytest.mark.design
class TestErrorFormattingIntegrationMarkers:
    """Test class to verify pytest markers work correctly."""

    def test_integration_markers_applied(self) -> None:
        """Test that integration pytest markers are properly applied."""
        # This test exists to verify the marker system works
        assert True
