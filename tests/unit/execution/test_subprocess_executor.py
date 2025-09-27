"""Unit tests for SubprocessExecutor."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from rich.console import Console

from cli_patterns.execution.subprocess_executor import CommandResult, SubprocessExecutor

pytestmark = pytest.mark.executor


class TestCommandResult:
    """Test CommandResult class."""

    def test_success_result(self):
        """Test successful command result."""
        result = CommandResult(
            exit_code=0, stdout="output", stderr="", timed_out=False, interrupted=False
        )
        assert result.success
        assert result.exit_code == 0
        assert result.stdout == "output"
        assert result.stderr == ""
        assert not result.timed_out
        assert not result.interrupted

    def test_failed_result(self):
        """Test failed command result."""
        result = CommandResult(
            exit_code=1, stdout="", stderr="error", timed_out=False, interrupted=False
        )
        assert not result.success
        assert result.exit_code == 1
        assert result.stderr == "error"

    def test_timed_out_result(self):
        """Test timed out command result."""
        result = CommandResult(
            exit_code=-1, stdout="", stderr="", timed_out=True, interrupted=False
        )
        assert not result.success
        assert result.timed_out

    def test_interrupted_result(self):
        """Test interrupted command result."""
        result = CommandResult(
            exit_code=130, stdout="", stderr="", timed_out=False, interrupted=True
        )
        assert not result.success
        assert result.interrupted


class TestSubprocessExecutor:
    """Test SubprocessExecutor class."""

    @pytest.fixture
    def console(self):
        """Mock Rich console."""
        return Mock(spec=Console)

    @pytest.fixture
    def executor(self, console):
        """Create executor with mocked console."""
        return SubprocessExecutor(console=console, default_timeout=10.0)

    @pytest.mark.asyncio
    async def test_successful_command(self, executor, console):
        """Test successful command execution."""
        with patch("asyncio.create_subprocess_shell") as mock_create:
            # Mock process
            mock_process = AsyncMock()
            mock_process.returncode = 0
            mock_process.stdout = AsyncMock()
            mock_process.stderr = AsyncMock()
            mock_process.stdout.read.side_effect = [b"Hello\n", b"World\n", b""]
            mock_process.stderr.read.return_value = b""
            mock_process.wait.return_value = None
            mock_create.return_value = mock_process

            result = await executor.run("echo 'Hello World'")

            assert result.success
            assert result.exit_code == 0
            assert "Hello" in result.stdout
            assert "World" in result.stdout
            assert result.stderr == ""

            # Check console output
            assert console.print.called

    @pytest.mark.asyncio
    async def test_failed_command(self, executor, console):
        """Test failed command execution."""
        with patch("asyncio.create_subprocess_shell") as mock_create:
            # Mock process
            mock_process = AsyncMock()
            mock_process.returncode = 1
            mock_process.stdout = AsyncMock()
            mock_process.stderr = AsyncMock()
            mock_process.stdout.read.return_value = b""
            mock_process.stderr.read.side_effect = [b"Error occurred\n", b""]
            mock_process.wait.return_value = None
            mock_create.return_value = mock_process

            result = await executor.run("false")

            assert not result.success
            assert result.exit_code == 1
            assert "Error occurred" in result.stderr
            assert console.print.called

    @pytest.mark.asyncio
    async def test_command_not_found(self, executor, console):
        """Test command not found error."""
        with patch("asyncio.create_subprocess_shell") as mock_create:
            mock_create.side_effect = FileNotFoundError("Command not found")

            result = await executor.run("nonexistent-command")

            assert not result.success
            assert result.exit_code == 127
            assert "Command not found" in result.stderr
            assert console.print.called

    @pytest.mark.asyncio
    async def test_permission_denied(self, executor, console):
        """Test permission denied error."""
        with patch("asyncio.create_subprocess_shell") as mock_create:
            mock_create.side_effect = PermissionError("Permission denied")

            result = await executor.run("/root/protected")

            assert not result.success
            assert result.exit_code == 126
            assert "Permission denied" in result.stderr
            assert console.print.called

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_timeout(self, executor, console):
        """Test command timeout."""
        with patch("asyncio.create_subprocess_shell") as mock_create:
            # Mock process that times out
            mock_process = AsyncMock()
            mock_process.returncode = None
            mock_process.stdout = AsyncMock()
            mock_process.stderr = AsyncMock()
            mock_process.stdout.read.return_value = b""
            mock_process.stderr.read.return_value = b""
            mock_process.wait.return_value = None
            mock_process.kill = MagicMock()  # Use MagicMock for kill
            mock_create.return_value = mock_process

            with patch("asyncio.wait_for", side_effect=asyncio.TimeoutError):
                result = await executor.run("sleep 100", timeout=0.1)

            assert not result.success
            assert result.timed_out
            assert result.exit_code == -1
            mock_process.kill.assert_called_once()

    @pytest.mark.asyncio
    async def test_keyboard_interrupt(self, executor, console):
        """Test keyboard interrupt handling."""
        with patch("asyncio.create_subprocess_shell") as mock_create:
            mock_create.side_effect = KeyboardInterrupt()

            result = await executor.run("long-running-command")

            assert not result.success
            assert result.interrupted
            assert result.exit_code == 130

    @pytest.mark.asyncio
    async def test_list_command(self, executor, console):
        """Test command as list of arguments."""
        with patch("asyncio.create_subprocess_shell") as mock_create:
            # Mock process
            mock_process = AsyncMock()
            mock_process.returncode = 0
            mock_process.stdout = AsyncMock()
            mock_process.stderr = AsyncMock()
            mock_process.stdout.read.side_effect = [b"file.txt\n", b""]
            mock_process.stderr.read.return_value = b""
            mock_process.wait.return_value = None
            mock_create.return_value = mock_process

            result = await executor.run(["ls", "-la", "/tmp"])

            assert result.success
            mock_create.assert_called_once()
            # Check that list was joined into string
            call_args = mock_create.call_args[0][0]
            assert call_args == "ls -la /tmp"

    @pytest.mark.asyncio
    async def test_custom_env(self, executor, console):
        """Test command with custom environment variables."""
        with patch("asyncio.create_subprocess_shell") as mock_create:
            # Mock process
            mock_process = AsyncMock()
            mock_process.returncode = 0
            mock_process.stdout = AsyncMock()
            mock_process.stderr = AsyncMock()
            mock_process.stdout.read.side_effect = [b"VALUE\n", b""]
            mock_process.stderr.read.return_value = b""
            mock_process.wait.return_value = None
            mock_create.return_value = mock_process

            custom_env = {"MY_VAR": "VALUE"}
            result = await executor.run("echo $MY_VAR", env=custom_env)

            assert result.success
            mock_create.assert_called_once()
            # Check that env was passed
            call_kwargs = mock_create.call_args[1]
            assert "env" in call_kwargs
            assert "MY_VAR" in call_kwargs["env"]

    @pytest.mark.asyncio
    async def test_custom_cwd(self, executor, console):
        """Test command with custom working directory."""
        with patch("asyncio.create_subprocess_shell") as mock_create:
            # Mock process
            mock_process = AsyncMock()
            mock_process.returncode = 0
            mock_process.stdout = AsyncMock()
            mock_process.stderr = AsyncMock()
            mock_process.stdout.read.side_effect = [b"/tmp\n", b""]
            mock_process.stderr.read.return_value = b""
            mock_process.wait.return_value = None
            mock_create.return_value = mock_process

            result = await executor.run("pwd", cwd="/tmp")

            assert result.success
            mock_create.assert_called_once()
            # Check that cwd was passed
            call_kwargs = mock_create.call_args[1]
            assert call_kwargs["cwd"] == "/tmp"

    @pytest.mark.asyncio
    async def test_no_streaming(self, console):
        """Test executor without output streaming."""
        executor = SubprocessExecutor(console=console, stream_output=False)

        with patch("asyncio.create_subprocess_shell") as mock_create:
            # Mock process
            mock_process = AsyncMock()
            mock_process.returncode = 0
            mock_process.stdout = AsyncMock()
            mock_process.stderr = AsyncMock()
            mock_process.stdout.read.side_effect = [b"Output\n", b""]
            mock_process.stderr.read.return_value = b""
            mock_process.wait.return_value = None
            mock_create.return_value = mock_process

            result = await executor.run("echo 'Output'")

            assert result.success
            assert "Output" in result.stdout
            # Console should not be called when streaming is disabled
            console.print.assert_not_called()

    @pytest.mark.asyncio
    async def test_binary_output_handling(self, executor, console):
        """Test handling of binary output that can't be decoded."""
        with patch("asyncio.create_subprocess_shell") as mock_create:
            # Mock process with binary output
            mock_process = AsyncMock()
            mock_process.returncode = 0
            mock_process.stdout = AsyncMock()
            mock_process.stderr = AsyncMock()
            # Invalid UTF-8 sequence
            mock_process.stdout.read.side_effect = [b"\xff\xfe\xfd\n", b""]
            mock_process.stderr.read.return_value = b""
            mock_process.wait.return_value = None
            mock_create.return_value = mock_process

            result = await executor.run("cat binary_file")

            assert result.success
            # Should handle binary data gracefully
            assert result.stdout  # Should have some output

    def test_executor_initialization(self):
        """Test executor initialization with defaults."""
        executor = SubprocessExecutor()
        assert executor.console is not None
        assert executor.default_timeout == 30.0
        assert executor.stream_output is True
        assert executor.output_component is not None

    def test_executor_custom_initialization(self):
        """Test executor initialization with custom values."""
        console = Mock(spec=Console)
        executor = SubprocessExecutor(
            console=console, default_timeout=60.0, stream_output=False
        )
        assert executor.console is console
        assert executor.default_timeout == 60.0
        assert executor.stream_output is False
