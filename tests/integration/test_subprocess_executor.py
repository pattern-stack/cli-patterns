"""Integration tests for SubprocessExecutor with real commands."""

from __future__ import annotations

import asyncio
import sys
import tempfile
from pathlib import Path

import pytest
from rich.console import Console

from cli_patterns.execution.subprocess_executor import SubprocessExecutor
from cli_patterns.ui.design.registry import theme_registry

pytestmark = pytest.mark.executor


class TestSubprocessExecutorIntegration:
    """Integration tests for SubprocessExecutor with real commands."""

    @pytest.fixture
    def executor(self):
        """Create executor with real console."""
        console = Console(force_terminal=True, width=80, no_color=True)
        return SubprocessExecutor(console=console)

    @pytest.mark.asyncio
    async def test_echo_command(self, executor):
        """Test simple echo command."""
        result = await executor.run("echo 'Hello, World!'")

        assert result.success
        assert result.exit_code == 0
        assert "Hello, World!" in result.stdout
        assert result.stderr == ""

    @pytest.mark.asyncio
    async def test_ls_command(self, executor):
        """Test ls command in current directory."""
        result = await executor.run("ls")

        assert result.success
        assert result.exit_code == 0
        # Should list some files
        assert result.stdout

    @pytest.mark.asyncio
    async def test_invalid_command(self, executor):
        """Test running an invalid command."""
        result = await executor.run("this-command-does-not-exist-12345")

        assert not result.success
        assert result.exit_code != 0
        # Should have error message
        assert result.stderr or "not found" in result.stdout.lower()

    @pytest.mark.asyncio
    async def test_stderr_output(self, executor):
        """Test command that outputs to stderr."""
        # Use Python to reliably generate stderr
        result = await executor.run(
            f"{sys.executable} -c \"import sys; sys.stderr.write('Error message\\n')\""
        )

        assert result.success
        assert "Error message" in result.stderr

    @pytest.mark.asyncio
    async def test_mixed_output(self, executor):
        """Test command with both stdout and stderr."""
        # Use Python to generate both outputs
        result = await executor.run(
            f'{sys.executable} -c "'
            "import sys; "
            "sys.stdout.write('Standard output\\n'); "
            "sys.stderr.write('Error output\\n')\""
        )

        assert result.success
        assert "Standard output" in result.stdout
        assert "Error output" in result.stderr

    @pytest.mark.asyncio
    async def test_exit_codes(self, executor):
        """Test various exit codes."""
        # Success (exit 0)
        result = await executor.run(f"{sys.executable} -c 'exit(0)'")
        assert result.success
        assert result.exit_code == 0

        # Failure (exit 1)
        result = await executor.run(f"{sys.executable} -c 'exit(1)'")
        assert not result.success
        assert result.exit_code == 1

        # Custom exit code
        result = await executor.run(f"{sys.executable} -c 'exit(42)'")
        assert not result.success
        assert result.exit_code == 42

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_timeout(self, executor):
        """Test command timeout."""
        # Use Python sleep to ensure cross-platform compatibility
        result = await executor.run(
            f"{sys.executable} -c 'import time; time.sleep(10)'", timeout=0.5
        )

        assert not result.success
        assert result.timed_out

    @pytest.mark.asyncio
    async def test_working_directory(self, executor):
        """Test command with custom working directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a test file in the temp directory
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("Test content")

            # Run ls in the temp directory
            result = await executor.run("ls", cwd=tmpdir)

            assert result.success
            assert "test.txt" in result.stdout

    @pytest.mark.asyncio
    async def test_environment_variables(self, executor):
        """Test command with custom environment variables."""
        # Set a custom environment variable
        result = await executor.run(
            f"{sys.executable} -c \"import os; print(os.environ.get('MY_TEST_VAR', 'not set'))\"",
            env={"MY_TEST_VAR": "test_value"},
        )

        assert result.success
        assert "test_value" in result.stdout

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_large_output(self, executor):
        """Test command with large output."""
        # Generate 1000 lines of output
        result = await executor.run(
            f"{sys.executable} -c \"for i in range(1000): print(f'Line {{i}}')\""
        )

        assert result.success
        lines = result.stdout.strip().split("\n")
        assert len(lines) == 1000
        assert lines[0] == "Line 0"
        assert lines[-1] == "Line 999"

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_concurrent_execution(self, executor):
        """Test running multiple commands concurrently."""
        tasks = [
            executor.run("echo 'Command 1'"),
            executor.run("echo 'Command 2'"),
            executor.run("echo 'Command 3'"),
        ]

        results = await asyncio.gather(*tasks)

        assert all(r.success for r in results)
        assert "Command 1" in results[0].stdout
        assert "Command 2" in results[1].stdout
        assert "Command 3" in results[2].stdout

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_streaming_output(self):
        """Test output streaming in real-time."""
        console = Console(force_terminal=True, width=80, no_color=True)
        executor = SubprocessExecutor(console=console, stream_output=True)

        # Run a command that outputs multiple lines with delays
        result = await executor.run(
            f'{sys.executable} -c "'
            "import time; "
            "print('Line 1', flush=True); "
            "time.sleep(0.1); "
            "print('Line 2', flush=True); "
            "time.sleep(0.1); "
            "print('Line 3', flush=True)\""
        )

        assert result.success
        assert "Line 1" in result.stdout
        assert "Line 2" in result.stdout
        assert "Line 3" in result.stdout

    @pytest.mark.asyncio
    async def test_no_streaming_output(self):
        """Test executor without output streaming."""
        console = Console(force_terminal=True, width=80, no_color=True)
        executor = SubprocessExecutor(console=console, stream_output=False)

        result = await executor.run("echo 'Silent output'")

        assert result.success
        assert "Silent output" in result.stdout

    @pytest.mark.asyncio
    async def test_theme_integration(self, executor):
        """Test that theme colors are properly applied."""
        # Set dark theme
        theme_registry.set_current("dark")

        result = await executor.run("echo 'Themed output'")
        assert result.success

        # Set light theme
        theme_registry.set_current("light")

        result = await executor.run("echo 'Light theme output'")
        assert result.success

    @pytest.mark.asyncio
    async def test_piped_commands(self, executor):
        """Test piped commands."""
        result = await executor.run("echo 'Hello World' | grep World")

        assert result.success
        assert "World" in result.stdout

    @pytest.mark.asyncio
    async def test_command_as_list(self, executor):
        """Test passing command as list of arguments."""
        result = await executor.run(["echo", "Hello", "World"])

        assert result.success
        assert "Hello World" in result.stdout
