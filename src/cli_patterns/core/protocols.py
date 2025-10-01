"""Protocol definitions for CLI Patterns.

This module defines the core protocols (interfaces) that implementation classes
must satisfy. Protocols enable:
- Dependency injection
- Multiple implementations
- Type-safe interfaces
- Runtime checking (with @runtime_checkable)

All protocols are runtime-checkable, meaning isinstance() checks work at runtime.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from cli_patterns.core.models import (
    ActionConfigUnion,
    ActionResult,
    CollectionResult,
    NavigationResult,
    OptionConfigUnion,
    SessionState,
)
from cli_patterns.core.types import BranchId


@runtime_checkable
class ActionExecutor(Protocol):
    """Protocol for executing actions.

    Implementations of this protocol handle the execution of actions
    (bash commands, Python functions, etc.) and return results.

    Example:
        class BashExecutor:
            def execute(self, action: ActionConfigUnion, state: SessionState) -> ActionResult:
                if isinstance(action, BashActionConfig):
                    # Execute bash command
                    result = subprocess.run(action.command, ...)
                    return ActionResult(...)
    """

    def execute(self, action: ActionConfigUnion, state: SessionState) -> ActionResult:
        """Execute an action and return the result.

        Args:
            action: The action configuration to execute
            state: Current session state

        Returns:
            ActionResult containing success status, output, and errors
        """
        ...


@runtime_checkable
class OptionCollector(Protocol):
    """Protocol for collecting option values from users.

    Implementations of this protocol handle the interactive collection
    of option values (strings, selections, paths, etc.) and return results.

    Example:
        class InteractiveCollector:
            def collect(self, option: OptionConfigUnion, state: SessionState) -> CollectionResult:
                if isinstance(option, StringOptionConfig):
                    # Prompt user for string input
                    value = input(f"{option.description}: ")
                    return CollectionResult(...)
    """

    def collect(
        self, option: OptionConfigUnion, state: SessionState
    ) -> CollectionResult:
        """Collect an option value from the user.

        Args:
            option: The option configuration to collect
            state: Current session state

        Returns:
            CollectionResult containing the collected value or error
        """
        ...


@runtime_checkable
class NavigationController(Protocol):
    """Protocol for controlling wizard navigation.

    Implementations of this protocol handle navigation between branches
    in the wizard tree, including history management.

    Example:
        class TreeNavigator:
            def navigate(self, target: BranchId, state: SessionState) -> NavigationResult:
                # Update state with new branch
                state.navigation_history.append(state.current_branch)
                state.current_branch = target
                return NavigationResult(...)
    """

    def navigate(self, target: BranchId, state: SessionState) -> NavigationResult:
        """Navigate to a target branch.

        Args:
            target: The branch ID to navigate to
            state: Current session state (will be modified)

        Returns:
            NavigationResult containing success status and target
        """
        ...


# TODO: Future protocol extension points
# - ValidationProtocol: For custom option validation
# - InterpolationProtocol: For variable interpolation in commands
# - PersistenceProtocol: For session state persistence
# - ThemeProtocol: For custom theming (may already exist in ui.design)
