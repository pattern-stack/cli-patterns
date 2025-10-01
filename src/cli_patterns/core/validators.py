"""Validation utilities for CLI Patterns core types.

This module provides security-focused validators to prevent DoS attacks
and ensure data integrity:

- JSON depth validation (prevents stack overflow)
- Collection size validation (prevents memory exhaustion)
- StateValue validation (combined depth + size checks)
"""

from __future__ import annotations

from typing import Any

# Configuration constants
MAX_JSON_DEPTH = 50
"""Maximum nesting depth for JSON-serializable values.

This prevents stack overflow during serialization and CPU exhaustion
during parsing. Default: 50 levels.
"""

MAX_COLLECTION_SIZE = 1000
"""Maximum total number of items in collections (lists, dicts).

This prevents memory exhaustion from excessively large data structures.
Default: 1000 items (counting nested items recursively).
"""


class ValidationError(Exception):
    """Raised when validation fails.

    This exception is raised by validators when input doesn't meet
    security or integrity requirements.
    """

    pass


def validate_json_depth(value: Any, max_depth: int = MAX_JSON_DEPTH) -> None:
    """Validate that JSON value doesn't exceed maximum nesting depth.

    This prevents DoS attacks via deeply nested structures that cause:
    - Stack overflow during serialization
    - Excessive memory consumption
    - CPU exhaustion during parsing

    Args:
        value: Value to validate (must be JSON-serializable)
        max_depth: Maximum allowed nesting depth (default: 50)

    Raises:
        ValidationError: If nesting exceeds max_depth

    Example:
        >>> validate_json_depth({"a": {"b": {"c": 1}}})  # OK
        >>> validate_json_depth(create_deeply_nested(100))  # Raises ValidationError
    """

    def check_depth(obj: Any, current_depth: int = 0) -> int:
        """Recursively check nesting depth."""
        if current_depth > max_depth:
            raise ValidationError(
                f"JSON nesting too deep: {current_depth} levels "
                f"(maximum: {max_depth})"
            )

        if isinstance(obj, dict):
            if not obj:  # Empty dict is depth 0
                return current_depth
            return max(check_depth(v, current_depth + 1) for v in obj.values())
        elif isinstance(obj, list):
            if not obj:  # Empty list is depth 0
                return current_depth
            return max(check_depth(item, current_depth + 1) for item in obj)
        else:
            # Primitive value
            return current_depth

    check_depth(value)


def validate_collection_size(value: Any, max_size: int = MAX_COLLECTION_SIZE) -> None:
    """Validate that collection doesn't exceed maximum size.

    This prevents DoS attacks via large collections that cause memory exhaustion.
    Counts all items recursively in nested structures.

    Args:
        value: Collection to validate (dict or list)
        max_size: Maximum allowed total size (default: 1000)

    Raises:
        ValidationError: If collection exceeds max_size

    Example:
        >>> validate_collection_size([1, 2, 3])  # OK
        >>> validate_collection_size([1] * 10000)  # Raises ValidationError
    """

    def check_size(obj: Any) -> int:
        """Recursively count total elements."""
        count = 0

        if isinstance(obj, dict):
            count += len(obj)
            if count > max_size:
                raise ValidationError(
                    f"Collection too large: {count} items (maximum: {max_size})"
                )
            for v in obj.values():
                count += check_size(v)
                if count > max_size:
                    raise ValidationError(
                        f"Collection too large: {count} items (maximum: {max_size})"
                    )
        elif isinstance(obj, list):
            count += len(obj)
            if count > max_size:
                raise ValidationError(
                    f"Collection too large: {count} items (maximum: {max_size})"
                )
            for item in obj:
                count += check_size(item)
                if count > max_size:
                    raise ValidationError(
                        f"Collection too large: {count} items (maximum: {max_size})"
                    )

        return count

    check_size(value)


def validate_state_value(value: Any) -> None:
    """Validate StateValue meets all safety requirements.

    This is the main validation function for StateValue types.
    It combines depth and size checks to ensure data safety.

    Checks:
    - Nesting depth within limits (default: 50 levels)
    - Collection size within limits (default: 1000 items)
    - Type is JSON-serializable (implicit - errors on non-JSON types)

    Args:
        value: StateValue to validate

    Raises:
        ValidationError: If validation fails

    Example:
        >>> validate_state_value({"user": {"name": "test", "age": 30}})  # OK
        >>> validate_state_value(create_huge_dict())  # Raises ValidationError
    """
    validate_json_depth(value)
    validate_collection_size(value)
