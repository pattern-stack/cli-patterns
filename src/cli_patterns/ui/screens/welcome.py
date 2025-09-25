"""Welcome screen for the CLI Patterns interactive shell.

This module provides a beautiful welcome screen with ASCII art and
information about the current theme and available commands.
"""

from __future__ import annotations

from rich.align import Align
from rich.console import Console
from rich.text import Text

from ..design.registry import theme_registry
from ..design.tokens import CategoryToken
from ..rich_adapter import rich_adapter


class WelcomeScreen:
    """Welcome screen display for the interactive shell."""

    def __init__(self, console: Console, current_theme: str) -> None:
        """Initialize the welcome screen.

        Args:
            console: Rich console for output
            current_theme: Name of the current theme
        """
        self.console = console
        self.current_theme = current_theme

    def display(self) -> None:
        """Display the welcome screen."""
        # Create ASCII art banner
        ascii_art = self._create_ascii_art()

        # Create info text
        info = self._create_info_text()

        # Create the main panel
        panel = rich_adapter.panel(
            Align.center(ascii_art + "\n\n" + info),
            title="Welcome to CLI Patterns",
            box_style="rounded"
        )

        self.console.print(panel)
        self.console.print()

    def _create_ascii_art(self) -> Text:
        """Create the ASCII art banner.

        Returns:
            Styled ASCII art text
        """
        # Simple but elegant ASCII art
        art_lines = [
            "╔═══════════════════════════════════╗",
            "║   ╔═╗╦  ╦  ╔═╗╔═╗╔╦╗╔╦╗╔═╗╔═╗╔╗╔╔═╗║",
            "║   ║  ║  ║  ╠═╝╠═╣ ║  ║ ║╣ ╠╦╝║║║╚═╗║",
            "║   ╚═╝╩═╝╩  ╩  ╩ ╩ ╩  ╩ ╚═╝╩╚═╝╚╝╚═╝║",
            "╚═══════════════════════════════════╝",
        ]

        # Create styled text
        text = Text("\n".join(art_lines))
        text.stylize(theme_registry.resolve(CategoryToken.CAT_1))

        return text

    def _create_info_text(self) -> Text:
        """Create the information text.

        Returns:
            Styled information text
        """

        lines = []

        # Version and theme info
        lines.append("[cat.cat_2]Version 0.1.0[/cat.cat_2]")
        lines.append(f"[cat.cat_3]Theme: {self.current_theme}[/cat.cat_3]")
        lines.append("")

        # Quick start
        lines.append("[cat.cat_4]Quick Start:[/cat.cat_4]")
        lines.append("  • Type [cat.cat_1]help[/cat.cat_1] to see available commands")
        lines.append("  • Type [cat.cat_1]theme[/cat.cat_1] to switch themes")
        lines.append("  • Type [cat.cat_1]exit[/cat.cat_1] to quit")

        return Text.from_markup("\n".join(lines))
