"""Rich adapter layer for mapping design tokens to Rich components.

This module provides adapters that bridge our design token system with Rich's
display capabilities, ensuring consistent theming across all output.
"""

from __future__ import annotations

from typing import Any, Optional

from rich.box import ASCII, DOUBLE, HEAVY, MINIMAL, ROUNDED
from rich.box import Box as RichBox
from rich.console import Console
from rich.panel import Panel as RichPanel
from rich.style import Style
from rich.theme import Theme as RichTheme

from .design.boxes import BOX_STYLES, BoxStyle
from .design.components import Panel
from .design.registry import theme_registry
from .design.tokens import CategoryToken, EmphasisToken, HierarchyToken, StatusToken


class RichAdapter:
    """Adapter for Rich components using our design token system."""

    def __init__(self) -> None:
        """Initialize the Rich adapter."""
        self._console: Optional[Console] = None
        self._unthemed_components: set[str] = set()
        self._component_usage: dict[str, int] = {}

    def create_console(self) -> Console:
        """Create a Rich Console with our theme applied.

        Returns:
            Configured Rich Console instance with current theme
        """
        rich_theme = self._create_rich_theme()
        self._console = Console(theme=rich_theme, legacy_windows=False)
        return self._console

    def _create_rich_theme(self) -> RichTheme:
        """Convert our theme tokens to Rich Theme.

        Returns:
            Rich Theme object with mapped token styles
        """
        current_theme = theme_registry.get_current()
        styles = {}

        # Map CategoryTokens
        for cat in CategoryToken:
            color = self._normalize_color(current_theme.categories[cat])
            styles[f"cat.{cat.value}"] = Style(color=color)

        # Map StatusTokens
        for status in StatusToken:
            style_str = current_theme.statuses[status]
            # Parse style string (e.g., "red bold" -> color="red", bold=True)
            parts = style_str.split()
            status_color: Optional[str] = (
                self._normalize_color(parts[0]) if parts else None
            )
            bold = "bold" in parts
            italic = "italic" in parts
            dim = "dim" in parts
            styles[f"status.{status.value}"] = Style(
                color=status_color, bold=bold, italic=italic, dim=dim
            )

        # Map EmphasisTokens
        for emphasis in EmphasisToken:
            style_str = current_theme.emphases[emphasis]
            bold = "bold" in style_str
            dim = "dim" in style_str
            styles[f"emphasis.{emphasis.value}"] = Style(bold=bold, dim=dim)

        # Map HierarchyTokens
        for hierarchy in HierarchyToken:
            style_str = current_theme.hierarchies[hierarchy]
            bold = "bold" in style_str
            italic = "italic" in style_str
            dim = "dim" in style_str
            styles[f"hierarchy.{hierarchy.value}"] = Style(
                bold=bold, italic=italic, dim=dim
            )

        return RichTheme(styles)

    def _normalize_color(self, color: str) -> str:
        """Normalize color names to Rich-compatible format.

        Args:
            color: Color name to normalize

        Returns:
            Rich-compatible color name
        """
        # Map problematic color names to Rich-compatible ones
        color_map = {
            "bright_black": "grey62",  # A medium grey that works well
            "bright_yellow": "yellow",
            "grey50": "grey62",
        }
        return color_map.get(color, color)

    def panel(
        self,
        content: Any,
        *,
        title: Optional[str] = None,
        box_style: str = "rounded",
        border_category: Optional[CategoryToken] = None,
        **kwargs: Any,
    ) -> RichPanel:
        """Create a themed Rich Panel using our design tokens.

        Args:
            content: The content to display in the panel
            title: Optional title for the panel
            box_style: Name of box style from our BOX_STYLES
            border_category: Category token for border color
            **kwargs: Additional arguments to pass to Rich Panel

        Returns:
            Themed Rich Panel instance
        """
        self._track_component("panel")

        # Get panel component defaults
        panel_component = Panel()

        # Use provided category or default from component
        if border_category is None:
            border_category = panel_component.border_category

        # Get border color from theme
        border_color = self._normalize_color(theme_registry.resolve(border_category))

        # Get title styling
        # title_style = None  # TODO: Apply title styling to panel
        if title:
            title_emphasis = theme_registry.resolve(panel_component.title_emphasis)
            title_hierarchy = theme_registry.resolve(panel_component.title_hierarchy)
            # Combine styles
            title_parts = []
            if title_emphasis != "default":
                title_parts.append(title_emphasis)
            if title_hierarchy != "default":
                title_parts.append(title_hierarchy)
            # title_style = " ".join(title_parts) if title_parts else None  # TODO: Apply to title

        # Map our box style to Rich box
        rich_box = self._get_rich_box(box_style)

        return RichPanel(
            content,
            title=title,
            title_align="left",
            border_style=border_color,
            box=rich_box,
            **kwargs,
        )

    def _get_rich_box(self, style_name: str) -> RichBox:
        """Get Rich Box from our box style name.

        Args:
            style_name: Name of box style from BOX_STYLES

        Returns:
            Rich Box instance
        """
        # Map our box styles to Rich's built-in boxes
        rich_box_map = {
            "rounded": ROUNDED,
            "heavy": HEAVY,
            "ascii": ASCII,
            "double": DOUBLE,
            "minimal": MINIMAL,
        }

        if style_name in rich_box_map:
            return rich_box_map[style_name]

        # For custom boxes, create a Rich Box from our BoxStyle
        if style_name in BOX_STYLES:
            box_style = BOX_STYLES[style_name]
            return self._create_custom_rich_box(box_style)

        # Default to rounded
        return ROUNDED

    def _create_custom_rich_box(self, box_style: BoxStyle) -> RichBox:
        """Create a custom Rich Box from our BoxStyle.

        Args:
            box_style: Our BoxStyle dataclass

        Returns:
            Custom Rich Box instance
        """

        # Rich expects a specific format for custom boxes
        # This is a simplified version - Rich's Box is more complex
        class CustomBox(RichBox):
            def __init__(self) -> None:
                # Rich expects a specific format for custom boxes
                # This would need to be implemented properly for custom box support
                pass

        return ROUNDED  # Fallback for now, custom boxes need more work

    def _track_component(self, component_name: str) -> None:
        """Track usage of a Rich component.

        Args:
            component_name: Name of the Rich component being used
        """
        if component_name not in self._component_usage:
            self._component_usage[component_name] = 0
        self._component_usage[component_name] += 1

    def track_unthemed_component(self, component_name: str) -> None:
        """Track a Rich component that hasn't been themed yet.

        Args:
            component_name: Name of the unthemed Rich component
        """
        self._unthemed_components.add(component_name)

    def get_coverage_report(self) -> dict[str, Any]:
        """Get a report of themed vs unthemed Rich components.

        Returns:
            Dictionary with coverage statistics
        """
        return {
            "themed_components": list(self._component_usage.keys()),
            "unthemed_components": list(self._unthemed_components),
            "usage_stats": self._component_usage.copy(),
            "coverage_percentage": self._calculate_coverage(),
        }

    def _calculate_coverage(self) -> float:
        """Calculate theming coverage percentage.

        Returns:
            Percentage of components that are themed
        """
        total = len(self._component_usage) + len(self._unthemed_components)
        if total == 0:
            return 100.0
        themed = len(self._component_usage)
        return (themed / total) * 100.0

    def refresh_theme(self) -> None:
        """Refresh console theme after theme change."""
        if self._console:
            # Rich Console doesn't have a mutable theme attribute
            # We need to recreate the console with the new theme
            rich_theme = self._create_rich_theme()
            self._console = Console(theme=rich_theme, legacy_windows=False)


# Global adapter instance
rich_adapter = RichAdapter()
