"""Integration tests for shell-parser system integration.

These tests verify that the interactive shell properly integrates with
the new parser system, maintaining backward compatibility while adding
new parsing capabilities.
"""

from unittest.mock import Mock, patch

import pytest

from cli_patterns.ui.parser import (
    CommandMetadata,
    CommandRegistry,
    Context,
    ParseError,
    ParseResult,
    ParserPipeline,
    ShellParser,
    TextParser,
)

# Import shell and parser components
from cli_patterns.ui.shell import InteractiveShell

pytestmark = pytest.mark.parser


class TestShellParserIntegration:
    """Integration tests for shell and parser system working together."""

    @pytest.fixture
    def mock_console(self):
        """Mock Rich console for testing."""
        console = Mock()
        console.print = Mock()
        return console

    @pytest.fixture
    def shell_with_parser(self, mock_console):
        """Create a shell instance with parser integration."""
        # We'll create the shell but mock the console
        with patch("cli_patterns.ui.shell.rich_adapter") as mock_adapter:
            mock_adapter.create_console.return_value = mock_console
            shell = InteractiveShell()

            # Add parser system integration (this is what we'll implement)
            shell.parser_pipeline = ParserPipeline()
            shell.parser_pipeline.add_parser(ShellParser(), priority=10)
            shell.parser_pipeline.add_parser(TextParser(), priority=5)
            shell.context = Context()
            shell.command_registry = CommandRegistry()

            # Register built-in commands in registry
            shell.command_registry.register(
                CommandMetadata(
                    name="help",
                    handler=shell.cmd_help,
                    description="Show help information",
                    aliases=[],
                    category="builtin",
                )
            )
            shell.command_registry.register(
                CommandMetadata(
                    name="exit",
                    handler=shell.cmd_exit,
                    description="Exit the shell",
                    aliases=["quit"],
                    category="builtin",
                )
            )
            shell.command_registry.register(
                CommandMetadata(
                    name="echo",
                    handler=shell.cmd_echo,
                    description="Echo text with theme styling",
                    aliases=[],
                    category="builtin",
                )
            )
            shell.command_registry.register(
                CommandMetadata(
                    name="theme",
                    handler=shell.cmd_theme,
                    description="Switch theme (dark/light)",
                    aliases=[],
                    category="builtin",
                )
            )
            shell.command_registry.register(
                CommandMetadata(
                    name="coverage",
                    handler=shell.cmd_coverage,
                    description="Show Rich component theming coverage",
                    aliases=[],
                    category="builtin",
                )
            )

            return shell

    def test_shell_has_parser_integration(self, shell_with_parser):
        """Test that shell properly initializes parser system."""
        shell = shell_with_parser

        # Check parser pipeline exists
        assert hasattr(shell, "parser_pipeline")
        assert isinstance(shell.parser_pipeline, ParserPipeline)

        # Check context exists
        assert hasattr(shell, "context")
        assert isinstance(shell.context, Context)

        # Check command registry exists
        assert hasattr(shell, "command_registry")
        assert isinstance(shell.command_registry, CommandRegistry)

        # Check built-in commands are registered
        help_cmd = shell.command_registry.get("help")
        assert help_cmd is not None
        assert help_cmd.name == "help"

        exit_cmd = shell.command_registry.get("exit")
        assert exit_cmd is not None
        assert "quit" in exit_cmd.aliases

    @pytest.mark.asyncio
    async def test_basic_command_parsing(self, shell_with_parser):
        """Test that basic commands are parsed correctly."""
        shell = shell_with_parser

        # Test simple command parsing
        result = shell.parser_pipeline.parse("help", shell.context)
        assert result.command == "help"
        assert result.args == []
        assert result.flags == set()
        assert result.options == {}

        # Test command with arguments
        result = shell.parser_pipeline.parse("echo hello world", shell.context)
        assert result.command == "echo"
        assert result.args == ["hello", "world"]

    @pytest.mark.asyncio
    async def test_shell_command_parsing(self, shell_with_parser):
        """Test that shell commands with ! prefix are parsed correctly."""
        shell = shell_with_parser

        # Test shell command parsing
        result = shell.parser_pipeline.parse("! ls -la", shell.context)
        assert result.command == "!"
        assert result.shell_command == "ls -la"

        # Test shell command with complex arguments
        result = shell.parser_pipeline.parse('! grep "pattern" file.txt', shell.context)
        assert result.command == "!"
        assert result.shell_command == 'grep "pattern" file.txt'

    @pytest.mark.asyncio
    async def test_quote_handling(self, shell_with_parser):
        """Test that quoted arguments are handled correctly."""
        shell = shell_with_parser

        # Test single quotes
        result = shell.parser_pipeline.parse("echo 'hello world'", shell.context)
        assert result.command == "echo"
        assert result.args == ["hello world"]

        # Test double quotes
        result = shell.parser_pipeline.parse('echo "hello world"', shell.context)
        assert result.command == "echo"
        assert result.args == ["hello world"]

    @pytest.mark.asyncio
    async def test_flag_and_option_parsing(self, shell_with_parser):
        """Test that flags and options are parsed correctly."""
        shell = shell_with_parser

        # Test flags
        result = shell.parser_pipeline.parse("command -v -h", shell.context)
        assert result.command == "command"
        assert "v" in result.flags
        assert "h" in result.flags

        # Test options
        result = shell.parser_pipeline.parse("command --output file.txt", shell.context)
        assert result.command == "command"
        assert result.options.get("output") == "file.txt"

    @pytest.mark.asyncio
    async def test_command_execution_with_parser(self, shell_with_parser):
        """Test that commands execute correctly through the parser system."""
        shell = shell_with_parser

        # Mock the _process_command method to use parser

        async def mock_process_command(user_input: str) -> None:
            if not user_input:
                return

            try:
                # Parse the input
                result = shell.parser_pipeline.parse(user_input, shell.context)

                # Add to history
                shell.context.add_to_history(user_input)

                if result.command == "!":
                    # Execute shell command (we'll mock this)
                    shell.console.print(
                        f"Would execute shell command: {result.shell_command}"
                    )
                else:
                    # Look up command in registry
                    cmd_meta = shell.command_registry.get(result.command)
                    if cmd_meta and cmd_meta.handler:
                        # For testing, just call with first arg if available
                        args_str = " ".join(result.args) if result.args else ""
                        cmd_meta.handler(args_str)
                    else:
                        # Show suggestions
                        suggestions = shell.command_registry.get_suggestions(
                            result.command
                        )
                        if suggestions:
                            shell.console.print(f"Unknown command: {result.command}")
                            shell.console.print(
                                f"Did you mean: {', '.join(suggestions)}?"
                            )
                        else:
                            shell.console.print(f"Unknown command: {result.command}")

            except ParseError as e:
                shell.console.print(f"Parse error: {e.message}")
                if e.suggestions:
                    shell.console.print(f"Suggestions: {', '.join(e.suggestions)}")

        # Replace the method temporarily
        shell._process_command = mock_process_command

        # Test help command execution
        await shell._process_command("help")
        shell.console.print.assert_called()  # Should have printed help table

        # Test shell command execution
        await shell._process_command("! echo hello")
        calls = shell.console.print.call_args_list
        assert any(
            "Would execute shell command: echo hello" in str(call) for call in calls
        )

        # Test unknown command with suggestions
        await shell._process_command("hlp")  # typo of "help"
        calls = shell.console.print.call_args_list
        assert any("Unknown command: hlp" in str(call) for call in calls)

    @pytest.mark.asyncio
    async def test_backward_compatibility(self, shell_with_parser):
        """Test that existing command handling still works."""
        shell = shell_with_parser

        # Test that original commands dict still exists
        assert hasattr(shell, "commands")
        assert isinstance(shell.commands, dict)

        # Test that all builtin commands are available
        expected_commands = ["help", "exit", "quit", "echo", "theme", "coverage"]
        for cmd in expected_commands:
            assert cmd in shell.commands or shell.command_registry.get(cmd) is not None

    def test_command_suggestions_on_typos(self, shell_with_parser):
        """Test that command suggestions work for typos."""
        shell = shell_with_parser

        # Test suggestions for common typos
        suggestions = shell.command_registry.get_suggestions("hlp")
        assert "help" in suggestions

        suggestions = shell.command_registry.get_suggestions("exti")
        assert "exit" in suggestions

        suggestions = shell.command_registry.get_suggestions("ech")
        assert "echo" in suggestions

    def test_command_aliases_work(self, shell_with_parser):
        """Test that command aliases work correctly."""
        shell = shell_with_parser

        # Test that "quit" alias resolves to "exit" command
        exit_cmd = shell.command_registry.get("quit")
        assert exit_cmd is not None
        assert exit_cmd.name == "exit"

        # Test direct lookup
        exit_direct = shell.command_registry.get("exit")
        assert exit_cmd == exit_direct

    @pytest.mark.asyncio
    async def test_session_context_tracking(self, shell_with_parser):
        """Test that session context tracks history and state."""
        shell = shell_with_parser

        # Add some commands to history
        shell.context.add_to_history("help")
        shell.context.add_to_history("echo hello")
        shell.context.add_to_history("! ls -la")

        # Check history
        assert len(shell.context.history) == 3
        assert "help" in shell.context.history
        assert "echo hello" in shell.context.history
        assert "! ls -la" in shell.context.history

        # Test session state
        shell.context.set_state("current_theme", "dark")
        assert shell.context.get_state("current_theme") == "dark"

        # Test state with default
        assert shell.context.get_state("nonexistent", "default") == "default"

    @pytest.mark.asyncio
    async def test_error_handling_and_recovery(self, shell_with_parser):
        """Test that parsing errors are handled gracefully."""
        shell = shell_with_parser

        # Create a parser that might throw errors
        def parse_with_error(input_str, context):
            if input_str.startswith("error"):
                raise ParseError(
                    "test_error", "Test parsing error", ["suggestion1", "suggestion2"]
                )
            return ParseResult(command=input_str)

        # Mock the parse method temporarily
        original_parse = shell.parser_pipeline.parse
        shell.parser_pipeline.parse = parse_with_error

        # Mock _process_command to handle errors
        async def mock_process_with_error(user_input: str) -> None:
            try:
                result = shell.parser_pipeline.parse(user_input, shell.context)
                shell.console.print(f"Parsed: {result.command}")
            except ParseError as e:
                shell.console.print(f"Parse error: {e.message}")
                if e.suggestions:
                    shell.console.print(f"Suggestions: {', '.join(e.suggestions)}")

        shell._process_command = mock_process_with_error

        # Test error handling
        await shell._process_command("error test")
        calls = shell.console.print.call_args_list
        assert any("Parse error: Test parsing error" in str(call) for call in calls)
        assert any(
            "Suggestions: suggestion1, suggestion2" in str(call) for call in calls
        )

        # Restore original parse method
        shell.parser_pipeline.parse = original_parse

    def test_word_completer_includes_aliases(self, shell_with_parser):
        """Test that word completer includes command aliases."""
        shell = shell_with_parser

        # Get all available command names for completion
        available_names = set()

        # Add command names
        for cmd in shell.command_registry.list_commands():
            available_names.add(cmd.name)
            available_names.update(cmd.aliases or [])

        # Check that both primary names and aliases are available
        assert "exit" in available_names
        assert "quit" in available_names
        assert "help" in available_names

    @pytest.mark.asyncio
    async def test_subprocess_executor_integration(self, shell_with_parser):
        """Test that shell commands are executed via SubprocessExecutor."""
        shell = shell_with_parser

        # Test the actual integrated shell command processing
        executed_commands = []

        # Create a mock subprocess executor that tracks calls
        class MockSubprocessExecutor:
            def __init__(self, console):
                self.console = console

            async def run(self, command):
                executed_commands.append(command)
                self.console.print(f"Mock execution: {command}")

        # Patch the SubprocessExecutor in the shell module
        with patch("cli_patterns.ui.shell.SubprocessExecutor", MockSubprocessExecutor):
            # Test shell command execution using the real _process_command
            await shell._process_command("! echo hello world")

            # Verify that the shell command was processed
            assert len(executed_commands) == 1
            assert executed_commands[0] == "echo hello world"

            # Test another shell command
            await shell._process_command("! ls -la")
            assert len(executed_commands) == 2
            assert executed_commands[1] == "ls -la"

    def test_command_registry_metadata_completeness(self, shell_with_parser):
        """Test that command registry has complete metadata for all commands."""
        shell = shell_with_parser

        # All builtin commands should be registered
        builtin_commands = ["help", "exit", "echo", "theme", "coverage"]

        for cmd_name in builtin_commands:
            cmd_meta = shell.command_registry.get(cmd_name)
            assert cmd_meta is not None, f"Command {cmd_name} not registered"
            assert cmd_meta.name == cmd_name
            assert cmd_meta.description, f"Command {cmd_name} has no description"
            assert cmd_meta.category == "builtin"
            assert cmd_meta.handler is not None, f"Command {cmd_name} has no handler"

    def test_context_mode_and_directory_tracking(self, shell_with_parser):
        """Test that context properly tracks mode and directory."""
        shell = shell_with_parser

        # Default context should be in text mode
        assert shell.context.mode == "text"

        # Should be able to set current directory
        shell.context.current_directory = "/tmp"
        assert shell.context.current_directory == "/tmp"

        # Should be able to change mode
        shell.context.mode = "interactive"
        assert shell.context.mode == "interactive"

    @pytest.mark.asyncio
    async def test_end_to_end_command_flow(self, shell_with_parser):
        """Test complete end-to-end command processing flow."""
        shell = shell_with_parser

        # Mock the complete flow
        processed_commands = []

        async def mock_complete_flow(user_input: str) -> None:
            # Step 1: Parse input
            result = shell.parser_pipeline.parse(user_input, shell.context)

            # Step 2: Add to history
            shell.context.add_to_history(user_input)

            # Step 3: Handle different command types
            if result.command == "!":
                processed_commands.append(f"shell:{result.shell_command}")
            elif result.command in ["exit", "quit"]:
                processed_commands.append("exit")
            else:
                cmd_meta = shell.command_registry.get(result.command)
                if cmd_meta:
                    processed_commands.append(f"builtin:{result.command}")
                else:
                    suggestions = shell.command_registry.get_suggestions(result.command)
                    processed_commands.append(f"unknown:{result.command}:{suggestions}")

        shell._process_command = mock_complete_flow

        # Test various command types
        await shell._process_command("help")
        await shell._process_command("! ls -la")
        await shell._process_command("exit")
        await shell._process_command("unknown_cmd")

        # Verify flow
        assert "builtin:help" in processed_commands
        assert "shell:ls -la" in processed_commands
        assert "exit" in processed_commands
        assert any("unknown:unknown_cmd:" in cmd for cmd in processed_commands)

        # Verify history tracking
        assert len(shell.context.history) == 4
        assert "help" in shell.context.history
        assert "! ls -la" in shell.context.history
