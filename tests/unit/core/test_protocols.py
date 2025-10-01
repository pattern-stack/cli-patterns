"""Tests for core protocol definitions.

This module tests the protocol definitions that define the interfaces for
action execution, option collection, and navigation control.
"""

from __future__ import annotations

from typing import Protocol

import pytest

# Import the protocols we're testing (these will fail initially)
try:
    from cli_patterns.core.models import (
        ActionConfigUnion,
        ActionResult,
        BashActionConfig,
        CollectionResult,
        NavigationResult,
        OptionConfigUnion,
        SessionState,
        StringOptionConfig,
    )
    from cli_patterns.core.protocols import (
        ActionExecutor,
        NavigationController,
        OptionCollector,
    )
    from cli_patterns.core.types import (
        BranchId,
        make_action_id,
        make_branch_id,
        make_option_key,
    )
except ImportError:
    # These imports will fail initially since the implementation doesn't exist
    pass

pytestmark = pytest.mark.unit


class TestActionExecutorProtocol:
    """Test the ActionExecutor protocol definition and compliance."""

    def test_protocol_is_runtime_checkable(self) -> None:
        """
        GIVEN: The ActionExecutor protocol
        WHEN: Checking if it's runtime checkable
        THEN: It should be a Protocol with runtime_checkable decorator
        """
        assert issubclass(ActionExecutor, Protocol)
        # Check that we can use isinstance with it (runtime_checkable)
        assert hasattr(ActionExecutor, "_is_runtime_protocol")

    def test_concrete_implementation_satisfies_protocol(self) -> None:
        """
        GIVEN: A concrete class implementing ActionExecutor
        WHEN: Checking protocol compliance
        THEN: The implementation satisfies the protocol
        """

        class ConcreteExecutor:
            """Concrete implementation of ActionExecutor."""

            def execute(
                self, action: ActionConfigUnion, state: SessionState
            ) -> ActionResult:
                """Execute an action."""
                if isinstance(action, BashActionConfig):
                    return ActionResult(
                        action_id=action.id,
                        success=True,
                        output="Command executed",
                    )
                return ActionResult(
                    action_id=action.id,
                    success=False,
                    error="Unsupported action type",
                )

        # Should be able to create instance
        executor = ConcreteExecutor()

        # Should satisfy protocol at runtime
        assert isinstance(executor, ActionExecutor)

    def test_protocol_execute_method_signature(self) -> None:
        """
        GIVEN: ActionExecutor protocol
        WHEN: Inspecting the execute method
        THEN: Method signature matches expected interface
        """

        class TestExecutor:
            """Test executor for signature verification."""

            def execute(
                self, action: ActionConfigUnion, state: SessionState
            ) -> ActionResult:
                """Execute method with correct signature."""
                return ActionResult(action_id=action.id, success=True, output="test")

        executor = TestExecutor()
        assert isinstance(executor, ActionExecutor)

        # Create test data
        action = BashActionConfig(
            type="bash",
            id=make_action_id("test_action"),
            name="Test Action",
            command="echo test",
        )
        state = SessionState()

        # Execute should work
        result = executor.execute(action, state)
        assert result.success is True

    def test_missing_execute_method_fails_protocol(self) -> None:
        """
        GIVEN: A class without execute method
        WHEN: Checking protocol compliance
        THEN: It should not satisfy the protocol
        """

        class NotAnExecutor:
            """Class that doesn't implement ActionExecutor."""

            def run(
                self, action: ActionConfigUnion, state: SessionState
            ) -> ActionResult:
                """Wrong method name."""
                return ActionResult(action_id=action.id, success=True, output="")

        not_executor = NotAnExecutor()
        assert not isinstance(not_executor, ActionExecutor)


class TestOptionCollectorProtocol:
    """Test the OptionCollector protocol definition and compliance."""

    def test_protocol_is_runtime_checkable(self) -> None:
        """
        GIVEN: The OptionCollector protocol
        WHEN: Checking if it's runtime checkable
        THEN: It should be a Protocol with runtime_checkable decorator
        """
        assert issubclass(OptionCollector, Protocol)
        assert hasattr(OptionCollector, "_is_runtime_protocol")

    def test_concrete_implementation_satisfies_protocol(self) -> None:
        """
        GIVEN: A concrete class implementing OptionCollector
        WHEN: Checking protocol compliance
        THEN: The implementation satisfies the protocol
        """

        class ConcreteCollector:
            """Concrete implementation of OptionCollector."""

            def collect(
                self, option: OptionConfigUnion, state: SessionState
            ) -> CollectionResult:
                """Collect an option value."""
                return CollectionResult(
                    option_key=option.id,
                    success=True,
                    value=option.default if option.default else "default_value",
                )

        collector = ConcreteCollector()
        assert isinstance(collector, OptionCollector)

    def test_protocol_collect_method_signature(self) -> None:
        """
        GIVEN: OptionCollector protocol
        WHEN: Inspecting the collect method
        THEN: Method signature matches expected interface
        """

        class TestCollector:
            """Test collector for signature verification."""

            def collect(
                self, option: OptionConfigUnion, state: SessionState
            ) -> CollectionResult:
                """Collect method with correct signature."""
                return CollectionResult(
                    option_key=option.id, success=True, value="test_value"
                )

        collector = TestCollector()
        assert isinstance(collector, OptionCollector)

        # Create test data
        option = StringOptionConfig(
            type="string",
            id=make_option_key("test_option"),
            name="Test Option",
            description="A test option",
        )
        state = SessionState()

        # Collect should work
        result = collector.collect(option, state)
        assert result.success is True

    def test_missing_collect_method_fails_protocol(self) -> None:
        """
        GIVEN: A class without collect method
        WHEN: Checking protocol compliance
        THEN: It should not satisfy the protocol
        """

        class NotACollector:
            """Class that doesn't implement OptionCollector."""

            def gather(
                self, option: OptionConfigUnion, state: SessionState
            ) -> CollectionResult:
                """Wrong method name."""
                return CollectionResult(
                    option_key=option.id, success=True, value="value"
                )

        not_collector = NotACollector()
        assert not isinstance(not_collector, OptionCollector)


class TestNavigationControllerProtocol:
    """Test the NavigationController protocol definition and compliance."""

    def test_protocol_is_runtime_checkable(self) -> None:
        """
        GIVEN: The NavigationController protocol
        WHEN: Checking if it's runtime checkable
        THEN: It should be a Protocol with runtime_checkable decorator
        """
        assert issubclass(NavigationController, Protocol)
        assert hasattr(NavigationController, "_is_runtime_protocol")

    def test_concrete_implementation_satisfies_protocol(self) -> None:
        """
        GIVEN: A concrete class implementing NavigationController
        WHEN: Checking protocol compliance
        THEN: The implementation satisfies the protocol
        """

        class ConcreteNavigator:
            """Concrete implementation of NavigationController."""

            def navigate(
                self, target: BranchId, state: SessionState
            ) -> NavigationResult:
                """Navigate to a branch."""
                return NavigationResult(success=True, target=target)

        navigator = ConcreteNavigator()
        assert isinstance(navigator, NavigationController)

    def test_protocol_navigate_method_signature(self) -> None:
        """
        GIVEN: NavigationController protocol
        WHEN: Inspecting the navigate method
        THEN: Method signature matches expected interface
        """

        class TestNavigator:
            """Test navigator for signature verification."""

            def navigate(
                self, target: BranchId, state: SessionState
            ) -> NavigationResult:
                """Navigate method with correct signature."""
                return NavigationResult(success=True, target=target)

        navigator = TestNavigator()
        assert isinstance(navigator, NavigationController)

        # Create test data
        target = make_branch_id("target_branch")
        state = SessionState()

        # Navigate should work
        result = navigator.navigate(target, state)
        assert result.success is True
        assert result.target == target

    def test_missing_navigate_method_fails_protocol(self) -> None:
        """
        GIVEN: A class without navigate method
        WHEN: Checking protocol compliance
        THEN: It should not satisfy the protocol
        """

        class NotANavigator:
            """Class that doesn't implement NavigationController."""

            def go_to(self, target: BranchId, state: SessionState) -> NavigationResult:
                """Wrong method name."""
                return NavigationResult(success=True, target=target)

        not_navigator = NotANavigator()
        assert not isinstance(not_navigator, NavigationController)


class TestProtocolIntegration:
    """Test protocol integration and usage patterns."""

    def test_protocols_can_be_used_as_type_hints(self) -> None:
        """
        GIVEN: Protocol types
        WHEN: Using them as type hints
        THEN: Type hints work correctly
        """

        def execute_action(
            executor: ActionExecutor, action: ActionConfigUnion, state: SessionState
        ) -> ActionResult:
            """Function accepting protocol type."""
            return executor.execute(action, state)

        def collect_option(
            collector: OptionCollector, option: OptionConfigUnion, state: SessionState
        ) -> CollectionResult:
            """Function accepting protocol type."""
            return collector.collect(option, state)

        def navigate_to(
            navigator: NavigationController, target: BranchId, state: SessionState
        ) -> NavigationResult:
            """Function accepting protocol type."""
            return navigator.navigate(target, state)

        # Create concrete implementations
        class TestExecutor:
            def execute(
                self, action: ActionConfigUnion, state: SessionState
            ) -> ActionResult:
                return ActionResult(
                    action_id=action.id, success=True, output="executed"
                )

        class TestCollector:
            def collect(
                self, option: OptionConfigUnion, state: SessionState
            ) -> CollectionResult:
                return CollectionResult(
                    option_key=option.id, success=True, value="collected"
                )

        class TestNavigator:
            def navigate(
                self, target: BranchId, state: SessionState
            ) -> NavigationResult:
                return NavigationResult(success=True, target=target)

        # Use the functions with concrete implementations
        action = BashActionConfig(
            type="bash",
            id=make_action_id("test"),
            name="Test",
            command="echo test",
        )
        option = StringOptionConfig(
            type="string",
            id=make_option_key("test"),
            name="Test",
            description="Test",
        )
        target = make_branch_id("test")
        state = SessionState()

        action_result = execute_action(TestExecutor(), action, state)
        assert action_result.success is True

        collection_result = collect_option(TestCollector(), option, state)
        assert collection_result.success is True

        nav_result = navigate_to(TestNavigator(), target, state)
        assert nav_result.success is True

    def test_protocols_enable_dependency_injection(self) -> None:
        """
        GIVEN: Protocols defining interfaces
        WHEN: Using them for dependency injection
        THEN: Different implementations can be swapped
        """

        class WizardEngine:
            """Engine that depends on protocols."""

            def __init__(
                self,
                executor: ActionExecutor,
                collector: OptionCollector,
                navigator: NavigationController,
            ) -> None:
                self.executor = executor
                self.collector = collector
                self.navigator = navigator

            def run_action(
                self, action: ActionConfigUnion, state: SessionState
            ) -> ActionResult:
                """Run action using injected executor."""
                return self.executor.execute(action, state)

        # Create mock implementations
        class MockExecutor:
            def execute(
                self, action: ActionConfigUnion, state: SessionState
            ) -> ActionResult:
                return ActionResult(action_id=action.id, success=True, output="mocked")

        class MockCollector:
            def collect(
                self, option: OptionConfigUnion, state: SessionState
            ) -> CollectionResult:
                return CollectionResult(
                    option_key=option.id, success=True, value="mocked"
                )

        class MockNavigator:
            def navigate(
                self, target: BranchId, state: SessionState
            ) -> NavigationResult:
                return NavigationResult(success=True, target=target)

        # Inject mock implementations
        engine = WizardEngine(MockExecutor(), MockCollector(), MockNavigator())

        # Use the engine
        action = BashActionConfig(
            type="bash",
            id=make_action_id("test"),
            name="Test",
            command="echo test",
        )
        state = SessionState()
        result = engine.run_action(action, state)

        assert result.success is True
        assert result.output == "mocked"

    def test_protocols_support_multiple_implementations(self) -> None:
        """
        GIVEN: A protocol definition
        WHEN: Creating multiple implementations
        THEN: All implementations satisfy the protocol
        """

        # Implementation 1: Simple executor
        class SimpleExecutor:
            def execute(
                self, action: ActionConfigUnion, state: SessionState
            ) -> ActionResult:
                return ActionResult(action_id=action.id, success=True, output="simple")

        # Implementation 2: Logging executor
        class LoggingExecutor:
            def __init__(self) -> None:
                self.log: list[str] = []

            def execute(
                self, action: ActionConfigUnion, state: SessionState
            ) -> ActionResult:
                self.log.append(f"Executing {action.id}")
                return ActionResult(action_id=action.id, success=True, output="logged")

        # Implementation 3: Async-like executor
        class AsyncExecutor:
            async def execute_async(
                self, action: ActionConfigUnion, state: SessionState
            ) -> ActionResult:
                # Simulate async work
                return ActionResult(action_id=action.id, success=True, output="async")

            def execute(
                self, action: ActionConfigUnion, state: SessionState
            ) -> ActionResult:
                # Synchronous wrapper
                return ActionResult(
                    action_id=action.id, success=True, output="async_sync"
                )

        # All should satisfy the protocol
        simple = SimpleExecutor()
        logging = LoggingExecutor()
        async_exec = AsyncExecutor()

        assert isinstance(simple, ActionExecutor)
        assert isinstance(logging, ActionExecutor)
        assert isinstance(async_exec, ActionExecutor)
