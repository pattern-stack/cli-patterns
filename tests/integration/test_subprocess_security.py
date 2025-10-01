"""Integration tests for subprocess security features.

This module tests the security features of SubprocessExecutor, including
command injection prevention through the allow_shell_features flag.
"""

import pytest

from cli_patterns.execution.subprocess_executor import SubprocessExecutor


@pytest.mark.asyncio
@pytest.mark.integration
class TestSubprocessSecurity:
    """Test security features of SubprocessExecutor."""

    async def test_safe_command_without_shell(self) -> None:
        """Should execute safe command without shell features."""
        executor = SubprocessExecutor(stream_output=False)
        result = await executor.run("echo hello", allow_shell_features=False)

        assert result.success
        assert "hello" in result.stdout

    async def test_blocks_command_injection_without_shell(self) -> None:
        """Should prevent command injection when shell features disabled."""
        executor = SubprocessExecutor(stream_output=False)

        # This should fail because semicolon will be treated as literal argument
        # The command "echo" will receive "test;whoami" as a single argument
        result = await executor.run("echo test;whoami", allow_shell_features=False)

        # Should succeed (echo accepts the argument)
        assert result.success
        # But semicolon should be in the output as a literal character
        assert "test;whoami" in result.stdout or ";" in result.stdout

    async def test_allows_shell_features_when_enabled(self) -> None:
        """Should allow shell features when explicitly enabled."""
        executor = SubprocessExecutor(stream_output=False)

        # This should work with shell features enabled
        result = await executor.run(
            "echo hello && echo world", allow_shell_features=True
        )

        assert result.success
        assert "hello" in result.stdout
        assert "world" in result.stdout

    async def test_pipe_fails_without_shell(self) -> None:
        """Should not support pipes when shell features disabled."""
        executor = SubprocessExecutor(stream_output=False)

        # Pipe should not work without shell
        result = await executor.run("echo test | cat", allow_shell_features=False)

        # The command will fail because "|" will be treated as a literal argument
        # and echo doesn't accept that as a valid option
        assert not result.success or "|" in result.stdout

    async def test_pipe_works_with_shell(self) -> None:
        """Should support pipes when shell features enabled."""
        executor = SubprocessExecutor(stream_output=False)

        # Pipe should work with shell enabled
        result = await executor.run("echo test | cat", allow_shell_features=True)

        assert result.success
        assert "test" in result.stdout

    async def test_command_substitution_fails_without_shell(self) -> None:
        """Should not execute command substitution without shell."""
        executor = SubprocessExecutor(stream_output=False)

        # Command substitution should not work
        result = await executor.run("echo $(whoami)", allow_shell_features=False)

        # Should treat $() as literal text
        assert not result.success or "$" in result.stdout or "(" in result.stdout

    async def test_command_substitution_works_with_shell(self) -> None:
        """Should execute command substitution with shell features."""
        executor = SubprocessExecutor(stream_output=False)

        # Command substitution should work with shell
        result = await executor.run("echo $(echo test)", allow_shell_features=True)

        assert result.success
        assert "test" in result.stdout

    async def test_redirection_fails_without_shell(self) -> None:
        """Should not support redirection without shell features."""
        executor = SubprocessExecutor(stream_output=False)

        # Redirection should not work
        result = await executor.run(
            "echo test > /tmp/test_output", allow_shell_features=False
        )

        # Should treat > as literal argument
        assert not result.success or ">" in result.stdout

    async def test_handles_commands_with_arguments(self) -> None:
        """Should handle commands with normal arguments safely."""
        executor = SubprocessExecutor(stream_output=False)

        result = await executor.run("echo -n hello world", allow_shell_features=False)

        assert result.success
        assert "hello world" in result.stdout or "helloworld" in result.stdout

    async def test_handles_quoted_arguments(self) -> None:
        """Should handle quoted arguments correctly."""
        executor = SubprocessExecutor(stream_output=False)

        result = await executor.run('echo "hello world"', allow_shell_features=False)

        assert result.success
        assert "hello world" in result.stdout

    async def test_default_is_safe_mode(self) -> None:
        """Should default to safe mode (shell features disabled)."""
        executor = SubprocessExecutor(stream_output=False)

        # Without specifying allow_shell_features, should default to False
        result = await executor.run("echo test")

        assert result.success
        assert "test" in result.stdout

    async def test_invalid_command_syntax(self) -> None:
        """Should handle invalid shell syntax gracefully."""
        executor = SubprocessExecutor(stream_output=False)

        # Unmatched quotes should fail in shlex.split
        result = await executor.run('echo "unterminated', allow_shell_features=False)

        assert not result.success
        assert "Invalid command syntax" in result.stderr

    async def test_command_not_found(self) -> None:
        """Should handle command not found gracefully."""
        executor = SubprocessExecutor(stream_output=False)

        result = await executor.run(
            "nonexistent_command_xyz", allow_shell_features=False
        )

        assert not result.success
        assert result.exit_code != 0
