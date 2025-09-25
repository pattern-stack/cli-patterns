"""Theme loading and configuration management.

This module provides functions for loading themes from YAML files,
handling theme inheritance, and applying themes from environment variables.
It supports both system-wide and user-specific theme configurations.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]

from ..ui.design.registry import theme_registry
from ..ui.design.themes import Theme
from ..ui.design.tokens import CategoryToken, EmphasisToken, HierarchyToken, StatusToken


class ThemeLoadError(Exception):
    """Raised when theme loading fails."""

    pass


def _validate_token_mappings(data: dict[str, Any]) -> None:
    """Validate that all required token mappings are present.

    Args:
        data: The theme data dictionary

    Raises:
        ThemeLoadError: If required mappings are missing or invalid
    """
    required_sections = ["categories", "hierarchies", "statuses", "emphases"]

    for section in required_sections:
        if section not in data:
            raise ThemeLoadError(f"Missing required section: {section}")

        if not isinstance(data[section], dict):
            raise ThemeLoadError(f"Section '{section}' must be a dictionary")

    # Validate category tokens
    categories = data["categories"]
    for token in CategoryToken:
        if token.value not in categories:
            raise ThemeLoadError(f"Missing category token: {token.value}")

    # Validate hierarchy tokens
    hierarchies = data["hierarchies"]
    for hierarchy_token in HierarchyToken:
        if hierarchy_token.value not in hierarchies:
            raise ThemeLoadError(f"Missing hierarchy token: {hierarchy_token.value}")

    # Validate status tokens
    statuses = data["statuses"]
    for status_token in StatusToken:
        if status_token.value not in statuses:
            raise ThemeLoadError(f"Missing status token: {status_token.value}")

    # Validate emphasis tokens
    emphases = data["emphases"]
    for emphasis_token in EmphasisToken:
        if emphasis_token.value not in emphases:
            raise ThemeLoadError(f"Missing emphasis token: {emphasis_token.value}")


def load_theme_from_yaml(path: Path | str) -> Theme:
    """Load a theme from a YAML file.

    Args:
        path: Path to the YAML theme file (string or Path object)

    Returns:
        Loaded theme instance

    Raises:
        ThemeLoadError: If the theme file is invalid or cannot be loaded
        FileNotFoundError: If the theme file does not exist
    """
    if isinstance(path, str):
        path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Theme file not found: {path}")

    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ThemeLoadError(f"Invalid YAML in theme file {path}: {e}") from e

    if not isinstance(data, dict):
        raise ThemeLoadError(f"Theme file {path} must contain a dictionary")

    # Validate required fields
    if "name" not in data:
        raise ThemeLoadError(f"Theme file {path} missing required 'name' field")

    name = data["name"]
    extends = data.get("extends")

    # Handle inheritance
    base_theme = None
    if extends:
        try:
            base_theme = theme_registry.get_theme(extends)
        except KeyError:
            raise ThemeLoadError(f"Parent theme '{extends}' not found") from None

    # Validate token mappings
    _validate_token_mappings(data)

    # Build token mappings
    categories = {CategoryToken(k): v for k, v in data["categories"].items()}
    hierarchies = {HierarchyToken(k): v for k, v in data["hierarchies"].items()}
    statuses = {StatusToken(k): v for k, v in data["statuses"].items()}
    emphases = {EmphasisToken(k): v for k, v in data["emphases"].items()}

    # Create theme
    theme = Theme(
        name=name,
        categories=categories,
        hierarchies=hierarchies,
        statuses=statuses,
        emphases=emphases,
        extends=extends,
    )

    # Apply inheritance if needed
    if base_theme:
        theme = base_theme.merge_with(theme)

    return theme


def load_user_themes() -> list[Theme]:
    """Load all user themes from ~/.cli-patterns/themes/.

    Searches for .yaml files in the user themes directory and loads
    them as custom themes.

    Returns:
        List of loaded theme instances

    Raises:
        ThemeLoadError: If any theme file is invalid
    """
    themes_dir = Path.home() / ".cli-patterns" / "themes"

    if not themes_dir.exists():
        return []

    loaded_themes: list[Theme] = []

    # Load all .yaml files in the themes directory
    for theme_file in themes_dir.glob("*.yaml"):
        try:
            theme = load_theme_from_yaml(theme_file)
            loaded_themes.append(theme)
        except (FileNotFoundError, ThemeLoadError) as e:
            # Log the error but continue loading other themes
            print(f"Warning: Failed to load theme from {theme_file}: {e}")
            continue

    return loaded_themes


def register_user_themes() -> None:
    """Load and register all user themes with the theme registry.

    This function loads themes from the user's theme directory and
    registers them with the global theme registry.
    """
    try:
        user_themes = load_user_themes()
        for theme in user_themes:
            try:
                theme_registry.register(theme)
            except ValueError as e:
                # Theme already exists, skip it
                print(f"Warning: {e}")
                continue
    except Exception as e:
        print(f"Warning: Failed to load user themes: {e}")


def apply_theme_from_env() -> None:
    """Apply theme from CLI_PATTERNS_THEME environment variable.

    Checks for the CLI_PATTERNS_THEME environment variable and sets
    it as the current theme if it exists and is registered.
    """
    theme_name = os.environ.get("CLI_PATTERNS_THEME")

    if not theme_name:
        return

    try:
        theme_registry.set_current(theme_name)
    except KeyError:
        print(f"Warning: Theme '{theme_name}' from CLI_PATTERNS_THEME not found")


def initialize_themes() -> None:
    """Initialize the theme system.

    This function should be called at application startup to:
    1. Register user themes
    2. Apply theme from environment variables
    """
    register_user_themes()
    apply_theme_from_env()
