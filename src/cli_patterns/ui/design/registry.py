"""Theme registry for managing and resolving CLI themes.

This module provides the centralized theme management system that handles
theme registration, resolution, and switching. It maintains a global registry
of available themes and provides the current active theme.
"""

from __future__ import annotations

from typing import Union

from .themes import DarkTheme, LightTheme, Theme
from .tokens import CategoryToken, EmphasisToken, HierarchyToken, StatusToken


class ThemeRegistry:
    """Central registry for managing CLI themes.

    This class maintains a collection of available themes and provides
    methods for theme registration, switching, and token resolution.
    It acts as the single source of truth for theme management.
    """

    def __init__(self) -> None:
        """Initialize the theme registry with default themes."""
        self._themes: dict[str, Theme] = {}
        self._current: Theme = DarkTheme()  # Default to dark theme

        # Register default themes
        self.register(DarkTheme())
        self.register(LightTheme())

    def register(self, theme: Theme) -> None:
        """Register a theme with the registry.

        Args:
            theme: The theme to register

        Raises:
            ValueError: If a theme with the same name already exists
        """
        if theme.name in self._themes:
            raise ValueError(f"Theme '{theme.name}' is already registered")

        self._themes[theme.name] = theme

    def set_current(self, name: str) -> None:
        """Set the current active theme.

        Args:
            name: The name of the theme to activate

        Raises:
            KeyError: If the theme name is not registered
        """
        if name not in self._themes:
            raise KeyError(f"Theme '{name}' is not registered")

        self._current = self._themes[name]

    def get_current(self) -> Theme:
        """Get the currently active theme.

        Returns:
            The current active theme instance
        """
        return self._current

    def resolve(
        self, token: Union[CategoryToken, HierarchyToken, StatusToken, EmphasisToken]
    ) -> str:
        """Resolve a token using the current active theme.

        This is a convenience method that delegates to the current theme's
        resolve method.

        Args:
            token: The design token to resolve

        Returns:
            Rich-compatible color or style string

        Raises:
            KeyError: If the token is not found in the current theme
            ValueError: If the token type is unknown
        """
        return self._current.resolve(token)

    def list_themes(self) -> list[str]:
        """Get a list of all registered theme names.

        Returns:
            List of theme names sorted alphabetically
        """
        return sorted(self._themes.keys())

    def get_theme(self, name: str) -> Theme:
        """Get a specific theme by name.

        Args:
            name: The name of the theme to retrieve

        Returns:
            The theme instance

        Raises:
            KeyError: If the theme name is not registered
        """
        if name not in self._themes:
            raise KeyError(f"Theme '{name}' is not registered")

        return self._themes[name]


# Global theme registry instance
theme_registry = ThemeRegistry()
