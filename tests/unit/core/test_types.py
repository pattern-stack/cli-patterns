"""Tests for core semantic types for the wizard system.

This module tests the semantic type definitions that provide type safety
for the wizard system. These are simple NewType definitions that prevent
type confusion while maintaining MyPy strict mode compliance.
"""

from __future__ import annotations

from typing import Any

import pytest

# Import the types we're testing (these will fail initially)
try:
    from cli_patterns.core.types import (
        ActionId,
        BranchId,
        OptionKey,
        StateValue,
        is_action_id,
        is_branch_id,
        is_menu_id,
        is_option_key,
        make_action_id,
        make_branch_id,
        make_menu_id,
        make_option_key,
    )
except ImportError:
    # These imports will fail initially since the implementation doesn't exist
    pass

pytestmark = pytest.mark.unit


class TestSemanticTypeDefinitions:
    """Test basic semantic type creation and identity."""

    def test_branch_id_creation(self) -> None:
        """
        GIVEN: A string value for a branch
        WHEN: Creating a BranchId
        THEN: The BranchId maintains the value but has distinct type identity
        """
        branch_str = "main_menu"
        branch_id = make_branch_id(branch_str)

        # Value preservation
        assert str(branch_id) == branch_str

        # Type identity (will be checked by MyPy at compile time)
        assert isinstance(branch_id, str)  # Runtime check

    def test_action_id_creation(self) -> None:
        """
        GIVEN: A string value for an action
        WHEN: Creating an ActionId
        THEN: The ActionId maintains the value but has distinct type identity
        """
        action_str = "deploy_app"
        action_id = make_action_id(action_str)

        assert str(action_id) == action_str
        assert isinstance(action_id, str)

    def test_option_key_creation(self) -> None:
        """
        GIVEN: A string value for an option key
        WHEN: Creating an OptionKey
        THEN: The OptionKey maintains the value but has distinct type identity
        """
        key_str = "environment"
        option_key = make_option_key(key_str)

        assert str(option_key) == key_str
        assert isinstance(option_key, str)

    def test_menu_id_creation(self) -> None:
        """
        GIVEN: A string value for a menu
        WHEN: Creating a MenuId
        THEN: The MenuId maintains the value but has distinct type identity
        """
        menu_str = "settings_menu"
        menu_id = make_menu_id(menu_str)

        assert str(menu_id) == menu_str
        assert isinstance(menu_id, str)


class TestSemanticTypeDistinctness:
    """Test that semantic types are distinct from each other and from str."""

    def test_types_are_distinct_from_str(self) -> None:
        """
        GIVEN: Various semantic types created from the same string value
        WHEN: Checking type identity at runtime
        THEN: All types derive from str but have semantic distinction
        """
        base_str = "test"

        branch_id = make_branch_id(base_str)
        action_id = make_action_id(base_str)
        option_key = make_option_key(base_str)
        menu_id = make_menu_id(base_str)

        # All are strings at runtime
        for semantic_type in [branch_id, action_id, option_key, menu_id]:
            assert isinstance(semantic_type, str)
            assert str(semantic_type) == base_str

    def test_type_safety_in_collections(self) -> None:
        """
        GIVEN: Semantic types used in collections
        WHEN: Adding them to typed collections
        THEN: The types maintain their semantic meaning in collections
        """
        # Test BranchId in sets and lists
        branch1 = make_branch_id("main")
        branch2 = make_branch_id("settings")
        branch3 = make_branch_id("main")  # Duplicate value

        branch_set: set[BranchId] = {branch1, branch2, branch3}
        assert len(branch_set) == 2  # Duplicate removed

        branch_list: list[BranchId] = [branch1, branch2, branch3]
        assert len(branch_list) == 3  # Duplicates preserved

        # Test ActionId in dictionaries
        action1 = make_action_id("deploy")
        action2 = make_action_id("test")

        actions_dict: dict[ActionId, str] = {
            action1: "Deploy the application",
            action2: "Run tests",
        }
        assert len(actions_dict) == 2

    def test_string_operations_work(self) -> None:
        """
        GIVEN: Semantic types that derive from str
        WHEN: Performing string operations
        THEN: All string operations work normally
        """
        branch_id = make_branch_id("main-menu")

        # String methods work
        assert branch_id.upper() == "MAIN-MENU"
        assert branch_id.lower() == "main-menu"
        assert branch_id.replace("-", "_") == "main_menu"
        assert branch_id.startswith("main")
        assert branch_id.endswith("menu")
        assert len(branch_id) == 9
        assert "main" in branch_id

        # String concatenation works
        combined = branch_id + "_suffix"
        assert combined == "main-menu_suffix"

        # String formatting works
        formatted = f"Branch: {branch_id}"
        assert formatted == "Branch: main-menu"


class TestSemanticTypeValidation:
    """Test validation and error handling for semantic types."""

    def test_factory_without_validation(self) -> None:
        """
        GIVEN: Factory functions called without validation
        WHEN: Creating semantic types with any string (even invalid)
        THEN: No validation occurs (zero overhead by default)
        """
        # Empty strings should work without validation
        empty_branch = make_branch_id("")
        empty_action = make_action_id("")
        empty_option = make_option_key("")
        empty_menu = make_menu_id("")

        # All should be empty strings
        for semantic_type in [empty_branch, empty_action, empty_option, empty_menu]:
            assert str(semantic_type) == ""
            assert len(semantic_type) == 0

    def test_factory_with_validation_rejects_empty(self) -> None:
        """
        GIVEN: Factory functions called with validation enabled
        WHEN: Creating semantic types with empty strings
        THEN: ValueError is raised
        """
        with pytest.raises(ValueError, match="BranchId cannot be empty"):
            make_branch_id("", validate=True)

        with pytest.raises(ValueError, match="ActionId cannot be empty"):
            make_action_id("", validate=True)

        with pytest.raises(ValueError, match="OptionKey cannot be empty"):
            make_option_key("", validate=True)

        with pytest.raises(ValueError, match="MenuId cannot be empty"):
            make_menu_id("", validate=True)

    def test_factory_with_validation_rejects_whitespace_only(self) -> None:
        """
        GIVEN: Factory functions called with validation enabled
        WHEN: Creating semantic types with whitespace-only strings
        THEN: ValueError is raised
        """
        with pytest.raises(ValueError, match="BranchId cannot be empty"):
            make_branch_id("   ", validate=True)

        with pytest.raises(ValueError, match="ActionId cannot be empty"):
            make_action_id("\t\n", validate=True)

    def test_factory_with_validation_rejects_too_long(self) -> None:
        """
        GIVEN: Factory functions called with validation enabled
        WHEN: Creating semantic types with strings that are too long
        THEN: ValueError is raised
        """
        too_long = "x" * 101

        with pytest.raises(ValueError, match="BranchId is too long"):
            make_branch_id(too_long, validate=True)

        with pytest.raises(ValueError, match="ActionId is too long"):
            make_action_id(too_long, validate=True)

        with pytest.raises(ValueError, match="OptionKey is too long"):
            make_option_key(too_long, validate=True)

        with pytest.raises(ValueError, match="MenuId is too long"):
            make_menu_id(too_long, validate=True)

    def test_factory_with_validation_accepts_valid_strings(self) -> None:
        """
        GIVEN: Factory functions called with validation enabled
        WHEN: Creating semantic types with valid strings
        THEN: Types are created successfully
        """
        valid_branch = make_branch_id("main_menu", validate=True)
        valid_action = make_action_id("deploy_action", validate=True)
        valid_option = make_option_key("environment", validate=True)
        valid_menu = make_menu_id("settings", validate=True)

        assert str(valid_branch) == "main_menu"
        assert str(valid_action) == "deploy_action"
        assert str(valid_option) == "environment"
        assert str(valid_menu) == "settings"

    def test_special_character_handling(self) -> None:
        """
        GIVEN: String values with special characters
        WHEN: Creating semantic types
        THEN: Special characters are preserved
        """
        special_branch = make_branch_id("main-menu_v2")
        special_action = make_action_id("deploy:prod")
        special_option = make_option_key("file.path")

        assert str(special_branch) == "main-menu_v2"
        assert str(special_action) == "deploy:prod"
        assert str(special_option) == "file.path"


class TestSemanticTypeEquality:
    """Test equality and hashing behavior of semantic types."""

    def test_equality_with_same_type(self) -> None:
        """
        GIVEN: Two semantic types of the same type with same value
        WHEN: Comparing for equality
        THEN: They are equal
        """
        branch1 = make_branch_id("main")
        branch2 = make_branch_id("main")

        assert branch1 == branch2
        assert not (branch1 != branch2)

    def test_equality_with_different_values(self) -> None:
        """
        GIVEN: Two semantic types of the same type with different values
        WHEN: Comparing for equality
        THEN: They are not equal
        """
        branch1 = make_branch_id("main")
        branch2 = make_branch_id("settings")

        assert branch1 != branch2
        assert not (branch1 == branch2)

    def test_equality_with_raw_string(self) -> None:
        """
        GIVEN: A semantic type and a raw string with the same value
        WHEN: Comparing for equality
        THEN: They are equal (since semantic types are NewType)
        """
        branch_id = make_branch_id("main")
        raw_str = "main"

        assert branch_id == raw_str
        assert raw_str == branch_id

    def test_hashing_behavior(self) -> None:
        """
        GIVEN: Semantic types with same and different values
        WHEN: Using them as dictionary keys or in sets
        THEN: Hashing works correctly
        """
        branch1 = make_branch_id("main")
        branch2 = make_branch_id("main")
        branch3 = make_branch_id("settings")

        # Same value should have same hash
        assert hash(branch1) == hash(branch2)

        # Can be used as dict keys
        branch_dict = {branch1: "main_info", branch3: "settings_info"}
        assert len(branch_dict) == 2
        assert branch_dict[branch2] == "main_info"  # branch2 should work as key


class TestTypeGuards:
    """Test type guard functions for runtime type checking."""

    def test_is_branch_id(self) -> None:
        """
        GIVEN: Various values including BranchId
        WHEN: Checking with is_branch_id type guard
        THEN: Returns True for strings, False otherwise
        """
        branch = make_branch_id("main")
        assert is_branch_id(branch)
        assert is_branch_id("main")
        assert not is_branch_id(123)
        assert not is_branch_id(None)
        assert not is_branch_id([])

    def test_is_action_id(self) -> None:
        """
        GIVEN: Various values including ActionId
        WHEN: Checking with is_action_id type guard
        THEN: Returns True for strings, False otherwise
        """
        action = make_action_id("deploy")
        assert is_action_id(action)
        assert is_action_id("deploy")
        assert not is_action_id(123)
        assert not is_action_id(None)

    def test_is_option_key(self) -> None:
        """
        GIVEN: Various values including OptionKey
        WHEN: Checking with is_option_key type guard
        THEN: Returns True for strings, False otherwise
        """
        option = make_option_key("environment")
        assert is_option_key(option)
        assert is_option_key("environment")
        assert not is_option_key(123)

    def test_is_menu_id(self) -> None:
        """
        GIVEN: Various values including MenuId
        WHEN: Checking with is_menu_id type guard
        THEN: Returns True for strings, False otherwise
        """
        menu = make_menu_id("settings")
        assert is_menu_id(menu)
        assert is_menu_id("settings")
        assert not is_menu_id(123)


class TestSemanticTypeUsagePatterns:
    """Test common usage patterns and best practices."""

    def test_function_signature_type_safety(self) -> None:
        """
        GIVEN: Functions that expect specific semantic types
        WHEN: Calling them with correct types
        THEN: The calls work without type errors
        """

        def navigate_to_branch(
            branch: BranchId, options: dict[OptionKey, StateValue]
        ) -> str:
            return f"Navigating to {branch} with {len(options)} options"

        branch = make_branch_id("main")
        opts = {
            make_option_key("env"): "production",
            make_option_key("region"): "us-west-2",
        }

        result = navigate_to_branch(branch, opts)
        assert "main" in result
        assert "2 options" in result

    def test_type_conversion_patterns(self) -> None:
        """
        GIVEN: Raw strings that need to be converted to semantic types
        WHEN: Converting them explicitly
        THEN: The conversion preserves value but adds type safety
        """
        raw_branches = ["main", "settings", "deploy"]
        semantic_branches = [make_branch_id(b) for b in raw_branches]

        assert len(semantic_branches) == 3
        for raw, semantic in zip(raw_branches, semantic_branches):
            assert str(semantic) == raw

    def test_mixed_type_collections(self) -> None:
        """
        GIVEN: Collections containing multiple semantic types
        WHEN: Working with them
        THEN: Type safety is maintained
        """
        # Dictionary with mixed semantic types as keys
        wizard_data: dict[str, Any] = {
            make_branch_id("main"): "main_branch",
            make_action_id("deploy"): "deploy_action",
            make_option_key("env"): "production",
            make_menu_id("settings"): "settings_menu",
        }

        assert len(wizard_data) == 4

        # All keys are strings at runtime but have semantic meaning
        for key in wizard_data.keys():
            assert isinstance(key, str)


class TestStateValueType:
    """Test StateValue type alias for JSON-serializable values."""

    def test_state_value_accepts_json_types(self) -> None:
        """
        GIVEN: Various JSON-serializable values
        WHEN: Using them as StateValue
        THEN: They are accepted by the type system
        """
        import json

        # All these should be valid StateValue types
        state_values: list[StateValue] = [
            "string_value",
            123,
            45.67,
            True,
            False,
            None,
            ["list", "of", "values"],
            {"key": "value", "nested": {"data": 123}},
        ]

        # Should be JSON-serializable
        for value in state_values:
            json_str = json.dumps(value)
            assert json_str is not None

    def test_state_value_in_collections(self) -> None:
        """
        GIVEN: StateValue used in option collections
        WHEN: Building option dictionaries
        THEN: Type safety is maintained
        """
        options: dict[OptionKey, StateValue] = {
            make_option_key("string_opt"): "value",
            make_option_key("number_opt"): 42,
            make_option_key("bool_opt"): True,
            make_option_key("list_opt"): [1, 2, 3],
            make_option_key("dict_opt"): {"nested": "data"},
        }

        assert len(options) == 5
        assert options[make_option_key("string_opt")] == "value"
        assert options[make_option_key("number_opt")] == 42


class TestSemanticTypeCompatibility:
    """Test compatibility with existing code and libraries."""

    def test_json_serialization(self) -> None:
        """
        GIVEN: Semantic types in data structures
        WHEN: Serializing to JSON
        THEN: Serialization works normally
        """
        import json

        data = {
            "branch": make_branch_id("main"),
            "action": make_action_id("deploy"),
            "options": {
                make_option_key("env"): "prod",
                make_option_key("region"): "us-west",
            },
        }

        # Should serialize without errors
        json_str = json.dumps(data, default=str)
        assert "main" in json_str
        assert "deploy" in json_str
        assert "prod" in json_str

    def test_string_formatting_compatibility(self) -> None:
        """
        GIVEN: Semantic types used in string formatting
        WHEN: Using various formatting methods
        THEN: All formatting works normally
        """
        branch = make_branch_id("main")
        action = make_action_id("deploy")
        option = make_option_key("environment")

        # Format strings
        formatted = f"Branch: {branch}, Action: {action}, Option: {option}"
        assert formatted == "Branch: main, Action: deploy, Option: environment"
