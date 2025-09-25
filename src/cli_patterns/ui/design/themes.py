"""Theme management and application for CLI components.

This module provides the theme system that maps design tokens to Rich-compatible
colors and styles. It supports theme inheritance, customization, and provides
both light and dark themes out of the box.
"""

from __future__ import annotations

from typing import Optional, Union

from .tokens import CategoryToken, EmphasisToken, HierarchyToken, StatusToken


class Theme:
    """Base theme class that maps design tokens to Rich-compatible styles.

    This class provides the foundation for the theme system, allowing tokens
    to be resolved to Rich-compatible color and style strings. It supports
    theme inheritance through the merge_with method.
    """

    def __init__(
        self,
        name: str,
        categories: dict[CategoryToken, str],
        hierarchies: dict[HierarchyToken, str],
        statuses: dict[StatusToken, str],
        emphases: dict[EmphasisToken, str],
        extends: Optional[str] = None,
    ) -> None:
        """Initialize a theme with token mappings.

        Args:
            name: Unique identifier for this theme
            categories: Mapping of category tokens to Rich color strings
            hierarchies: Mapping of hierarchy tokens to Rich style strings
            statuses: Mapping of status tokens to Rich color/style strings
            emphases: Mapping of emphasis tokens to Rich style strings
            extends: Optional name of parent theme for inheritance
        """
        self.name = name
        self.categories = categories
        self.hierarchies = hierarchies
        self.statuses = statuses
        self.emphases = emphases
        self.extends = extends

    def resolve(
        self, token: Union[CategoryToken, HierarchyToken, StatusToken, EmphasisToken]
    ) -> str:
        """Resolve any token type to its Rich-compatible style string.

        Args:
            token: The design token to resolve

        Returns:
            Rich-compatible color or style string

        Raises:
            KeyError: If the token is not found in this theme
        """
        if isinstance(token, CategoryToken):
            return self.categories[token]
        elif isinstance(token, HierarchyToken):
            return self.hierarchies[token]
        elif isinstance(token, StatusToken):
            return self.statuses[token]
        elif isinstance(token, EmphasisToken):
            return self.emphases[token]
        else:
            raise ValueError(f"Unknown token type: {type(token)}")

    def merge_with(self, other: Theme) -> Theme:
        """Merge this theme with another theme for inheritance.

        The other theme's values take precedence over this theme's values.

        Args:
            other: The theme to merge with (takes precedence)

        Returns:
            A new Theme instance with merged values
        """
        merged_categories = {**self.categories, **other.categories}
        merged_hierarchies = {**self.hierarchies, **other.hierarchies}
        merged_statuses = {**self.statuses, **other.statuses}
        merged_emphases = {**self.emphases, **other.emphases}

        return Theme(
            name=other.name,
            categories=merged_categories,
            hierarchies=merged_hierarchies,
            statuses=merged_statuses,
            emphases=merged_emphases,
            extends=self.name,
        )


class DarkTheme(Theme):
    """Professional dark theme optimized for dark terminals.

    This theme provides a carefully selected color palette that works well
    in dark terminal environments, with high contrast and good readability.
    """

    def __init__(self) -> None:
        """Initialize the dark theme with professional dark colors."""
        categories = {
            CategoryToken.CAT_1: "cyan",
            CategoryToken.CAT_2: "magenta",
            CategoryToken.CAT_3: "yellow",
            CategoryToken.CAT_4: "green",
            CategoryToken.CAT_5: "blue",
            CategoryToken.CAT_6: "red",
            CategoryToken.CAT_7: "white",
            CategoryToken.CAT_8: "bright_black",
        }

        hierarchies = {
            HierarchyToken.PRIMARY: "bold",
            HierarchyToken.SECONDARY: "default",
            HierarchyToken.TERTIARY: "dim",
            HierarchyToken.QUATERNARY: "dim italic",
        }

        statuses = {
            StatusToken.SUCCESS: "green",
            StatusToken.ERROR: "red bold",
            StatusToken.WARNING: "yellow",
            StatusToken.INFO: "blue",
            StatusToken.MUTED: "bright_black",
            StatusToken.RUNNING: "cyan italic",
        }

        emphases = {
            EmphasisToken.STRONG: "bold",
            EmphasisToken.NORMAL: "default",
            EmphasisToken.SUBTLE: "dim",
        }

        super().__init__(
            name="dark",
            categories=categories,
            hierarchies=hierarchies,
            statuses=statuses,
            emphases=emphases,
        )


class LightTheme(Theme):
    """Professional light theme optimized for light terminals.

    This theme provides colors and styles that work well in light terminal
    environments, with appropriate contrast adjustments for readability.
    """

    def __init__(self) -> None:
        """Initialize the light theme with appropriate light terminal colors."""
        categories = {
            CategoryToken.CAT_1: "blue",
            CategoryToken.CAT_2: "magenta",
            CategoryToken.CAT_3: "bright_yellow",
            CategoryToken.CAT_4: "green",
            CategoryToken.CAT_5: "cyan",
            CategoryToken.CAT_6: "red",
            CategoryToken.CAT_7: "black",
            CategoryToken.CAT_8: "bright_black",
        }

        hierarchies = {
            HierarchyToken.PRIMARY: "bold",
            HierarchyToken.SECONDARY: "default",
            HierarchyToken.TERTIARY: "dim",
            HierarchyToken.QUATERNARY: "dim italic",
        }

        statuses = {
            StatusToken.SUCCESS: "green",
            StatusToken.ERROR: "red bold",
            StatusToken.WARNING: "bright_yellow",
            StatusToken.INFO: "blue",
            StatusToken.MUTED: "bright_black",
            StatusToken.RUNNING: "cyan italic",
        }

        emphases = {
            EmphasisToken.STRONG: "bold",
            EmphasisToken.NORMAL: "default",
            EmphasisToken.SUBTLE: "dim",
        }

        super().__init__(
            name="light",
            categories=categories,
            hierarchies=hierarchies,
            statuses=statuses,
            emphases=emphases,
        )
