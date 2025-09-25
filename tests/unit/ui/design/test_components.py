"""Tests for UI components and design elements."""

from cli_patterns.ui.design.boxes import (
    ASCII,
    BOX_STYLES,
    DOUBLE,
    HEAVY,
    ROUNDED,
)
from cli_patterns.ui.design.components import Output, Panel, ProgressBar, Prompt
from cli_patterns.ui.design.icons import (
    ASCII_ICONS,
    EMOJI_ICONS,
    ICON_SETS,
    NERD_FONT_ICONS,
    UNICODE_ICONS,
    get_icon_set,
)
from cli_patterns.ui.design.tokens import (
    CategoryToken,
    EmphasisToken,
    HierarchyToken,
    StatusToken,
)


class TestPanelComponent:
    """Tests for Panel component default values."""

    def test_panel_default_values(self):
        """Test Panel has expected default token mappings."""
        panel = Panel()

        assert panel.border_category == CategoryToken.CAT_1
        assert panel.title_hierarchy == HierarchyToken.PRIMARY
        assert panel.title_emphasis == EmphasisToken.STRONG
        assert panel.content_emphasis == EmphasisToken.NORMAL

    def test_panel_custom_values(self):
        """Test Panel can be customized with different tokens."""
        panel = Panel(
            border_category=CategoryToken.CAT_3,
            title_hierarchy=HierarchyToken.SECONDARY,
            title_emphasis=EmphasisToken.NORMAL,
            content_emphasis=EmphasisToken.SUBTLE,
        )

        assert panel.border_category == CategoryToken.CAT_3
        assert panel.title_hierarchy == HierarchyToken.SECONDARY
        assert panel.title_emphasis == EmphasisToken.NORMAL
        assert panel.content_emphasis == EmphasisToken.SUBTLE


class TestProgressBarComponent:
    """Tests for ProgressBar component token mappings."""

    def test_progressbar_default_values(self):
        """Test ProgressBar has expected default token mappings."""
        progress = ProgressBar()

        assert progress.complete_status == StatusToken.SUCCESS
        assert progress.running_status == StatusToken.RUNNING
        assert progress.pending_status == StatusToken.MUTED
        assert progress.bar_category == CategoryToken.CAT_2

    def test_progressbar_custom_values(self):
        """Test ProgressBar can be customized with different tokens."""
        progress = ProgressBar(
            complete_status=StatusToken.INFO,
            running_status=StatusToken.WARNING,
            pending_status=StatusToken.ERROR,
            bar_category=CategoryToken.CAT_5,
        )

        assert progress.complete_status == StatusToken.INFO
        assert progress.running_status == StatusToken.WARNING
        assert progress.pending_status == StatusToken.ERROR
        assert progress.bar_category == CategoryToken.CAT_5


class TestPromptComponent:
    """Tests for Prompt component configurations."""

    def test_prompt_default_values(self):
        """Test Prompt has expected default token mappings."""
        prompt = Prompt()

        assert prompt.symbol == "►"
        assert prompt.category == CategoryToken.CAT_1
        assert prompt.emphasis == EmphasisToken.NORMAL
        assert prompt.error_status == StatusToken.ERROR

    def test_prompt_custom_values(self):
        """Test Prompt can be customized with different tokens."""
        prompt = Prompt(
            symbol="$",
            category=CategoryToken.CAT_4,
            emphasis=EmphasisToken.STRONG,
            error_status=StatusToken.WARNING,
        )

        assert prompt.symbol == "$"
        assert prompt.category == CategoryToken.CAT_4
        assert prompt.emphasis == EmphasisToken.STRONG
        assert prompt.error_status == StatusToken.WARNING


class TestOutputComponent:
    """Tests for Output component formatting tokens."""

    def test_output_default_values(self):
        """Test Output has expected default token mappings."""
        output = Output()

        assert output.stdout_emphasis == EmphasisToken.NORMAL
        assert output.stderr_status == StatusToken.ERROR
        assert output.debug_emphasis == EmphasisToken.SUBTLE
        assert output.info_status == StatusToken.INFO

    def test_output_custom_values(self):
        """Test Output can be customized with different tokens."""
        output = Output(
            stdout_emphasis=EmphasisToken.STRONG,
            stderr_status=StatusToken.WARNING,
            debug_emphasis=EmphasisToken.NORMAL,
            info_status=StatusToken.SUCCESS,
        )

        assert output.stdout_emphasis == EmphasisToken.STRONG
        assert output.stderr_status == StatusToken.WARNING
        assert output.debug_emphasis == EmphasisToken.NORMAL
        assert output.info_status == StatusToken.SUCCESS


class TestBoxStyles:
    """Tests for box drawing styles."""

    def test_box_style_has_all_characters(self):
        """Test BoxStyle dataclass has all required character fields."""
        # Test with ROUNDED style
        assert hasattr(ROUNDED, "top")
        assert hasattr(ROUNDED, "bottom")
        assert hasattr(ROUNDED, "left")
        assert hasattr(ROUNDED, "right")
        assert hasattr(ROUNDED, "top_left")
        assert hasattr(ROUNDED, "top_right")
        assert hasattr(ROUNDED, "bottom_left")
        assert hasattr(ROUNDED, "bottom_right")
        assert hasattr(ROUNDED, "horizontal_down")
        assert hasattr(ROUNDED, "horizontal_up")
        assert hasattr(ROUNDED, "vertical_right")
        assert hasattr(ROUNDED, "vertical_left")
        assert hasattr(ROUNDED, "cross")

    def test_rounded_style_characters(self):
        """Test ROUNDED style has expected Unicode characters."""
        assert ROUNDED.top == "─"
        assert ROUNDED.bottom == "─"
        assert ROUNDED.left == "│"
        assert ROUNDED.right == "│"
        assert ROUNDED.top_left == "╭"
        assert ROUNDED.top_right == "╮"
        assert ROUNDED.bottom_left == "╰"
        assert ROUNDED.bottom_right == "╯"

    def test_heavy_style_characters(self):
        """Test HEAVY style has expected Unicode characters."""
        assert HEAVY.top == "━"
        assert HEAVY.bottom == "━"
        assert HEAVY.left == "┃"
        assert HEAVY.right == "┃"
        assert HEAVY.top_left == "┏"
        assert HEAVY.top_right == "┓"
        assert HEAVY.bottom_left == "┗"
        assert HEAVY.bottom_right == "┛"

    def test_ascii_style_characters(self):
        """Test ASCII style has expected ASCII characters."""
        assert ASCII.top == "-"
        assert ASCII.bottom == "-"
        assert ASCII.left == "|"
        assert ASCII.right == "|"
        assert ASCII.top_left == "+"
        assert ASCII.top_right == "+"
        assert ASCII.bottom_left == "+"
        assert ASCII.bottom_right == "+"

    def test_double_style_characters(self):
        """Test DOUBLE style has expected Unicode characters."""
        assert DOUBLE.top == "═"
        assert DOUBLE.bottom == "═"
        assert DOUBLE.left == "║"
        assert DOUBLE.right == "║"
        assert DOUBLE.top_left == "╔"
        assert DOUBLE.top_right == "╗"
        assert DOUBLE.bottom_left == "╚"
        assert DOUBLE.bottom_right == "╝"

    def test_box_styles_registry(self):
        """Test BOX_STYLES contains all defined styles."""
        assert "rounded" in BOX_STYLES
        assert "heavy" in BOX_STYLES
        assert "ascii" in BOX_STYLES
        assert "double" in BOX_STYLES

        assert BOX_STYLES["rounded"] is ROUNDED
        assert BOX_STYLES["heavy"] is HEAVY
        assert BOX_STYLES["ascii"] is ASCII
        assert BOX_STYLES["double"] is DOUBLE

    def test_all_box_styles_complete(self):
        """Test all box styles have complete character sets."""
        required_fields = [
            "top",
            "bottom",
            "left",
            "right",
            "top_left",
            "top_right",
            "bottom_left",
            "bottom_right",
            "horizontal_down",
            "horizontal_up",
            "vertical_right",
            "vertical_left",
            "cross",
        ]

        for style_name, style in BOX_STYLES.items():
            for field in required_fields:
                assert hasattr(
                    style, field
                ), f"Style '{style_name}' missing field '{field}'"
                assert getattr(
                    style, field
                ), f"Style '{style_name}' has empty field '{field}'"


class TestIconSets:
    """Tests for icon sets and fallback logic."""

    def test_icon_set_has_all_icons(self):
        """Test IconSet dataclass has all required icon fields."""
        # Test with EMOJI_ICONS
        required_fields = [
            "success",
            "error",
            "warning",
            "info",
            "running",
            "folder",
            "file",
            "arrow_right",
            "arrow_down",
            "check",
            "cross",
            "bullet",
        ]

        for field in required_fields:
            assert hasattr(EMOJI_ICONS, field)

    def test_emoji_icons(self):
        """Test EMOJI_ICONS has expected emoji characters."""
        assert EMOJI_ICONS.success == "✅"
        assert EMOJI_ICONS.error == "❌"
        assert EMOJI_ICONS.warning == "⚠️"
        assert EMOJI_ICONS.info == "ℹ️"
        assert EMOJI_ICONS.running == "🔄"
        assert EMOJI_ICONS.folder == "📁"
        assert EMOJI_ICONS.file == "📄"

    def test_unicode_icons(self):
        """Test UNICODE_ICONS has expected Unicode characters."""
        assert UNICODE_ICONS.success == "✓"
        assert UNICODE_ICONS.error == "✗"
        assert UNICODE_ICONS.warning == "⚠"
        assert UNICODE_ICONS.info == "ⓘ"
        assert UNICODE_ICONS.running == "◉"
        assert UNICODE_ICONS.folder == "▸"
        assert UNICODE_ICONS.file == "▪"

    def test_ascii_icons(self):
        """Test ASCII_ICONS has expected ASCII characters."""
        assert ASCII_ICONS.success == "[OK]"
        assert ASCII_ICONS.error == "[X]"
        assert ASCII_ICONS.warning == "[!]"
        assert ASCII_ICONS.info == "[i]"
        assert ASCII_ICONS.running == "[*]"
        assert ASCII_ICONS.folder == ">"
        assert ASCII_ICONS.file == "-"

    def test_nerd_font_icons(self):
        """Test NERD_FONT_ICONS has Nerd Font characters."""
        # Test that nerd font icons are not empty (they should contain special chars)
        assert NERD_FONT_ICONS.success == ""
        assert NERD_FONT_ICONS.error == ""
        assert NERD_FONT_ICONS.warning == ""
        assert NERD_FONT_ICONS.info == ""

    def test_icon_sets_registry(self):
        """Test ICON_SETS contains all defined icon sets."""
        assert "emoji" in ICON_SETS
        assert "unicode" in ICON_SETS
        assert "ascii" in ICON_SETS
        assert "nerd" in ICON_SETS

        assert ICON_SETS["emoji"] is EMOJI_ICONS
        assert ICON_SETS["unicode"] is UNICODE_ICONS
        assert ICON_SETS["ascii"] is ASCII_ICONS
        assert ICON_SETS["nerd"] is NERD_FONT_ICONS

    def test_all_icon_sets_complete(self):
        """Test all icon sets have complete icon mappings."""
        required_fields = [
            "success",
            "error",
            "warning",
            "info",
            "running",
            "folder",
            "file",
            "arrow_right",
            "arrow_down",
            "check",
            "cross",
            "bullet",
        ]

        for set_name, icon_set in ICON_SETS.items():
            for field in required_fields:
                assert hasattr(
                    icon_set, field
                ), f"Icon set '{set_name}' missing field '{field}'"
                # Note: Don't check for non-empty values as some icon sets might use empty strings


class TestGetIconSetFunction:
    """Tests for get_icon_set fallback logic."""

    def test_get_icon_set_default_preference(self):
        """Test get_icon_set with default preference order."""
        result = get_icon_set()
        # Default should return emoji as first preference
        assert result is EMOJI_ICONS

    def test_get_icon_set_with_custom_preference(self):
        """Test get_icon_set with custom preference order."""
        result = get_icon_set(["ascii", "unicode"])
        assert result is ASCII_ICONS

    def test_get_icon_set_with_single_preference(self):
        """Test get_icon_set with single preference."""
        result = get_icon_set(["nerd"])
        assert result is NERD_FONT_ICONS

    def test_get_icon_set_with_invalid_preference(self):
        """Test get_icon_set with invalid preference falls back to ASCII."""
        result = get_icon_set(["invalid", "nonexistent"])
        assert result is ASCII_ICONS

    def test_get_icon_set_with_mixed_preferences(self):
        """Test get_icon_set with mix of valid and invalid preferences."""
        result = get_icon_set(["invalid", "unicode", "ascii"])
        assert result is UNICODE_ICONS

    def test_get_icon_set_with_empty_preferences(self):
        """Test get_icon_set with empty preference list."""
        result = get_icon_set([])
        assert result is ASCII_ICONS

    def test_get_icon_set_preferences_order_matters(self):
        """Test get_icon_set respects preference order."""
        result1 = get_icon_set(["unicode", "emoji"])
        result2 = get_icon_set(["emoji", "unicode"])

        assert result1 is UNICODE_ICONS
        assert result2 is EMOJI_ICONS
