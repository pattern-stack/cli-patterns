"""Reusable UI components for CLI applications.

This module provides component token mappings using dataclasses for simplicity.
Each component class defines the default token mappings for consistent styling
across the CLI interface.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from rich.console import Console
from rich.panel import Panel as RichPanel
from rich.text import Text

from .tokens import (
    CategoryToken,
    DisplayMetadata,
    DisplayStyle,
    EmphasisToken,
    HierarchyToken,
    StatusToken,
)


@dataclass
class Panel:
    """Token mappings for panel components."""

    border_category: CategoryToken = CategoryToken.CAT_1
    title_hierarchy: HierarchyToken = HierarchyToken.PRIMARY
    title_emphasis: EmphasisToken = EmphasisToken.STRONG
    content_emphasis: EmphasisToken = EmphasisToken.NORMAL


@dataclass
class ProgressBar:
    """Token mappings for progress indicators."""

    complete_status: StatusToken = StatusToken.SUCCESS
    running_status: StatusToken = StatusToken.RUNNING
    pending_status: StatusToken = StatusToken.MUTED
    bar_category: CategoryToken = CategoryToken.CAT_2


@dataclass
class Prompt:
    """Token mappings for interactive prompts."""

    symbol: str = "►"
    category: CategoryToken = CategoryToken.CAT_1
    emphasis: EmphasisToken = EmphasisToken.NORMAL
    error_status: StatusToken = StatusToken.ERROR


@dataclass
class Output:
    """Token mappings for command output."""

    stdout_emphasis: EmphasisToken = EmphasisToken.NORMAL
    stderr_status: StatusToken = StatusToken.ERROR
    debug_emphasis: EmphasisToken = EmphasisToken.SUBTLE
    info_status: StatusToken = StatusToken.INFO


@dataclass
class ErrorDisplay:
    """Component for displaying error messages with design token integration.

    This component provides consistent error formatting across the CLI interface
    using design tokens for styling. It handles error titles, messages, and
    suggestions with appropriate visual hierarchy.
    """

    border_category: CategoryToken = CategoryToken.CAT_1
    title_hierarchy: HierarchyToken = HierarchyToken.PRIMARY
    title_emphasis: EmphasisToken = EmphasisToken.STRONG
    content_emphasis: EmphasisToken = EmphasisToken.NORMAL
    error_status: StatusToken = StatusToken.ERROR
    suggestion_emphasis: EmphasisToken = EmphasisToken.SUBTLE

    def create_error_title_style(
        self, metadata: Optional[DisplayMetadata]
    ) -> DisplayStyle:
        """Create display style for error title.

        Args:
            metadata: Optional display metadata for customization

        Returns:
            DisplayStyle for error title
        """
        return DisplayStyle(
            category=metadata.category if metadata else CategoryToken.CAT_1,
            hierarchy=self.title_hierarchy,
            emphasis=self.title_emphasis,
            status=self.error_status,
        )

    def create_error_content_style(
        self, metadata: Optional[DisplayMetadata]
    ) -> DisplayStyle:
        """Create display style for error content.

        Args:
            metadata: Optional display metadata for customization

        Returns:
            DisplayStyle for error content
        """
        return DisplayStyle(
            category=metadata.category if metadata else CategoryToken.CAT_1,
            hierarchy=metadata.hierarchy if metadata else HierarchyToken.PRIMARY,
            emphasis=self.content_emphasis,
            status=self.error_status,
        )

    def create_suggestion_style(
        self, metadata: Optional[DisplayMetadata]
    ) -> DisplayStyle:
        """Create display style for suggestions.

        Args:
            metadata: Optional display metadata for customization

        Returns:
            DisplayStyle for suggestions
        """
        return DisplayStyle(
            category=metadata.category if metadata else CategoryToken.CAT_1,
            hierarchy=metadata.hierarchy if metadata else HierarchyToken.PRIMARY,
            emphasis=self.suggestion_emphasis,
            status=StatusToken.INFO,  # Suggestions use info status
        )

    def create_border_style(self, metadata: Optional[DisplayMetadata]) -> DisplayStyle:
        """Create display style for border.

        Args:
            metadata: Optional display metadata for customization

        Returns:
            DisplayStyle for border
        """
        return DisplayStyle(
            category=self.border_category,
            hierarchy=metadata.hierarchy if metadata else HierarchyToken.PRIMARY,
            emphasis=metadata.emphasis if metadata else EmphasisToken.NORMAL,
            status=self.error_status,
        )

    def render_error_title(
        self, title_text: str, style: DisplayStyle, console: Console
    ) -> Text:
        """Render error title with styling.

        Args:
            title_text: The error title text
            style: Display style to apply
            console: Rich console for rendering

        Returns:
            Styled Rich Text object
        """
        text = Text(title_text)
        # Apply styling based on design tokens
        # The actual styling would be resolved through the theme system
        return text

    def render_error_message(
        self, message_text: str, style: DisplayStyle, console: Console
    ) -> Text:
        """Render error message with styling.

        Args:
            message_text: The error message text
            style: Display style to apply
            console: Rich console for rendering

        Returns:
            Styled Rich Text object
        """
        text = Text(message_text)
        # Apply styling based on design tokens
        # The actual styling would be resolved through the theme system
        return text

    def render_suggestions_list(
        self, suggestions: list[str], style: DisplayStyle, console: Console
    ) -> Optional[Text]:
        """Render suggestions list with styling.

        Args:
            suggestions: List of suggestion strings
            style: Display style to apply
            console: Rich console for rendering

        Returns:
            Styled Rich Text object or None for empty suggestions
        """
        if not suggestions:
            return Text("")  # Return empty text for empty suggestions

        # Format suggestions as a list
        text_parts = []
        for suggestion in suggestions:
            text_parts.append(suggestion)

        text = Text("\n".join(text_parts))
        # Apply styling based on design tokens
        # The actual styling would be resolved through the theme system
        return text

    def render_error_panel(
        self,
        error_data: dict[str, Any],
        metadata: Optional[DisplayMetadata],
        console: Console,
    ) -> RichPanel:
        """Render complete error panel.

        Args:
            error_data: Dictionary containing error information
            metadata: Optional display metadata for styling
            console: Rich console for rendering

        Returns:
            Rich Panel with complete error display
        """
        # Create styles
        title_style = self.create_error_title_style(metadata)
        content_style = self.create_error_content_style(metadata)
        suggestion_style = self.create_suggestion_style(metadata)
        border_style = self.create_border_style(metadata)

        # Render components
        title_text = self.render_error_title(
            error_data.get("title", ""), title_style, console
        )
        message_text = self.render_error_message(
            error_data.get("message", ""), content_style, console
        )

        # Combine content
        panel_content = Text()
        panel_content.append_text(title_text)
        panel_content.append("\n\n")
        panel_content.append_text(message_text)

        # Add suggestions if present
        suggestions = error_data.get("suggestions", [])
        if suggestions:
            suggestions_text = self.render_suggestions_list(
                suggestions, suggestion_style, console
            )
            if suggestions_text and suggestions_text.plain.strip():
                panel_content.append("\n\nSuggestions:\n")
                panel_content.append_text(suggestions_text)

        # Create panel with border styling
        # Convert status to color for border
        border_color = "red"  # Default error color
        if border_style.status == StatusToken.WARNING:
            border_color = "yellow"
        elif border_style.status == StatusToken.INFO:
            border_color = "blue"
        elif border_style.status == StatusToken.SUCCESS:
            border_color = "green"

        return RichPanel(panel_content, title="Error", border_style=border_color)

    def format_error_data(
        self, error_type: str, message: str, suggestions: Optional[list[str]]
    ) -> dict[str, Any]:
        """Format error data into structured dictionary.

        Args:
            error_type: Type of error
            message: Error message
            suggestions: Optional list of suggestions

        Returns:
            Formatted error data dictionary
        """
        return {
            "title": error_type,
            "message": message,
            "suggestions": suggestions or [],
        }

    def truncate_text(self, text: str, max_length: int) -> str:
        """Truncate text to maximum length with ellipsis.

        Args:
            text: Text to truncate
            max_length: Maximum length

        Returns:
            Truncated text with ellipsis if needed
        """
        if len(text) <= max_length:
            return text
        return text[: max_length - 3] + "..."

    def wrap_text(self, text: str, width: int) -> list[str]:
        """Wrap text to specified width.

        Args:
            text: Text to wrap
            width: Maximum line width

        Returns:
            List of wrapped lines
        """
        lines = text.split("\n")
        wrapped_lines = []

        for line in lines:
            if len(line) <= width:
                wrapped_lines.append(line)
            else:
                # Simple word wrapping
                words = line.split(" ")
                current_line = ""

                for word in words:
                    if len(current_line + " " + word) <= width:
                        if current_line:
                            current_line += " " + word
                        else:
                            current_line = word
                    else:
                        if current_line:
                            wrapped_lines.append(current_line)
                        current_line = word

                if current_line:
                    wrapped_lines.append(current_line)

        return wrapped_lines

    def sanitize_text(self, text: str) -> str:
        """Sanitize text for safe display.

        Args:
            text: Text to sanitize

        Returns:
            Sanitized text
        """
        # Replace control characters with visible representations
        sanitized = text.replace("\t", "    ")  # Replace tabs with spaces
        sanitized = sanitized.replace("\r", "")  # Remove carriage returns
        return sanitized
