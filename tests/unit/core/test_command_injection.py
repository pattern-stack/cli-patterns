"""Tests for command injection prevention measures.

This module tests security measures that prevent command injection attacks
through shell metacharacter exploitation.
"""

import pytest

from cli_patterns.core.models import BashActionConfig
from cli_patterns.core.types import make_action_id


class TestCommandInjectionPrevention:
    """Test command injection prevention measures."""

    def test_rejects_command_chaining_semicolon(self) -> None:
        """Should reject commands with semicolon chaining."""
        with pytest.raises(ValueError, match="command chaining"):
            BashActionConfig(
                id=make_action_id("test"),
                name="Test",
                command="echo hello; rm -rf /",
                allow_shell_features=False,
            )

    def test_rejects_command_chaining_ampersand(self) -> None:
        """Should reject commands with ampersand chaining."""
        with pytest.raises(ValueError, match="command chaining"):
            BashActionConfig(
                id=make_action_id("test"),
                name="Test",
                command="echo hello & rm -rf /",
                allow_shell_features=False,
            )

    def test_rejects_command_chaining_pipe(self) -> None:
        """Should reject commands with pipe chaining."""
        with pytest.raises(ValueError, match="command chaining"):
            BashActionConfig(
                id=make_action_id("test"),
                name="Test",
                command="cat file | grep secret",
                allow_shell_features=False,
            )

    def test_rejects_command_substitution_dollar_paren(self) -> None:
        """Should reject commands with $() command substitution."""
        with pytest.raises(ValueError, match="command substitution"):
            BashActionConfig(
                id=make_action_id("test"),
                name="Test",
                command="echo $(whoami)",
                allow_shell_features=False,
            )

    def test_rejects_command_substitution_backticks(self) -> None:
        """Should reject commands with backtick command substitution."""
        with pytest.raises(ValueError, match="command substitution"):
            BashActionConfig(
                id=make_action_id("test"),
                name="Test",
                command="echo `whoami`",
                allow_shell_features=False,
            )

    def test_rejects_output_redirection(self) -> None:
        """Should reject commands with output redirection."""
        with pytest.raises(ValueError, match="redirection"):
            BashActionConfig(
                id=make_action_id("test"),
                name="Test",
                command="echo secret > /tmp/stolen",
                allow_shell_features=False,
            )

    def test_rejects_input_redirection(self) -> None:
        """Should reject commands with input redirection."""
        with pytest.raises(ValueError, match="redirection"):
            BashActionConfig(
                id=make_action_id("test"),
                name="Test",
                command="cat < /etc/passwd",
                allow_shell_features=False,
            )

    def test_rejects_variable_expansion(self) -> None:
        """Should reject commands with ${} variable expansion."""
        with pytest.raises(ValueError, match="variable expansion"):
            BashActionConfig(
                id=make_action_id("test"),
                name="Test",
                command="echo ${HOME}",
                allow_shell_features=False,
            )

    def test_rejects_variable_assignment(self) -> None:
        """Should reject commands with variable assignment."""
        with pytest.raises(ValueError, match="variable assignment"):
            BashActionConfig(
                id=make_action_id("test"),
                name="Test",
                command="PATH=/evil/path ls",
                allow_shell_features=False,
            )

    def test_allows_safe_command_without_shell_features(self) -> None:
        """Should allow safe commands without shell features."""
        config = BashActionConfig(
            id=make_action_id("test"),
            name="Test",
            command="kubectl apply -f deploy.yaml",
            allow_shell_features=False,
        )
        assert config.command == "kubectl apply -f deploy.yaml"
        assert config.allow_shell_features is False

    def test_allows_command_with_arguments(self) -> None:
        """Should allow commands with normal arguments."""
        config = BashActionConfig(
            id=make_action_id("test"),
            name="Test",
            command="docker run --rm -v /data:/data myimage",
            allow_shell_features=False,
        )
        assert config.command == "docker run --rm -v /data:/data myimage"

    def test_allows_dangerous_command_with_explicit_flag(self) -> None:
        """Should allow dangerous commands when explicitly enabled."""
        config = BashActionConfig(
            id=make_action_id("test"),
            name="Test",
            command="cat file | grep secret",
            allow_shell_features=True,  # Explicit opt-in
        )
        assert config.command == "cat file | grep secret"
        assert config.allow_shell_features is True

    def test_allows_all_shell_features_when_enabled(self) -> None:
        """Should allow all shell features when flag is True."""
        # This should NOT raise even with all dangerous patterns
        config = BashActionConfig(
            id=make_action_id("test"),
            name="Test",
            command="cat ${FILE} | grep pattern > output.txt && echo done",
            allow_shell_features=True,
        )
        assert config.allow_shell_features is True

    def test_default_allow_shell_features_is_false(self) -> None:
        """Should default to allow_shell_features=False for security."""
        config = BashActionConfig(
            id=make_action_id("test"),
            name="Test",
            command="echo hello",
        )
        assert config.allow_shell_features is False

    def test_error_message_suggests_fix(self) -> None:
        """Should provide helpful error message with fix suggestion."""
        with pytest.raises(ValueError, match="Set allow_shell_features=True to enable"):
            BashActionConfig(
                id=make_action_id("test"),
                name="Test",
                command="echo test | cat",
                allow_shell_features=False,
            )
