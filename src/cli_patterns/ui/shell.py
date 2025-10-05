"""Interactive shell implementation using prompt_toolkit and Rich.

This module provides the main interactive shell that combines prompt_toolkit
for input handling and Rich for output display, all themed through our
design token system.
"""

from __future__ import annotations

import asyncio
import sys
from typing import Any, Callable, Optional, Union

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style as PromptStyle
from rich.table import Table

from ..config.theme_loader import initialize_themes
from ..core.models import SessionState
from ..execution.subprocess_executor import SubprocessExecutor
from .design.components import Prompt as PromptComponent
from .design.icons import get_icon_set
from .design.registry import theme_registry
from .design.tokens import CategoryToken, StatusToken
from .parser import (
    CommandMetadata,
    CommandRegistry,
    ParseError,
    ParseResult,
    ParserPipeline,
    ShellParser,
    TextParser,
)
from .rich_adapter import rich_adapter


class InteractiveShell:
    """Main interactive shell with themed input and output."""

    def __init__(self) -> None:
        """Initialize the interactive shell."""
        # Initialize themes first
        initialize_themes()

        # Setup Rich console for output
        self.console = rich_adapter.create_console()

        # Legacy command registry for backward compatibility
        self.commands: dict[str, Callable[..., Any]] = {}
        self._setup_builtin_commands()

        # New parser system
        self.parser_pipeline = ParserPipeline()
        self.parser_pipeline.add_parser(
            ShellParser(), priority=10
        )  # Higher priority for shell commands
        self.parser_pipeline.add_parser(TextParser(), priority=5)
        self.session_state = SessionState(parse_mode="interactive")
        self.command_registry = CommandRegistry()

        # Register builtin commands in new registry
        self._register_builtin_commands()

        # Prompt configuration
        self.prompt_component = PromptComponent()
        self.icons = get_icon_set(["unicode", "ascii"])

        # Session will be created when running
        self.session: Optional[PromptSession[str]] = None
        self.running = False

    def _setup_builtin_commands(self) -> None:
        """Register built-in shell commands (legacy)."""
        self.commands = {
            "help": self.cmd_help,
            "exit": self.cmd_exit,
            "quit": self.cmd_exit,
            "echo": self.cmd_echo,
            "theme": self.cmd_theme,
            "coverage": self.cmd_coverage,
            "test-parser": self.cmd_test_parser,
        }

    def _register_builtin_commands(self) -> None:
        """Register built-in commands in the new command registry."""
        command_data = [
            ("help", "Show this help message", [], self.cmd_help),
            ("exit", "Exit the shell", ["quit"], self.cmd_exit),
            ("echo", "Echo text with theme styling", [], self.cmd_echo_parsed),
            ("theme", "Switch theme (dark/light)", [], self.cmd_theme_parsed),
            ("coverage", "Show Rich component theming coverage", [], self.cmd_coverage),
            (
                "test-parser",
                "Test parser functionality with debug output",
                [],
                self.cmd_test_parser,
            ),
        ]

        for name, description, aliases, handler in command_data:
            try:
                self.command_registry.register(
                    CommandMetadata(
                        name=name,
                        description=description,
                        aliases=aliases,
                        category="builtin",
                        handler=handler,  # type: ignore[arg-type]
                    )
                )
            except ValueError as e:
                # Log but don't fail if there are conflicts
                print(f"Warning: Could not register command {name}: {e}")

    def _create_prompt_style(self) -> PromptStyle:
        """Create prompt_toolkit style from our theme tokens.

        Returns:
            PromptStyle object with mapped colors
        """
        current_theme = theme_registry.get_current()

        # Build style dictionary for prompt_toolkit
        style_dict = {
            # Prompt symbol
            "prompt": self._normalize_color(
                theme_registry.resolve(self.prompt_component.category)
            ),
            # Error messages
            "error": self._normalize_color(
                theme_registry.resolve(self.prompt_component.error_status)
            ),
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
        return HTML(f"<prompt>{symbol}</prompt> ")

    async def run(self) -> None:
        """Run the interactive shell asynchronously."""
        self.running = True

        # Show welcome screen
        await self._show_welcome()

        # Get all command names and aliases for completion
        completion_words = list(self.commands.keys())
        for cmd in self.command_registry.list_commands():
            completion_words.append(cmd.name)
            completion_words.extend(cmd.aliases or [])

        # Remove duplicates while preserving order
        completion_words = list(dict.fromkeys(completion_words))

        # Create prompt session with theme
        self.session = PromptSession[str](
            style=self._create_prompt_style(),
            completer=WordCompleter(completion_words),
            history=FileHistory(".cli_patterns_history"),
        )

        # Main command loop
        while self.running:
            try:
                # Get user input
                user_input = await self.session.prompt_async(self._get_prompt_message())

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
        """Process a user command using the new parser system.

        Args:
            user_input: The raw input from the user
        """
        if not user_input:
            return

        try:
            # Parse the input using the parser pipeline
            result = self.parser_pipeline.parse(user_input, self.session_state)

            # Add to command history
            self.session_state.command_history.append(user_input)

            if result.command == "!":
                # Execute shell command via SubprocessExecutor
                if result.shell_command:
                    executor = SubprocessExecutor(self.console)
                    await executor.run(result.shell_command)
                else:
                    self.console.print(
                        "[status.warning]No shell command provided[/status.warning]"
                    )
            else:
                # Look up command in new registry first
                cmd_meta = self.command_registry.get(result.command)
                if cmd_meta and cmd_meta.handler:
                    try:
                        # Call handler with parsed result
                        cmd_result = cmd_meta.handler(result)
                        # Handle async commands
                        if asyncio.iscoroutine(cmd_result):
                            await cmd_result
                    except Exception as e:
                        self.console.print(
                            f"[status.error]Command failed: {e}[/status.error]"
                        )

                # Fallback to legacy command handling
                elif result.command in self.commands:
                    try:
                        # Convert parsed args back to string for legacy handlers
                        args_str = " ".join(result.args) if result.args else ""
                        cmd_result = self.commands[result.command](args_str)
                        # Handle async commands
                        if asyncio.iscoroutine(cmd_result):
                            await cmd_result
                    except Exception as e:
                        self.console.print(
                            f"[status.error]Command failed: {e}[/status.error]"
                        )

                else:
                    # Show suggestions for unknown commands
                    suggestions = self.command_registry.get_suggestions(result.command)
                    if suggestions:
                        self.console.print(
                            f"[status.warning]Unknown command: {result.command}[/status.warning]"
                        )
                        self.console.print(
                            f"[dim]Did you mean: {', '.join(suggestions[:3])}?[/dim]"
                        )
                    else:
                        self.console.print(
                            f"[status.warning]Unknown command: {result.command}[/status.warning]"
                        )
                        self.console.print(
                            "[dim]Type 'help' for available commands[/dim]"
                        )

        except ParseError as e:
            self.console.print(f"[status.error]Parse error: {e.message}[/status.error]")
            if e.suggestions:
                self.console.print(
                    f"[dim]Suggestions: {', '.join(e.suggestions)}[/dim]"
                )
        except Exception as e:
            self.console.print(f"[status.error]Unexpected error: {e}[/status.error]")

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

            self.console.print(
                f"[status.success]✓ Switched to '{theme_name}' theme[/status.success]"
            )
        except KeyError:
            self.console.print(
                f"[status.error]Theme '{theme_name}' not found[/status.error]"
            )
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

    def cmd_echo_parsed(self, parse_result: ParseResult) -> None:
        """Echo text with theme styling using parsed arguments.

        Args:
            parse_result: ParseResult from the parser system
        """
        if not parse_result.args:
            self.console.print("[status.warning]Usage: echo <text>[/status.warning]")
            return

        # Demonstrate different styling options
        words = parse_result.args
        styled_parts = []
        categories = list(CategoryToken)

        for i, word in enumerate(words):
            cat = categories[i % len(categories)]
            color = theme_registry.resolve(cat)
            styled_parts.append(f"[{color}]{word}[/{color}]")

        self.console.print(" ".join(styled_parts))

    def cmd_theme_parsed(self, parse_result: ParseResult) -> None:
        """Switch the current theme using parsed arguments.

        Args:
            parse_result: ParseResult from the parser system
        """
        if not parse_result.args:
            # Show current theme and available themes
            current = theme_registry.get_current().name
            available = theme_registry.list_themes()

            self.console.print(f"[status.info]Current theme: {current}[/status.info]")
            self.console.print(f"[dim]Available themes: {', '.join(available)}[/dim]")
            return

        theme_name = parse_result.args[0].strip().lower()

        try:
            # Switch theme
            theme_registry.set_current(theme_name)

            # Refresh Rich console theme
            rich_adapter.refresh_theme()
            self.console = rich_adapter.create_console()

            # Update prompt session style
            if self.session:
                self.session.style = self._create_prompt_style()

            self.console.print(
                f"[status.success]✓ Switched to '{theme_name}' theme[/status.success]"
            )
        except KeyError:
            self.console.print(
                f"[status.error]Theme '{theme_name}' not found[/status.error]"
            )
            available = theme_registry.list_themes()
            self.console.print(f"[dim]Available themes: {', '.join(available)}[/dim]")

    def cmd_test_parser(
        self, parse_result: Union[ParseResult, str, None] = None
    ) -> None:
        """Test parser functionality with debug output.

        Args:
            parse_result: ParseResult from the parser system (for new style) or string for legacy
        """
        if isinstance(parse_result, str):
            # Legacy mode - convert to simple test
            test_input = parse_result.strip() if parse_result else "help --verbose -f"
        else:
            # New mode - use the parse result itself or a default test
            if parse_result and parse_result.args:
                test_input = " ".join(parse_result.args)
            else:
                test_input = "help --verbose -f"

        self.console.print(
            f"[cat.cat_1]Testing parser with input:[/cat.cat_1] '{test_input}'"
        )

        try:
            # Parse the test input
            result = self.parser_pipeline.parse(test_input, self.session_state)

            # Display parsing results
            table = Table(
                title="Parser Debug Output", show_header=True, header_style="bold"
            )
            table.add_column("Field", style="cat.cat_2")
            table.add_column("Value", style="cat.cat_7")

            table.add_row("Command", result.command)
            table.add_row("Arguments", str(result.args))
            table.add_row("Flags", str(sorted(result.flags)))
            table.add_row("Options", str(dict(result.options)))
            table.add_row("Raw Input", result.raw_input)

            if result.shell_command:
                table.add_row("Shell Command", result.shell_command)

            self.console.print(table)

            # Show command registry lookup
            cmd_meta = self.command_registry.get(result.command)
            if cmd_meta:
                self.console.print(
                    "\n[cat.cat_3]Command found in registry:[/cat.cat_3]"
                )
                self.console.print(f"  Name: {cmd_meta.name}")
                self.console.print(f"  Description: {cmd_meta.description}")
                if cmd_meta.aliases:
                    self.console.print(f"  Aliases: {', '.join(cmd_meta.aliases)}")
                self.console.print(f"  Category: {cmd_meta.category}")
            else:
                suggestions = self.command_registry.get_suggestions(result.command)
                if suggestions:
                    self.console.print(
                        "\n[cat.cat_6]Command not found. Suggestions:[/cat.cat_6]"
                    )
                    self.console.print(f"  {', '.join(suggestions[:5])}")

        except ParseError as e:
            self.console.print(f"[status.error]Parse Error:[/status.error] {e.message}")
            if e.suggestions:
                self.console.print(
                    f"[dim]Suggestions: {', '.join(e.suggestions)}[/dim]"
                )
        except Exception as e:
            self.console.print(f"[status.error]Unexpected Error:[/status.error] {e}")


def run_shell() -> None:
    """Synchronous entry point for the interactive shell."""
    shell = InteractiveShell()
    try:
        asyncio.run(shell.run())
    except KeyboardInterrupt:
        print("\nShell interrupted")
        sys.exit(0)
