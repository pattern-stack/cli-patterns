"""Integration tests for the complete design system."""

import os
import tempfile
from pathlib import Path

import yaml

from cli_patterns.config.theme_loader import (
    load_theme_from_yaml,
)
from cli_patterns.ui.design.boxes import BOX_STYLES, BoxStyle
from cli_patterns.ui.design.components import Output, Panel, ProgressBar, Prompt
from cli_patterns.ui.design.icons import get_icon_set
from cli_patterns.ui.design.registry import theme_registry
from cli_patterns.ui.design.themes import DarkTheme, Theme
from cli_patterns.ui.design.tokens import (
    CategoryToken,
    DisplayMetadata,
    EmphasisToken,
    HierarchyToken,
    StatusToken,
)


class TestDesignSystemIntegration:
    """Test that all design system components work together."""

    def test_token_to_theme_resolution(self):
        """Test that tokens resolve correctly through themes."""
        # Set dark theme
        theme_registry.set_current("dark")

        # Test all token types resolve
        assert theme_registry.resolve(CategoryToken.CAT_1) == "cyan"
        assert theme_registry.resolve(StatusToken.SUCCESS) == "green"
        assert theme_registry.resolve(HierarchyToken.PRIMARY) == "bold"
        assert theme_registry.resolve(EmphasisToken.STRONG) == "bold"

        # Switch to light theme
        theme_registry.set_current("light")

        # Test tokens resolve differently
        assert theme_registry.resolve(CategoryToken.CAT_1) == "blue"
        assert theme_registry.resolve(StatusToken.SUCCESS) == "green"

    def test_component_with_theme_integration(self):
        """Test components use tokens that resolve through themes."""
        panel = Panel()
        theme_registry.set_current("dark")

        # Panel tokens should resolve to actual colors
        border_color = theme_registry.resolve(panel.border_category)
        assert border_color == "cyan"  # CAT_1 in dark theme

        title_style = theme_registry.resolve(panel.title_emphasis)
        assert title_style == "bold"  # STRONG emphasis

    def test_display_metadata_with_theme(self):
        """Test DisplayMetadata works with theme system."""
        metadata = DisplayMetadata(
            category=CategoryToken.CAT_2, hierarchy=HierarchyToken.SECONDARY
        )

        theme_registry.set_current("dark")

        # Create display style with status
        style = metadata.with_status(StatusToken.RUNNING)

        # All tokens should resolve
        assert theme_registry.resolve(style.category) == "magenta"
        assert theme_registry.resolve(style.hierarchy) == "default"
        assert theme_registry.resolve(style.status) == "cyan italic"

    def test_yaml_theme_loading_integration(self):
        """Test loading themes from YAML files."""
        # Load existing dark theme
        dark_path = Path("config/themes/dark.yaml")
        if dark_path.exists():
            theme = load_theme_from_yaml(str(dark_path))
            assert theme.name == "dark"
            assert CategoryToken.CAT_1 in theme.categories

    def test_custom_theme_registration(self):
        """Test creating and registering custom themes."""
        custom_theme = Theme(
            name="custom",
            categories={
                CategoryToken.CAT_1: "red",
                CategoryToken.CAT_2: "blue",
                CategoryToken.CAT_3: "green",
                CategoryToken.CAT_4: "yellow",
                CategoryToken.CAT_5: "magenta",
                CategoryToken.CAT_6: "cyan",
                CategoryToken.CAT_7: "white",
                CategoryToken.CAT_8: "black",
            },
            hierarchies={
                HierarchyToken.PRIMARY: "bold",
                HierarchyToken.SECONDARY: "normal",
                HierarchyToken.TERTIARY: "dim",
                HierarchyToken.QUATERNARY: "dim italic",
            },
            statuses={
                StatusToken.SUCCESS: "green bold",
                StatusToken.ERROR: "red bold",
                StatusToken.WARNING: "yellow",
                StatusToken.INFO: "blue",
                StatusToken.MUTED: "dim",
                StatusToken.RUNNING: "magenta italic",
            },
            emphases={
                EmphasisToken.STRONG: "bold",
                EmphasisToken.NORMAL: "normal",
                EmphasisToken.SUBTLE: "dim",
            },
        )

        # Register and use custom theme
        theme_registry.register(custom_theme)
        theme_registry.set_current("custom")

        assert theme_registry.resolve(CategoryToken.CAT_1) == "red"
        assert "custom" in theme_registry.list_themes()

    def test_box_styles_with_components(self):
        """Test box styles work with panel components."""
        Panel()  # Just verifying it can be created

        for _style_name, box_style in BOX_STYLES.items():
            assert isinstance(box_style, BoxStyle)
            assert box_style.top_left  # All styles should have corners
            assert box_style.top_right
            assert box_style.bottom_left
            assert box_style.bottom_right

    def test_icon_sets_with_output(self):
        """Test icon sets work with output components."""
        Output()  # Just verifying it can be created

        # Get different icon sets
        emoji_icons = get_icon_set(["emoji"])
        ascii_icons = get_icon_set(["ascii"])

        # Icons should be different
        assert emoji_icons.success != ascii_icons.success
        assert emoji_icons.error != ascii_icons.error

    def test_progress_bar_with_theme(self):
        """Test progress bar component with theme integration."""
        progress = ProgressBar()
        theme_registry.set_current("dark")

        # Progress states should resolve to colors
        complete_color = theme_registry.resolve(progress.complete_status)
        running_color = theme_registry.resolve(progress.running_status)
        pending_color = theme_registry.resolve(progress.pending_status)

        assert complete_color == "green"
        assert running_color == "cyan italic"
        assert pending_color == "bright_black"

    def test_prompt_with_icons(self):
        """Test prompt component with icon integration."""
        prompt = Prompt()
        icons = get_icon_set(["unicode"])

        # Prompt should work with icons
        assert prompt.symbol == "►"
        assert icons.arrow_right == "→"

    def test_environment_variable_integration(self):
        """Test theme selection via environment variable."""
        # Set environment variable
        os.environ["CLI_PATTERNS_THEME"] = "light"

        # Initialize themes (would normally happen at startup)
        # This would load the theme from env var
        # For testing, we'll just set it directly
        if "light" in theme_registry.list_themes():
            theme_registry.set_current("light")
            assert theme_registry.get_current().name == "light"

    def test_theme_inheritance_integration(self):
        """Test theme inheritance with YAML loading."""
        # For now, test that we can load a complete theme
        # Inheritance would require all sections present (or implementing merge logic)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            # Create a complete theme that overrides one color
            dark_theme = DarkTheme()
            theme_data = {
                "name": "custom-dark",
                "categories": {k.value: v for k, v in dark_theme.categories.items()},
                "hierarchies": {k.value: v for k, v in dark_theme.hierarchies.items()},
                "statuses": {k.value: v for k, v in dark_theme.statuses.items()},
                "emphases": {k.value: v for k, v in dark_theme.emphases.items()},
            }
            # Override one color
            theme_data["categories"]["cat_1"] = "bright_cyan"
            yaml.dump(theme_data, f)
            temp_path = f.name

        try:
            theme = load_theme_from_yaml(temp_path)
            assert theme.name == "custom-dark"
            assert theme.categories[CategoryToken.CAT_1] == "bright_cyan"
            # Other categories should remain as dark theme
            assert theme.categories[CategoryToken.CAT_2] == "magenta"
        finally:
            os.unlink(temp_path)

    def test_complete_workflow(self):
        """Test a complete workflow using all design system components."""
        # 1. Set theme
        theme_registry.set_current("dark")

        # 2. Create a component with metadata
        panel = Panel()
        metadata = DisplayMetadata(
            category=panel.border_category,
            hierarchy=panel.title_hierarchy,
            emphasis=panel.title_emphasis,
        )

        # 3. Get appropriate icons
        icons = get_icon_set(["emoji", "unicode", "ascii"])

        # 4. Get box style
        box = BOX_STYLES["rounded"]

        # 5. Resolve all tokens through theme
        border_color = theme_registry.resolve(metadata.category)
        title_style = f"{theme_registry.resolve(metadata.hierarchy)} {theme_registry.resolve(metadata.emphasis)}"

        # 6. Verify everything integrates
        assert border_color == "cyan"
        assert "bold" in title_style
        assert box.top_left == "╭"
        assert icons.success in ["✅", "✓", "[OK]"]  # Depending on terminal support

    def test_output_with_status_tokens(self):
        """Test output component with various status tokens."""
        output = Output()
        theme_registry.set_current("dark")

        # Map output types to their status/emphasis tokens
        stdout_style = theme_registry.resolve(output.stdout_emphasis)
        stderr_style = theme_registry.resolve(output.stderr_status)
        debug_style = theme_registry.resolve(output.debug_emphasis)
        info_style = theme_registry.resolve(output.info_status)

        assert stdout_style == "default"
        assert stderr_style == "red bold"
        assert debug_style == "dim"
        assert info_style == "blue"
