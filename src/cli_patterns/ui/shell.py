"""Interactive shell implementation using prompt_toolkit and Rich.

This module provides the main interactive shell that combines prompt_toolkit
for input handling and Rich for output display, all themed through our
design token system.
"""

from __future__ import annotations

import asyncio
import sys
from typing import Callable, Optional

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style as PromptStyle
from rich.table import Table

from ..config.theme_loader import initialize_themes
from .design.components import Prompt as PromptComponent
from .design.icons import get_icon_set
from .design.registry import theme_registry
from .design.tokens import CategoryToken, StatusToken
from .rich_adapter import rich_adapter


class InteractiveShell:
    """Main interactive shell with themed input and output."""

    def __init__(self) -> None:
        """Initialize the interactive shell."""
        # Initialize themes first
        initialize_themes()

        # Setup Rich console for output
        self.console = rich_adapter.create_console()

        # Command registry
        self.commands: dict[str, Callable] = {}
        self._setup_builtin_commands()

        # Prompt configuration
        self.prompt_component = PromptComponent()
        self.icons = get_icon_set(["unicode", "ascii"])

        # Session will be created when running
        self.session: Optional[PromptSession] = None
        self.running = False

    def _setup_builtin_commands(self) -> None:
        """Register built-in shell commands."""
        self.commands = {
            "help": self.cmd_help,
            "exit": self.cmd_exit,
            "quit": self.cmd_exit,
            "echo": self.cmd_echo,
            "theme": self.cmd_theme,
            "coverage": self.cmd_coverage,
        }

    def _create_prompt_style(self) -> PromptStyle:
        """Create prompt_toolkit style from our theme tokens.

        Returns:
            PromptStyle object with mapped colors
        """
        current_theme = theme_registry.get_current()

        # Build style dictionary for prompt_toolkit
        style_dict = {
            # Prompt symbol
            "prompt": self._normalize_color(theme_registry.resolve(self.prompt_component.category)),
            # Error messages
            "error": self._normalize_color(theme_registry.resolve(self.prompt_component.error_status)),
            # Input text
            "": "default",
        }

        # Add category colors
        for cat in CategoryToken:
            color = self._normalize_color(current_theme.categories[cat])
            style_dict[f"cat-{cat.value}"] = color

        # Add status colors
        for status in StatusToken:
            style_str = current_theme.statuses[status]
            # Normalize color in style string
            parts = style_str.split()
            if parts:
                parts[0] = self._normalize_color(parts[0])
                style_str = " ".join(parts)
            style_dict[f"status-{status.value}"] = style_str

        return PromptStyle.from_dict(style_dict)

    def _normalize_color(self, color: str) -> str:
        """Normalize color names to prompt_toolkit compatible format.

        Args:
            color: Color name to normalize

        Returns:
            prompt_toolkit compatible color name
        """
        # Map problematic color names to prompt_toolkit compatible ones
        color_map = {
            "bright_black": "#808080",  # Use hex for grey
            "grey62": "#808080",
            "grey50": "#808080",
        }
        return color_map.get(color, color)

    def _get_prompt_message(self) -> HTML:
        """Get the prompt message with styling.

        Returns:
            Formatted prompt message
        """
        # prompt_color = theme_registry.resolve(self.prompt_component.category)  # For future use
        symbol = self.prompt_component.symbol
        return HTML(f'<prompt>{symbol}</prompt> ')

    async def run(self) -> None:
        """Run the interactive shell asynchronously."""
        self.running = True

        # Show welcome screen
        await self._show_welcome()

        # Create prompt session with theme
        self.session = PromptSession(
            style=self._create_prompt_style(),
            completer=WordCompleter(list(self.commands.keys())),
            history=FileHistory(".cli_patterns_history"),
        )

        # Main command loop
        while self.running:
            try:
                # Get user input
                user_input = await self.session.prompt_async(
                    self._get_prompt_message()
                )

                # Process command
                await self._process_command(user_input.strip())

            except (EOFError, KeyboardInterrupt):
                # Handle Ctrl+D and Ctrl+C gracefully
                self.console.print("\n[dim]Goodbye![/dim]")
                break
            except Exception as e:
                self.console.print(f"[status.error]Error: {e}[/status.error]")

    async def _show_welcome(self) -> None:
        """Display the welcome screen."""
        # Defer to welcome screen module
        from .screens.welcome import WelcomeScreen
        welcome = WelcomeScreen(self.console, theme_registry.get_current().name)
        welcome.display()

    async def _process_command(self, user_input: str) -> None:
        """Process a user command.

        Args:
            user_input: The raw input from the user
        """
        if not user_input:
            return

        # Parse command and arguments
        parts = user_input.split(maxsplit=1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        # Execute command
        if command in self.commands:
            try:
                result = self.commands[command](args)
                # Handle async commands
                if asyncio.iscoroutine(result):
                    await result
            except Exception as e:
                self.console.print(f"[status.error]Command failed: {e}[/status.error]")
        else:
            self.console.print(f"[status.warning]Unknown command: {command}[/status.warning]")
            self.console.print("[dim]Type 'help' for available commands[/dim]")

    def cmd_help(self, args: str) -> None:
        """Display help information.

        Args:
            args: Command arguments (unused)
        """
        table = Table(title="Available Commands", show_header=True, header_style="bold")
        table.add_column("Command", style="cat.cat_1")
        table.add_column("Description", style="cat.cat_7")

        command_help = {
            "help": "Show this help message",
            "exit": "Exit the shell",
            "quit": "Exit the shell (alias for exit)",
            "echo <text>": "Echo text with theme styling",
            "theme <name>": "Switch theme (dark/light)",
            "coverage": "Show Rich component theming coverage",
        }

        for cmd, desc in command_help.items():
            table.add_row(cmd, desc)

        self.console.print(table)

    def cmd_exit(self, args: str) -> None:
        """Exit the shell.

        Args:
            args: Command arguments (unused)
        """
        self.running = False
        self.console.print("[status.success]Goodbye![/status.success]")

    def cmd_echo(self, args: str) -> None:
        """Echo text with theme styling.

        Args:
            args: Text to echo
        """
        if not args:
            self.console.print("[status.warning]Usage: echo <text>[/status.warning]")
            return

        # Demonstrate different styling options
        # text = Text(args)  # For future use

        # Apply category styling to different words
        words = args.split()
        styled_parts = []
        categories = list(CategoryToken)

        for i, word in enumerate(words):
            cat = categories[i % len(categories)]
            color = theme_registry.resolve(cat)
            styled_parts.append(f"[{color}]{word}[/{color}]")

        self.console.print(" ".join(styled_parts))

    def cmd_theme(self, args: str) -> None:
        """Switch the current theme.

        Args:
            args: Theme name to switch to
        """
        if not args:
            # Show current theme and available themes
            current = theme_registry.get_current().name
            available = theme_registry.list_themes()

            self.console.print(f"[status.info]Current theme: {current}[/status.info]")
            self.console.print(f"[dim]Available themes: {', '.join(available)}[/dim]")
            return

        theme_name = args.strip().lower()

        try:
            # Switch theme
            theme_registry.set_current(theme_name)

            # Refresh Rich console theme
            rich_adapter.refresh_theme()
            self.console = rich_adapter.create_console()

            # Update prompt session style
            if self.session:
                self.session.style = self._create_prompt_style()

            self.console.print(f"[status.success]✓ Switched to '{theme_name}' theme[/status.success]")
        except KeyError:
            self.console.print(f"[status.error]Theme '{theme_name}' not found[/status.error]")
            available = theme_registry.list_themes()
            self.console.print(f"[dim]Available themes: {', '.join(available)}[/dim]")

    def cmd_coverage(self, args: str) -> None:
        """Show Rich component theming coverage.

        Args:
            args: Command arguments (unused)
        """
        coverage = rich_adapter.get_coverage_report()

        table = Table(title="Rich Component Coverage", show_header=True)
        table.add_column("Metric", style="cat.cat_1")
        table.add_column("Value", style="cat.cat_2")

        table.add_row("Themed Components", str(len(coverage["themed_components"])))
        table.add_row("Unthemed Components", str(len(coverage["unthemed_components"])))
        table.add_row("Coverage", f"{coverage['coverage_percentage']:.1f}%")

        self.console.print(table)

        if coverage["themed_components"]:
            self.console.print("\n[cat.cat_3]Themed components:[/cat.cat_3]")
            for comp in coverage["themed_components"]:
                usage = coverage["usage_stats"][comp]
                self.console.print(f"  • {comp} (used {usage}x)")

        if coverage["unthemed_components"]:
            self.console.print("\n[cat.cat_6]Unthemed components:[/cat.cat_6]")
            for comp in coverage["unthemed_components"]:
                self.console.print(f"  • {comp}")


def run_shell() -> None:
    """Synchronous entry point for the interactive shell."""
    shell = InteractiveShell()
    try:
        asyncio.run(shell.run())
    except KeyboardInterrupt:
        print("\nShell interrupted")
        sys.exit(0)
