"""Security tests for core models.

This module tests command injection prevention, DoS protection,
and collection size limits.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from cli_patterns.core.models import (
    BashActionConfig,
    BranchConfig,
    SessionState,
    StringOptionConfig,
    WizardConfig,
)
from cli_patterns.core.types import make_action_id, make_branch_id, make_option_key

pytestmark = pytest.mark.unit


class TestCommandInjectionPrevention:
    """Test command injection prevention in BashActionConfig."""

    def test_rejects_command_chaining_semicolon(self) -> None:
        """Should reject commands with semicolon chaining."""
        with pytest.raises(ValidationError, match="command chaining"):
            BashActionConfig(
                id=make_action_id("test"),
                name="Test",
                command="echo hello; rm -rf /",
                allow_shell_features=False,
            )

    def test_rejects_command_chaining_ampersand(self) -> None:
        """Should reject commands with ampersand chaining."""
        with pytest.raises(ValidationError, match="command chaining"):
            BashActionConfig(
                id=make_action_id("test"),
                name="Test",
                command="echo hello & rm -rf /",
                allow_shell_features=False,
            )

    def test_rejects_command_chaining_pipe(self) -> None:
        """Should reject commands with pipe."""
        with pytest.raises(ValidationError, match="command chaining"):
            BashActionConfig(
                id=make_action_id("test"),
                name="Test",
                command="cat file | grep secret",
                allow_shell_features=False,
            )

    def test_rejects_command_substitution_dollar_paren(self) -> None:
        """Should reject commands with $() substitution."""
        with pytest.raises(ValidationError, match="command substitution"):
            BashActionConfig(
                id=make_action_id("test"),
                name="Test",
                command="echo $(whoami)",
                allow_shell_features=False,
            )

    def test_rejects_command_substitution_backtick(self) -> None:
        """Should reject commands with backtick substitution."""
        with pytest.raises(ValidationError, match="command substitution"):
            BashActionConfig(
                id=make_action_id("test"),
                name="Test",
                command="echo `whoami`",
                allow_shell_features=False,
            )

    def test_rejects_output_redirection(self) -> None:
        """Should reject commands with output redirection."""
        with pytest.raises(ValidationError, match="redirection"):
            BashActionConfig(
                id=make_action_id("test"),
                name="Test",
                command="echo secret > /tmp/leak",
                allow_shell_features=False,
            )

    def test_rejects_input_redirection(self) -> None:
        """Should reject commands with input redirection."""
        with pytest.raises(ValidationError, match="redirection"):
            BashActionConfig(
                id=make_action_id("test"),
                name="Test",
                command="cat < /etc/passwd",
                allow_shell_features=False,
            )

    def test_rejects_variable_expansion(self) -> None:
        """Should reject commands with variable expansion."""
        with pytest.raises(ValidationError, match="variable expansion"):
            BashActionConfig(
                id=make_action_id("test"),
                name="Test",
                command="echo ${PATH}",
                allow_shell_features=False,
            )

    def test_rejects_variable_assignment(self) -> None:
        """Should reject commands with variable assignment."""
        with pytest.raises(ValidationError, match="variable assignment"):
            BashActionConfig(
                id=make_action_id("test"),
                name="Test",
                command="PATH=/evil/path kubectl apply",
                allow_shell_features=False,
            )

    def test_allows_safe_command(self) -> None:
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
            command="docker run --rm -it ubuntu:latest /bin/bash",
            allow_shell_features=False,
        )
        assert "docker run" in config.command

    def test_allows_dangerous_command_with_flag(self) -> None:
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
        commands = [
            "echo hello; echo world",
            "cat file | grep pattern",
            "echo $(date)",
            "echo `whoami`",
            "cat > output.txt",
            "cmd < input.txt",
            "echo ${VAR}",
            "PATH=/new/path cmd",
        ]

        for cmd in commands:
            config = BashActionConfig(
                id=make_action_id("test"),
                name="Test",
                command=cmd,
                allow_shell_features=True,
            )
            assert config.command == cmd


class TestDoSProtection:
    """Test DoS protection via depth and size validation."""

    def test_rejects_deeply_nested_option_value(self) -> None:
        """Should reject deeply nested structures in option values."""
        # Create deeply nested dict (> 50 levels)
        deep_value: dict[str, any] = {"value": 1}
        for _ in range(55):
            deep_value = {"nested": deep_value}

        with pytest.raises(ValidationError, match="nesting too deep"):
            SessionState(option_values={make_option_key("test"): deep_value})

    def test_rejects_large_option_value(self) -> None:
        """Should reject excessively large option values."""
        # Create list with > 1000 items
        large_value = list(range(1500))

        with pytest.raises(ValidationError, match="too large"):
            SessionState(option_values={make_option_key("test"): large_value})

    def test_rejects_deeply_nested_variable(self) -> None:
        """Should reject deeply nested structures in variables."""
        deep_value: dict[str, any] = {"value": 1}
        for _ in range(55):
            deep_value = {"nested": deep_value}

        with pytest.raises(ValidationError, match="nesting too deep"):
            SessionState(variables={"test": deep_value})

    def test_rejects_large_variable(self) -> None:
        """Should reject excessively large variables."""
        large_value = list(range(1500))

        with pytest.raises(ValidationError, match="too large"):
            SessionState(variables={"test": large_value})

    def test_rejects_too_many_options(self) -> None:
        """Should reject too many options."""
        options = {make_option_key(f"opt{i}"): i for i in range(1001)}

        with pytest.raises(ValidationError, match="Too many options"):
            SessionState(option_values=options)

    def test_rejects_too_many_variables(self) -> None:
        """Should reject too many variables."""
        variables = {f"var{i}": i for i in range(1001)}

        with pytest.raises(ValidationError, match="Too many variables"):
            SessionState(variables=variables)

    def test_accepts_valid_nested_value(self) -> None:
        """Should accept reasonably nested values."""
        valid_value = {"level1": {"level2": {"level3": {"level4": {"level5": "data"}}}}}
        state = SessionState(option_values={make_option_key("test"): valid_value})
        assert state.option_values[make_option_key("test")] == valid_value

    def test_accepts_valid_large_value(self) -> None:
        """Should accept moderately large values."""
        valid_value = list(range(500))
        state = SessionState(option_values={make_option_key("test"): valid_value})
        assert len(state.option_values[make_option_key("test")]) == 500


class TestCollectionLimits:
    """Test collection size limits in configuration models."""

    def test_rejects_too_many_actions(self) -> None:
        """Should reject branch with too many actions."""
        with pytest.raises(ValidationError, match="Too many actions"):
            BranchConfig(
                id=make_branch_id("test"),
                title="Test",
                actions=[
                    BashActionConfig(
                        id=make_action_id(f"action{i}"),
                        name=f"Action {i}",
                        command="echo test",
                    )
                    for i in range(101)  # Over limit
                ],
            )

    def test_rejects_too_many_options(self) -> None:
        """Should reject branch with too many options."""
        with pytest.raises(ValidationError, match="Too many options"):
            BranchConfig(
                id=make_branch_id("test"),
                title="Test",
                options=[
                    StringOptionConfig(
                        id=make_option_key(f"opt{i}"),
                        name=f"Option {i}",
                        description="Test",
                    )
                    for i in range(51)  # Over limit
                ],
            )

    def test_rejects_too_many_menus(self) -> None:
        """Should reject branch with too many menus."""
        from cli_patterns.core.models import MenuConfig

        with pytest.raises(ValidationError, match="Too many menus"):
            BranchConfig(
                id=make_branch_id("test"),
                title="Test",
                menus=[
                    MenuConfig(
                        id=make_action_id(f"menu{i}"),
                        label=f"Menu {i}",
                        target=make_branch_id("target"),
                    )
                    for i in range(21)  # Over limit
                ],
            )

    def test_rejects_too_many_branches(self) -> None:
        """Should reject wizard with too many branches."""
        with pytest.raises(ValidationError, match="Too many branches"):
            WizardConfig(
                name="test",
                version="1.0.0",
                entry_branch=make_branch_id("branch0"),
                branches=[
                    BranchConfig(id=make_branch_id(f"branch{i}"), title=f"Branch {i}")
                    for i in range(101)  # Over limit
                ],
            )

    def test_accepts_maximum_actions(self) -> None:
        """Should accept exactly 100 actions."""
        config = BranchConfig(
            id=make_branch_id("test"),
            title="Test",
            actions=[
                BashActionConfig(
                    id=make_action_id(f"action{i}"),
                    name=f"Action {i}",
                    command="echo test",
                )
                for i in range(100)  # Exactly at limit
            ],
        )
        assert len(config.actions) == 100

    def test_accepts_maximum_branches(self) -> None:
        """Should accept exactly 100 branches."""
        config = WizardConfig(
            name="test",
            version="1.0.0",
            entry_branch=make_branch_id("branch0"),
            branches=[
                BranchConfig(id=make_branch_id(f"branch{i}"), title=f"Branch {i}")
                for i in range(100)  # Exactly at limit
            ],
        )
        assert len(config.branches) == 100


class TestWizardValidation:
    """Test wizard-specific validation."""

    def test_rejects_nonexistent_entry_branch(self) -> None:
        """Should reject wizard with entry_branch not in branches."""
        with pytest.raises(ValidationError, match="entry_branch.*not found"):
            WizardConfig(
                name="test",
                version="1.0.0",
                entry_branch=make_branch_id("nonexistent"),
                branches=[
                    BranchConfig(id=make_branch_id("main"), title="Main"),
                    BranchConfig(id=make_branch_id("settings"), title="Settings"),
                ],
            )

    def test_accepts_valid_entry_branch(self) -> None:
        """Should accept wizard with valid entry_branch."""
        config = WizardConfig(
            name="test",
            version="1.0.0",
            entry_branch=make_branch_id("main"),
            branches=[
                BranchConfig(id=make_branch_id("main"), title="Main"),
                BranchConfig(id=make_branch_id("settings"), title="Settings"),
            ],
        )
        assert config.entry_branch == make_branch_id("main")

    def test_error_message_shows_available_branches(self) -> None:
        """Should show available branches in error message."""
        try:
            WizardConfig(
                name="test",
                version="1.0.0",
                entry_branch=make_branch_id("invalid"),
                branches=[
                    BranchConfig(id=make_branch_id("main"), title="Main"),
                    BranchConfig(id=make_branch_id("settings"), title="Settings"),
                ],
            )
            pytest.fail("Should have raised ValidationError")
        except ValidationError as e:
            error_str = str(e)
            assert "Available branches" in error_str
            assert "main" in error_str or "settings" in error_str
