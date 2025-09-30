"""Tests for theme management and resolution."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from cli_patterns.config.theme_loader import (
    ThemeLoadError,
    apply_theme_from_env,
    load_theme_from_yaml,
    load_user_themes,
)
from cli_patterns.ui.design.registry import ThemeRegistry
from cli_patterns.ui.design.themes import DarkTheme, LightTheme, Theme
from cli_patterns.ui.design.tokens import (
    CategoryToken,
    EmphasisToken,
    HierarchyToken,
    StatusToken,
)

pytestmark = pytest.mark.design


class TestTheme:
    """Tests for the base Theme class."""

    def test_theme_initialization(self) -> None:
        """Test theme initialization with all parameters."""
        categories = {CategoryToken.CAT_1: "red", CategoryToken.CAT_2: "blue"}
        hierarchies = {HierarchyToken.PRIMARY: "bold"}
        statuses = {StatusToken.SUCCESS: "green"}
        emphases = {EmphasisToken.STRONG: "bold"}

        theme = Theme(
            name="test",
            categories=categories,
            hierarchies=hierarchies,
            statuses=statuses,
            emphases=emphases,
            extends="parent",
        )

        assert theme.name == "test"
        assert theme.categories == categories
        assert theme.hierarchies == hierarchies
        assert theme.statuses == statuses
        assert theme.emphases == emphases
        assert theme.extends == "parent"

    def test_resolve_category_token(self) -> None:
        """Test resolving category tokens."""
        theme = Theme(
            name="test",
            categories={CategoryToken.CAT_1: "red"},
            hierarchies={},
            statuses={},
            emphases={},
        )

        result = theme.resolve(CategoryToken.CAT_1)
        assert result == "red"

    def test_resolve_hierarchy_token(self) -> None:
        """Test resolving hierarchy tokens."""
        theme = Theme(
            name="test",
            categories={},
            hierarchies={HierarchyToken.PRIMARY: "bold"},
            statuses={},
            emphases={},
        )

        result = theme.resolve(HierarchyToken.PRIMARY)
        assert result == "bold"

    def test_resolve_status_token(self) -> None:
        """Test resolving status tokens."""
        theme = Theme(
            name="test",
            categories={},
            hierarchies={},
            statuses={StatusToken.SUCCESS: "green"},
            emphases={},
        )

        result = theme.resolve(StatusToken.SUCCESS)
        assert result == "green"

    def test_resolve_emphasis_token(self) -> None:
        """Test resolving emphasis tokens."""
        theme = Theme(
            name="test",
            categories={},
            hierarchies={},
            statuses={},
            emphases={EmphasisToken.STRONG: "bold"},
        )

        result = theme.resolve(EmphasisToken.STRONG)
        assert result == "bold"

    def test_resolve_unknown_token(self) -> None:
        """Test resolving unknown token raises KeyError."""
        theme = Theme(
            name="test",
            categories={},
            hierarchies={},
            statuses={},
            emphases={},
        )

        with pytest.raises(KeyError):
            theme.resolve(CategoryToken.CAT_1)

    def test_resolve_invalid_token_type(self) -> None:
        """Test resolving invalid token type raises ValueError."""
        theme = Theme(
            name="test",
            categories={},
            hierarchies={},
            statuses={},
            emphases={},
        )

        with pytest.raises(ValueError, match="Unknown token type"):
            theme.resolve("invalid")  # type: ignore

    def test_merge_with_other_theme(self) -> None:
        """Test merging themes with inheritance."""
        base_theme = Theme(
            name="base",
            categories={CategoryToken.CAT_1: "red", CategoryToken.CAT_2: "blue"},
            hierarchies={HierarchyToken.PRIMARY: "bold"},
            statuses={StatusToken.SUCCESS: "green"},
            emphases={EmphasisToken.STRONG: "bold"},
        )

        child_theme = Theme(
            name="child",
            categories={CategoryToken.CAT_1: "yellow"},  # Override
            hierarchies={HierarchyToken.SECONDARY: "dim"},  # Add new
            statuses={},  # Empty
            emphases={EmphasisToken.NORMAL: "default"},  # Add new
        )

        merged = base_theme.merge_with(child_theme)

        # Child takes precedence
        assert merged.name == "child"
        assert merged.extends == "base"

        # Check merged mappings
        assert merged.categories[CategoryToken.CAT_1] == "yellow"  # Overridden
        assert merged.categories[CategoryToken.CAT_2] == "blue"  # From base
        assert merged.hierarchies[HierarchyToken.PRIMARY] == "bold"  # From base
        assert merged.hierarchies[HierarchyToken.SECONDARY] == "dim"  # From child
        assert merged.statuses[StatusToken.SUCCESS] == "green"  # From base
        assert merged.emphases[EmphasisToken.STRONG] == "bold"  # From base
        assert merged.emphases[EmphasisToken.NORMAL] == "default"  # From child


class TestDarkTheme:
    """Tests for the DarkTheme class."""

    def test_dark_theme_initialization(self) -> None:
        """Test dark theme has all required tokens."""
        theme = DarkTheme()

        assert theme.name == "dark"
        assert theme.extends is None

        # Check all category tokens are present
        for token in CategoryToken:
            assert token in theme.categories

        # Check all hierarchy tokens are present
        for token in HierarchyToken:
            assert token in theme.hierarchies

        # Check all status tokens are present
        for token in StatusToken:
            assert token in theme.statuses

        # Check all emphasis tokens are present
        for token in EmphasisToken:
            assert token in theme.emphases

    def test_dark_theme_colors(self) -> None:
        """Test dark theme has expected colors."""
        theme = DarkTheme()

        assert theme.categories[CategoryToken.CAT_1] == "cyan"
        assert theme.statuses[StatusToken.SUCCESS] == "green"
        assert theme.hierarchies[HierarchyToken.PRIMARY] == "bold"
        assert theme.emphases[EmphasisToken.STRONG] == "bold"


class TestLightTheme:
    """Tests for the LightTheme class."""

    def test_light_theme_initialization(self) -> None:
        """Test light theme has all required tokens."""
        theme = LightTheme()

        assert theme.name == "light"
        assert theme.extends is None

        # Check all category tokens are present
        for token in CategoryToken:
            assert token in theme.categories

        # Check all hierarchy tokens are present
        for token in HierarchyToken:
            assert token in theme.hierarchies

        # Check all status tokens are present
        for token in StatusToken:
            assert token in theme.statuses

        # Check all emphasis tokens are present
        for token in EmphasisToken:
            assert token in theme.emphases

    def test_light_theme_colors(self) -> None:
        """Test light theme has expected colors for light terminals."""
        theme = LightTheme()

        assert theme.categories[CategoryToken.CAT_1] == "blue"
        assert theme.statuses[StatusToken.WARNING] == "bright_yellow"
        assert theme.categories[CategoryToken.CAT_7] == "black"  # Different from dark


class TestThemeRegistry:
    """Tests for the ThemeRegistry class."""

    def test_registry_initialization(self) -> None:
        """Test registry initializes with default themes."""
        registry = ThemeRegistry()

        themes = registry.list_themes()
        assert "dark" in themes
        assert "light" in themes

        # Default should be dark theme
        current = registry.get_current()
        assert current.name == "dark"

    def test_register_theme(self) -> None:
        """Test registering a custom theme."""
        registry = ThemeRegistry()

        custom_theme = Theme(
            name="custom",
            categories={CategoryToken.CAT_1: "purple"},
            hierarchies={HierarchyToken.PRIMARY: "bold"},
            statuses={StatusToken.SUCCESS: "lime"},
            emphases={EmphasisToken.STRONG: "bold"},
        )

        registry.register(custom_theme)

        themes = registry.list_themes()
        assert "custom" in themes

        retrieved = registry.get_theme("custom")
        assert retrieved.name == "custom"

    def test_register_duplicate_theme_raises_error(self) -> None:
        """Test registering duplicate theme name raises ValueError."""
        registry = ThemeRegistry()

        duplicate_theme = Theme(
            name="dark",  # Already exists
            categories={CategoryToken.CAT_1: "purple"},
            hierarchies={HierarchyToken.PRIMARY: "bold"},
            statuses={StatusToken.SUCCESS: "lime"},
            emphases={EmphasisToken.STRONG: "bold"},
        )

        with pytest.raises(ValueError, match="already registered"):
            registry.register(duplicate_theme)

    def test_set_current_theme(self) -> None:
        """Test setting current theme."""
        registry = ThemeRegistry()

        registry.set_current("light")
        current = registry.get_current()
        assert current.name == "light"

    def test_set_unknown_theme_raises_error(self) -> None:
        """Test setting unknown theme raises KeyError."""
        registry = ThemeRegistry()

        with pytest.raises(KeyError, match="not registered"):
            registry.set_current("unknown")

    def test_get_unknown_theme_raises_error(self) -> None:
        """Test getting unknown theme raises KeyError."""
        registry = ThemeRegistry()

        with pytest.raises(KeyError, match="not registered"):
            registry.get_theme("unknown")

    def test_resolve_delegates_to_current_theme(self) -> None:
        """Test resolve method delegates to current theme."""
        registry = ThemeRegistry()

        # Should resolve using dark theme (default)
        result = registry.resolve(StatusToken.SUCCESS)
        assert result == "green"

        # Switch to light theme
        registry.set_current("light")
        result = registry.resolve(StatusToken.WARNING)
        assert result == "bright_yellow"  # Light theme uses bright_yellow

    def test_list_themes_sorted(self) -> None:
        """Test list_themes returns sorted list."""
        registry = ThemeRegistry()

        # Add custom theme
        custom_theme = Theme(
            name="zebra",  # Will be last alphabetically
            categories={CategoryToken.CAT_1: "purple"},
            hierarchies={HierarchyToken.PRIMARY: "bold"},
            statuses={StatusToken.SUCCESS: "lime"},
            emphases={EmphasisToken.STRONG: "bold"},
        )
        registry.register(custom_theme)

        themes = registry.list_themes()
        assert themes == sorted(themes)
        assert themes[-1] == "zebra"


class TestThemeLoader:
    """Tests for theme loading functionality."""

    def test_load_theme_from_yaml_success(self) -> None:
        """Test loading valid theme from YAML file."""
        theme_data = {
            "name": "test_theme",
            "categories": {
                token.value: f"color_{i}" for i, token in enumerate(CategoryToken)
            },
            "hierarchies": {
                token.value: f"style_{i}" for i, token in enumerate(HierarchyToken)
            },
            "statuses": {
                token.value: f"status_{i}" for i, token in enumerate(StatusToken)
            },
            "emphases": {
                token.value: f"emphasis_{i}" for i, token in enumerate(EmphasisToken)
            },
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(theme_data, f)
            temp_path = Path(f.name)

        try:
            theme = load_theme_from_yaml(temp_path)

            assert theme.name == "test_theme"
            assert theme.categories[CategoryToken.CAT_1] == "color_0"
            assert theme.hierarchies[HierarchyToken.PRIMARY] == "style_0"
            assert theme.statuses[StatusToken.SUCCESS] == "status_0"
            assert theme.emphases[EmphasisToken.STRONG] == "emphasis_0"
        finally:
            temp_path.unlink()

    def test_load_theme_file_not_found(self) -> None:
        """Test loading non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_theme_from_yaml(Path("/non/existent/file.yaml"))

    def test_load_theme_invalid_yaml(self) -> None:
        """Test loading invalid YAML raises ThemeLoadError."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("invalid: yaml: content: [")
            temp_path = Path(f.name)

        try:
            with pytest.raises(ThemeLoadError, match="Invalid YAML"):
                load_theme_from_yaml(temp_path)
        finally:
            temp_path.unlink()

    def test_load_theme_missing_name(self) -> None:
        """Test loading theme without name raises ThemeLoadError."""
        theme_data = {
            "categories": {token.value: "color" for token in CategoryToken},
            "hierarchies": {token.value: "style" for token in HierarchyToken},
            "statuses": {token.value: "status" for token in StatusToken},
            "emphases": {token.value: "emphasis" for token in EmphasisToken},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(theme_data, f)
            temp_path = Path(f.name)

        try:
            with pytest.raises(ThemeLoadError, match="missing required 'name' field"):
                load_theme_from_yaml(temp_path)
        finally:
            temp_path.unlink()

    def test_load_theme_missing_section(self) -> None:
        """Test loading theme with missing section raises ThemeLoadError."""
        theme_data = {
            "name": "incomplete",
            "categories": {token.value: "color" for token in CategoryToken},
            # Missing hierarchies, statuses, emphases
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(theme_data, f)
            temp_path = Path(f.name)

        try:
            with pytest.raises(ThemeLoadError, match="Missing required section"):
                load_theme_from_yaml(temp_path)
        finally:
            temp_path.unlink()

    def test_load_theme_missing_token(self) -> None:
        """Test loading theme with missing token raises ThemeLoadError."""
        theme_data = {
            "name": "incomplete",
            "categories": {
                CategoryToken.CAT_1.value: "color"
            },  # Missing other categories
            "hierarchies": {token.value: "style" for token in HierarchyToken},
            "statuses": {token.value: "status" for token in StatusToken},
            "emphases": {token.value: "emphasis" for token in EmphasisToken},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(theme_data, f)
            temp_path = Path(f.name)

        try:
            with pytest.raises(ThemeLoadError, match="Missing category token"):
                load_theme_from_yaml(temp_path)
        finally:
            temp_path.unlink()

    def test_load_user_themes_no_directory(self) -> None:
        """Test loading user themes when directory doesn't exist."""
        with patch("cli_patterns.config.theme_loader.Path.home") as mock_home:
            mock_home.return_value = Path("/non/existent/home")
            themes = load_user_themes()
            assert themes == []

    @patch.dict(os.environ, {"CLI_PATTERNS_THEME": "light"})
    def test_apply_theme_from_env_success(self) -> None:
        """Test applying theme from environment variable."""
        # Import global registry
        from cli_patterns.ui.design.registry import theme_registry

        # Ensure we start with dark theme
        theme_registry.set_current("dark")
        assert theme_registry.get_current().name == "dark"

        apply_theme_from_env()

        # Should switch to light theme
        assert theme_registry.get_current().name == "light"

        # Reset for other tests
        theme_registry.set_current("dark")

    @patch.dict(os.environ, {"CLI_PATTERNS_THEME": "nonexistent"})
    def test_apply_theme_from_env_invalid_theme(self, capsys) -> None:
        """Test applying invalid theme from environment variable."""
        from cli_patterns.ui.design.registry import theme_registry

        original_theme = theme_registry.get_current().name

        apply_theme_from_env()

        # Should stay with original theme
        assert theme_registry.get_current().name == original_theme

        # Should print warning
        captured = capsys.readouterr()
        assert (
            "Warning: Theme 'nonexistent' from CLI_PATTERNS_THEME not found"
            in captured.out
        )

    @patch.dict(os.environ, {}, clear=True)
    def test_apply_theme_from_env_no_env_var(self) -> None:
        """Test applying theme when no environment variable is set."""
        from cli_patterns.ui.design.registry import theme_registry

        original_theme = theme_registry.get_current().name

        apply_theme_from_env()

        # Should stay with original theme
        assert theme_registry.get_current().name == original_theme

    def test_theme_inheritance_with_extends(self) -> None:
        """Test theme inheritance using extends field."""
        # Import global registry
        from cli_patterns.ui.design.registry import theme_registry

        base_data = {
            "name": "base_test",
            "categories": {
                token.value: f"base_{token.value}" for token in CategoryToken
            },
            "hierarchies": {
                token.value: f"base_{token.value}" for token in HierarchyToken
            },
            "statuses": {token.value: f"base_{token.value}" for token in StatusToken},
            "emphases": {token.value: f"base_{token.value}" for token in EmphasisToken},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(base_data, f)
            base_path = Path(f.name)

        base_theme = load_theme_from_yaml(base_path)
        theme_registry.register(base_theme)

        # Now create child theme that extends base
        child_categories = {
            token.value: f"base_{token.value}" for token in CategoryToken
        }
        child_categories[CategoryToken.CAT_1.value] = (
            "child_override"  # Override one category
        )

        child_data = {
            "name": "child_test",
            "extends": "base_test",
            "categories": child_categories,
            "hierarchies": {
                token.value: f"base_{token.value}" for token in HierarchyToken
            },
            "statuses": {token.value: f"base_{token.value}" for token in StatusToken},
            "emphases": {token.value: f"base_{token.value}" for token in EmphasisToken},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(child_data, f)
            child_path = Path(f.name)

        try:
            child_theme = load_theme_from_yaml(child_path)

            # Check inheritance worked
            assert child_theme.name == "child_test"
            assert child_theme.extends == "base_test"
            assert (
                child_theme.categories[CategoryToken.CAT_1] == "child_override"
            )  # Overridden
            assert (
                child_theme.categories[CategoryToken.CAT_2] == "base_cat_2"
            )  # Inherited
        finally:
            base_path.unlink()
            child_path.unlink()

    def test_theme_inheritance_parent_not_found(self) -> None:
        """Test theme inheritance fails when parent doesn't exist."""
        child_data = {
            "name": "orphan",
            "extends": "nonexistent_parent",
            "categories": {token.value: "value" for token in CategoryToken},
            "hierarchies": {token.value: "value" for token in HierarchyToken},
            "statuses": {token.value: "value" for token in StatusToken},
            "emphases": {token.value: "value" for token in EmphasisToken},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(child_data, f)
            temp_path = Path(f.name)

        try:
            with pytest.raises(
                ThemeLoadError, match="Parent theme 'nonexistent_parent' not found"
            ):
                load_theme_from_yaml(temp_path)
        finally:
            temp_path.unlink()
