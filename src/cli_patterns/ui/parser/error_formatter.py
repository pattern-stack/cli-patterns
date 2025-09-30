"""Error formatter for parser errors with design token integration."""

from __future__ import annotations

from typing import Optional

from rich.console import Console
from rich.text import Text

from cli_patterns.ui.design.components import ErrorDisplay
from cli_patterns.ui.design.tokens import (
    DisplayMetadata,
    DisplayStyle,
    EmphasisToken,
    StatusToken,
)
from cli_patterns.ui.parser.types import ParseError


class ErrorFormatter:
    """Formatter for ParseError objects with design token styling.

    This class provides a high-level interface for formatting ParseError objects
    into styled Rich Text objects using the design token system and ErrorDisplay
    component for consistent styling.
    """

    def __init__(self, console: Optional[Console] = None) -> None:
        """Initialize ErrorFormatter.

        Args:
            console: Optional Rich console instance. If not provided, a default
                    console will be created.
        """
        self.console = console or Console()
        self.error_display = ErrorDisplay()

    def format_error(self, error: ParseError) -> Text:
        """Format a ParseError into styled Rich Text.

        This is the main entry point for error formatting. It handles both
        legacy ParseError objects without display metadata and enhanced
        ParseError objects with display metadata.

        Args:
            error: ParseError instance to format

        Returns:
            Styled Rich Text object containing the formatted error
        """
        # Get display metadata if available, or None for backward compatibility
        metadata = getattr(error, "display_metadata", None)

        # Format the error data
        error_data = self.error_display.format_error_data(
            error.error_type, error.message, error.suggestions
        )

        # Create styles based on metadata
        title_style = self.error_display.create_error_title_style(metadata)
        content_style = self.error_display.create_error_content_style(metadata)
        suggestion_style = self.error_display.create_suggestion_style(metadata)

        # Render error components
        title_text = self.error_display.render_error_title(
            error_data["title"], title_style, self.console
        )
        message_text = self.error_display.render_error_message(
            error_data["message"], content_style, self.console
        )

        # Combine into final formatted text
        result = Text()

        # Add title with styling
        styled_title = self.apply_error_styling(title_text, StatusToken.ERROR)
        result.append_text(styled_title)
        result.append("\n\n")

        # Add message
        result.append_text(message_text)

        # Add suggestions if present
        suggestions = error_data.get("suggestions", [])
        if suggestions:
            suggestions_text = self.format_suggestions(suggestions)
            if suggestions_text and suggestions_text.plain.strip():
                result.append("\n\nSuggestions:\n")
                styled_suggestions = self.apply_suggestion_styling(
                    suggestions_text, suggestion_style.emphasis
                )
                result.append_text(styled_suggestions)

        return result

    def format_suggestions(self, suggestions: list[str]) -> Optional[Text]:
        """Format a list of suggestions into styled text.

        Args:
            suggestions: List of suggestion strings

        Returns:
            Styled Rich Text object or None for empty suggestions
        """
        if not suggestions:
            return Text("")

        # Format as bullet list
        text_parts = []
        for suggestion in suggestions:
            text_parts.append(f"• {suggestion}")

        return Text("\n".join(text_parts))

    def apply_error_styling(self, text: Text, status: StatusToken) -> Text:
        """Apply error styling to text based on status token.

        Args:
            text: Rich Text object to style
            status: Status token for styling

        Returns:
            Styled Rich Text object
        """
        # Apply status-based styling
        # The actual styling would be resolved through the theme system
        # For now, return the text as-is with basic styling
        if status == StatusToken.ERROR:
            text.stylize("bold red")
        elif status == StatusToken.WARNING:
            text.stylize("bold yellow")
        elif status == StatusToken.INFO:
            text.stylize("blue")

        return text

    def apply_suggestion_styling(self, text: Text, emphasis: EmphasisToken) -> Text:
        """Apply suggestion styling to text based on emphasis token.

        Args:
            text: Rich Text object to style
            emphasis: Emphasis token for styling

        Returns:
            Styled Rich Text object
        """
        # Apply emphasis-based styling
        if emphasis == EmphasisToken.SUBTLE:
            text.stylize("dim")
        elif emphasis == EmphasisToken.STRONG:
            text.stylize("bold")
        # NORMAL emphasis doesn't need additional styling

        return text

    def resolve_metadata_style(
        self, metadata: Optional[DisplayMetadata], status: StatusToken
    ) -> DisplayStyle:
        """Resolve display metadata to a complete display style.

        Args:
            metadata: Optional display metadata
            status: Status token to apply

        Returns:
            Complete DisplayStyle object
        """
        if metadata:
            return metadata.with_status(status)
        else:
            # Return default style for backward compatibility
            return DisplayStyle.from_metadata(
                DisplayMetadata.model_validate(
                    {"category": "cat_1", "hierarchy": "primary", "emphasis": "normal"}
                ),
                status=status,
            )
