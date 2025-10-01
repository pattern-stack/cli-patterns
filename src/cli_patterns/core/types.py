"""Core semantic types for the wizard system.

This module defines semantic types that provide type safety for the wizard system
while maintaining MyPy strict mode compliance. These are simple NewType definitions
that prevent type confusion without adding runtime validation complexity.

The semantic types help distinguish between different string contexts in the wizard:
- BranchId: Represents a branch identifier in the wizard tree
- ActionId: Represents an action identifier
- OptionKey: Represents an option key name
- MenuId: Represents a menu identifier for navigation
- StateValue: Represents any JSON-serializable value that can be stored in state

All ID types are backed by strings but provide semantic meaning at the type level.
StateValue is a JSON-compatible type alias for flexible state storage.
"""

from __future__ import annotations

from typing import Any, NewType, Optional, Union

from typing_extensions import TypeGuard

# JSON-compatible types for state values
JsonPrimitive = Union[str, int, float, bool, None]
JsonValue = Union[JsonPrimitive, list["JsonValue"], dict[str, "JsonValue"]]

# Core semantic types for wizard system
BranchId = NewType("BranchId", str)
"""Semantic type for branch identifiers in the wizard tree."""

ActionId = NewType("ActionId", str)
"""Semantic type for action identifiers."""

OptionKey = NewType("OptionKey", str)
"""Semantic type for option key names."""

MenuId = NewType("MenuId", str)
"""Semantic type for menu identifiers."""

# State value is any JSON-serializable value
StateValue = JsonValue
"""Type alias for state values - any JSON-serializable data."""

# Type aliases for common collections using semantic types
BranchList = list[BranchId]
"""Type alias for lists of branch IDs."""

BranchSet = set[BranchId]
"""Type alias for sets of branch IDs."""

ActionList = list[ActionId]
"""Type alias for lists of action IDs."""

ActionSet = set[ActionId]
"""Type alias for sets of action IDs."""

OptionDict = dict[OptionKey, StateValue]
"""Type alias for option dictionaries mapping keys to state values."""

MenuList = list[MenuId]
"""Type alias for lists of menu IDs."""


# Factory functions for creating semantic types
def make_branch_id(value: str, validate: Optional[bool] = None) -> BranchId:
    """Create a BranchId from a string value.

    Args:
        value: String value to convert to BranchId
        validate: If True, validate input. If None, use global config. If False, skip.

    Returns:
        BranchId with semantic type safety

    Raises:
        ValueError: If validate=True and value is invalid
    """
    if validate is None:
        # Import here to avoid circular dependency
        from cli_patterns.core.config import get_config

        validate = get_config()["enable_validation"]

    if validate:
        if not value or not value.strip():
            raise ValueError("BranchId cannot be empty")
        if len(value) > 100:
            raise ValueError("BranchId is too long (max 100 characters)")
    return BranchId(value)


def make_action_id(value: str, validate: Optional[bool] = None) -> ActionId:
    """Create an ActionId from a string value.

    Args:
        value: String value to convert to ActionId
        validate: If True, validate input. If None, use global config. If False, skip.

    Returns:
        ActionId with semantic type safety

    Raises:
        ValueError: If validate=True and value is invalid
    """
    if validate is None:
        from cli_patterns.core.config import get_config

        validate = get_config()["enable_validation"]

    if validate:
        if not value or not value.strip():
            raise ValueError("ActionId cannot be empty")
        if len(value) > 100:
            raise ValueError("ActionId is too long (max 100 characters)")
    return ActionId(value)


def make_option_key(value: str, validate: Optional[bool] = None) -> OptionKey:
    """Create an OptionKey from a string value.

    Args:
        value: String value to convert to OptionKey
        validate: If True, validate input. If None, use global config. If False, skip.

    Returns:
        OptionKey with semantic type safety

    Raises:
        ValueError: If validate=True and value is invalid
    """
    if validate is None:
        from cli_patterns.core.config import get_config

        validate = get_config()["enable_validation"]

    if validate:
        if not value or not value.strip():
            raise ValueError("OptionKey cannot be empty")
        if len(value) > 100:
            raise ValueError("OptionKey is too long (max 100 characters)")
    return OptionKey(value)


def make_menu_id(value: str, validate: Optional[bool] = None) -> MenuId:
    """Create a MenuId from a string value.

    Args:
        value: String value to convert to MenuId
        validate: If True, validate input. If None, use global config. If False, skip.

    Returns:
        MenuId with semantic type safety

    Raises:
        ValueError: If validate=True and value is invalid
    """
    if validate is None:
        from cli_patterns.core.config import get_config

        validate = get_config()["enable_validation"]

    if validate:
        if not value or not value.strip():
            raise ValueError("MenuId cannot be empty")
        if len(value) > 100:
            raise ValueError("MenuId is too long (max 100 characters)")
    return MenuId(value)


# Type guard functions for runtime type checking
def is_branch_id(value: Any) -> TypeGuard[BranchId]:
    """Check if a value is a BranchId at runtime.

    Args:
        value: Value to check

    Returns:
        True if value is a BranchId (string type), False otherwise

    Note:
        This is a type guard function that helps with type narrowing.
        At runtime, BranchId is just a string, so this checks for string type.
    """
    return isinstance(value, str)


def is_action_id(value: Any) -> TypeGuard[ActionId]:
    """Check if a value is an ActionId at runtime.

    Args:
        value: Value to check

    Returns:
        True if value is an ActionId (string type), False otherwise

    Note:
        This is a type guard function that helps with type narrowing.
        At runtime, ActionId is just a string, so this checks for string type.
    """
    return isinstance(value, str)


def is_option_key(value: Any) -> TypeGuard[OptionKey]:
    """Check if a value is an OptionKey at runtime.

    Args:
        value: Value to check

    Returns:
        True if value is an OptionKey (string type), False otherwise

    Note:
        This is a type guard function that helps with type narrowing.
        At runtime, OptionKey is just a string, so this checks for string type.
    """
    return isinstance(value, str)


def is_menu_id(value: Any) -> TypeGuard[MenuId]:
    """Check if a value is a MenuId at runtime.

    Args:
        value: Value to check

    Returns:
        True if value is a MenuId (string type), False otherwise

    Note:
        This is a type guard function that helps with type narrowing.
        At runtime, MenuId is just a string, so this checks for string type.
    """
    return isinstance(value, str)
