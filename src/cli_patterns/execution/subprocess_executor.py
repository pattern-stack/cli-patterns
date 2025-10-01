"""Subprocess execution utilities for CLI commands.

This module provides async subprocess execution with real-time output streaming
and integration with the design system for themed output display.

Example usage:
    executor = SubprocessExecutor(console)
    result = await executor.run("ls -la")
    result = await executor.run("echo 'Hello World'")
    result = await executor.run("invalid-command")  # Shows nice error
"""

from __future__ import annotations

import asyncio
import logging
import os
import shlex
from typing import Optional, Union

from rich.console import Console
from rich.text import Text

from ..ui.design.components import Output
from ..ui.design.registry import theme_registry
from ..ui.design.tokens import StatusToken

logger = logging.getLogger(__name__)


class CommandResult:
    """Result of a command execution."""

    def __init__(
        self,
        exit_code: int,
        stdout: str,
        stderr: str,
        timed_out: bool = False,
        interrupted: bool = False,
    ):
        """Initialize command result.

        Args:
            exit_code: Process exit code
            stdout: Captured stdout output
            stderr: Captured stderr output
            timed_out: Whether the command timed out
            interrupted: Whether the command was interrupted
        """
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr
        self.timed_out = timed_out
        self.interrupted = interrupted

    @property
    def success(self) -> bool:
        """Check if command executed successfully."""
        return self.exit_code == 0 and not self.timed_out and not self.interrupted


class SubprocessExecutor:
    """Executor for running shell commands with async subprocess and themed output."""

    def __init__(
        self,
        console: Optional[Console] = None,
        default_timeout: float = 30.0,
        stream_output: bool = True,
    ):
        """Initialize the subprocess executor.

        Args:
            console: Rich console for output (creates one if not provided)
            default_timeout: Default timeout in seconds for commands
            stream_output: Whether to stream output in real-time
        """
        self.console = console or Console()
        self.default_timeout = default_timeout
        self.stream_output = stream_output
        self.output_component = Output()

    async def run(
        self,
        command: Union[str, list[str]],
        timeout: Optional[float] = None,
        cwd: Optional[str] = None,
        env: Optional[dict[str, str]] = None,
        allow_shell_features: bool = False,
    ) -> CommandResult:
        """Execute a command asynchronously with themed output streaming.

        Args:
            command: Command to execute (string or list of args)
            timeout: Command timeout in seconds (uses default if None)
            cwd: Working directory for the command
            env: Environment variables for the command
            allow_shell_features: Allow shell features (pipes, redirects, etc.).
                SECURITY WARNING: Only enable for trusted commands. When False,
                command is executed without shell to prevent injection attacks.

        Returns:
            CommandResult with exit code and captured output
        """
        timeout = timeout or self.default_timeout

        # Prepare command list for display and execution
        if isinstance(command, list):
            command_list = command
            command_str = " ".join(command)
        else:
            command_str = command
            # Parse string into list for safe execution
            try:
                command_list = shlex.split(command_str)
            except ValueError as e:
                # Invalid shell syntax
                stderr_msg = f"Invalid command syntax: {e}"
                if self.stream_output:
                    error_style = theme_registry.resolve(StatusToken.ERROR)
                    self.console.print(Text(stderr_msg, style=error_style))
                return CommandResult(
                    exit_code=-1,
                    stdout="",
                    stderr=stderr_msg,
                )

        # Show running status
        if self.stream_output:
            running_style = theme_registry.resolve(StatusToken.RUNNING)
            self.console.print(Text(f"Running: {command_str}", style=running_style))

        # Merge environment variables
        process_env = os.environ.copy()
        if env:
            process_env.update(env)

        # Capture output
        stdout_lines: list[str] = []
        stderr_lines: list[str] = []
        timed_out = False
        interrupted = False
        exit_code = -1
        process = None  # Initialize process variable

        try:
            # Create subprocess - use shell only if explicitly allowed
            if allow_shell_features:
                # SECURITY WARNING: Shell features enabled
                logger.warning(
                    f"Executing command with shell features enabled: {command_str}"
                )
                process = await asyncio.create_subprocess_shell(
                    command_str,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=cwd,
                    env=process_env,
                )
            else:
                # Safe execution without shell (prevents injection)
                if not command_list:
                    stderr_msg = "Empty command"
                    if self.stream_output:
                        error_style = theme_registry.resolve(StatusToken.ERROR)
                        self.console.print(Text(stderr_msg, style=error_style))
                    return CommandResult(
                        exit_code=-1,
                        stdout="",
                        stderr=stderr_msg,
                    )

                process = await asyncio.create_subprocess_exec(
                    *command_list,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=cwd,
                    env=process_env,
                )

            # Create tasks for reading streams
            stdout_task = asyncio.create_task(
                self._read_stream(process.stdout, stdout_lines, is_stderr=False)
            )
            stderr_task = asyncio.create_task(
                self._read_stream(process.stderr, stderr_lines, is_stderr=True)
            )

            # Wait for process with timeout
            try:
                await asyncio.wait_for(
                    asyncio.gather(process.wait(), stdout_task, stderr_task),
                    timeout=timeout,
                )
                exit_code = process.returncode or 0
            except asyncio.TimeoutError:
                timed_out = True
                # Kill the process
                if process.returncode is None:
                    process.kill()
                    await process.wait()
                exit_code = -1

        except KeyboardInterrupt:
            interrupted = True
            # Kill the process on interrupt
            if process and process.returncode is None:
                process.kill()
                await process.wait()
            exit_code = 130  # Standard exit code for SIGINT

        except FileNotFoundError:
            # Command not found
            stderr_lines.append("Command not found")
            if self.stream_output:
                self._display_line("Command not found", is_stderr=True)
            exit_code = 127

        except PermissionError:
            # Permission denied
            stderr_lines.append("Permission denied")
            if self.stream_output:
                self._display_line("Permission denied", is_stderr=True)
            exit_code = 126

        except Exception as e:
            # Other errors
            error_msg = f"Error executing command: {e}"
            stderr_lines.append(error_msg)
            if self.stream_output:
                self._display_line(error_msg, is_stderr=True)
            exit_code = 1

        # Display completion status
        if self.stream_output:
            if timed_out:
                timeout_style = theme_registry.resolve(StatusToken.WARNING)
                self.console.print(
                    Text(f"Command timed out after {timeout}s", style=timeout_style)
                )
            elif interrupted:
                interrupt_style = theme_registry.resolve(StatusToken.WARNING)
                self.console.print(Text("Command interrupted", style=interrupt_style))
            elif exit_code == 0:
                success_style = theme_registry.resolve(StatusToken.SUCCESS)
                self.console.print(
                    Text("Command completed successfully", style=success_style)
                )
            else:
                error_style = theme_registry.resolve(StatusToken.ERROR)
                self.console.print(
                    Text(
                        f"Command failed with exit code {exit_code}", style=error_style
                    )
                )

        return CommandResult(
            exit_code=exit_code,
            stdout="\n".join(stdout_lines),
            stderr="\n".join(stderr_lines),
            timed_out=timed_out,
            interrupted=interrupted,
        )

    async def _read_stream(
        self,
        stream: Optional[asyncio.StreamReader],
        lines: list[str],
        is_stderr: bool = False,
    ) -> None:
        """Read from a stream line by line and display with theming.

        Args:
            stream: The asyncio stream to read from
            lines: List to append lines to
            is_stderr: Whether this is stderr (for styling)
        """
        if not stream:
            return

        decoder_errors = "replace"  # Handle binary output gracefully
        buffer = b""

        try:
            while True:
                # Read available data
                chunk = await stream.read(1024)
                if not chunk:
                    break

                buffer += chunk

                # Process complete lines
                while b"\n" in buffer:
                    line_bytes, buffer = buffer.split(b"\n", 1)
                    try:
                        line = line_bytes.decode("utf-8", errors=decoder_errors)
                    except Exception:
                        line = str(line_bytes)

                    lines.append(line)
                    if self.stream_output:
                        self._display_line(line, is_stderr)

            # Process remaining buffer
            if buffer:
                try:
                    line = buffer.decode("utf-8", errors=decoder_errors)
                except Exception:
                    line = str(buffer)
                lines.append(line)
                if self.stream_output:
                    self._display_line(line, is_stderr)

        except Exception as e:
            error_line = f"Stream reading error: {e}"
            lines.append(error_line)
            if self.stream_output:
                self._display_line(error_line, is_stderr=True)

    def _display_line(self, line: str, is_stderr: bool = False) -> None:
        """Display a line of output with appropriate theming.

        Args:
            line: The line to display
            is_stderr: Whether this is stderr output
        """
        if is_stderr:
            # Use error styling for stderr
            style = theme_registry.resolve(self.output_component.stderr_status)
            self.console.print(Text(line, style=style), highlight=False)
        else:
            # Use normal emphasis for stdout
            style = theme_registry.resolve(self.output_component.stdout_emphasis)
            self.console.print(Text(line, style=style), highlight=False)
