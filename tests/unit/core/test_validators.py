"""Tests for core validators.

This module tests the validation functions that prevent DoS attacks
and ensure data integrity.
"""

from __future__ import annotations

import pytest

from cli_patterns.core.validators import (
    MAX_COLLECTION_SIZE,
    MAX_JSON_DEPTH,
    ValidationError,
    validate_collection_size,
    validate_json_depth,
    validate_state_value,
)

pytestmark = pytest.mark.unit


class TestDepthValidation:
    """Test JSON depth validation."""

    def test_accepts_shallow_dict(self) -> None:
        """Should accept dict within depth limit."""
        data = {"a": {"b": {"c": 1}}}
        validate_json_depth(data)  # Should not raise

    def test_accepts_shallow_list(self) -> None:
        """Should accept list within depth limit."""
        data = [[[[1]]]]
        validate_json_depth(data)  # Should not raise

    def test_accepts_empty_dict(self) -> None:
        """Should accept empty dict."""
        validate_json_depth({})

    def test_accepts_empty_list(self) -> None:
        """Should accept empty list."""
        validate_json_depth([])

    def test_accepts_primitives(self) -> None:
        """Should accept primitive values."""
        validate_json_depth("string")
        validate_json_depth(123)
        validate_json_depth(45.67)
        validate_json_depth(True)
        validate_json_depth(None)

    def test_rejects_deeply_nested_dict(self) -> None:
        """Should reject dict exceeding depth limit."""
        # Create deeply nested dict
        data: dict[str, any] = {"value": 1}
        for _ in range(MAX_JSON_DEPTH + 1):
            data = {"nested": data}

        with pytest.raises(ValidationError, match="nesting too deep"):
            validate_json_depth(data)

    def test_rejects_deeply_nested_list(self) -> None:
        """Should reject list exceeding depth limit."""
        data: list[any] = [1]
        for _ in range(MAX_JSON_DEPTH + 1):
            data = [data]

        with pytest.raises(ValidationError, match="nesting too deep"):
            validate_json_depth(data)

    def test_rejects_mixed_nested_structure(self) -> None:
        """Should reject mixed dict/list exceeding depth."""
        data: any = [{"nested": [{"deep": 1}]}]
        for _ in range(MAX_JSON_DEPTH):
            data = [data]

        with pytest.raises(ValidationError, match="nesting too deep"):
            validate_json_depth(data)

    def test_custom_depth_limit(self) -> None:
        """Should respect custom depth limit."""
        data = {"a": {"b": {"c": 1}}}

        validate_json_depth(data, max_depth=10)  # OK
        with pytest.raises(ValidationError):
            validate_json_depth(data, max_depth=2)  # Too deep

    def test_depth_counts_correctly(self) -> None:
        """Should count depth correctly for various structures."""
        # Depth 0: primitives
        validate_json_depth(1, max_depth=0)

        # Depth 1: single-level dict/list
        validate_json_depth({"a": 1}, max_depth=1)
        validate_json_depth([1, 2], max_depth=1)

        # Depth 2: nested
        validate_json_depth({"a": {"b": 1}}, max_depth=2)
        validate_json_depth([[1]], max_depth=2)


class TestSizeValidation:
    """Test collection size validation."""

    def test_accepts_small_dict(self) -> None:
        """Should accept dict within size limit."""
        data = {f"key{i}": i for i in range(100)}
        validate_collection_size(data)  # Should not raise

    def test_accepts_small_list(self) -> None:
        """Should accept list within size limit."""
        data = list(range(100))
        validate_collection_size(data)

    def test_accepts_empty_collections(self) -> None:
        """Should accept empty collections."""
        validate_collection_size({})
        validate_collection_size([])

    def test_accepts_primitives(self) -> None:
        """Should accept primitive values."""
        validate_collection_size("string")
        validate_collection_size(123)
        validate_collection_size(True)
        validate_collection_size(None)

    def test_rejects_large_dict(self) -> None:
        """Should reject dict exceeding size limit."""
        data = {f"key{i}": i for i in range(MAX_COLLECTION_SIZE + 1)}

        with pytest.raises(ValidationError, match="too large"):
            validate_collection_size(data)

    def test_rejects_large_list(self) -> None:
        """Should reject list exceeding size limit."""
        data = list(range(MAX_COLLECTION_SIZE + 1))

        with pytest.raises(ValidationError, match="too large"):
            validate_collection_size(data)

    def test_counts_nested_elements(self) -> None:
        """Should count elements in nested structures."""
        # Create nested structure with many elements
        data = {f"key{i}": list(range(100)) for i in range(20)}
        # Total: 20 keys + 20*100 list items = 2020 elements

        with pytest.raises(ValidationError, match="too large"):
            validate_collection_size(data, max_size=1000)

    def test_counts_deeply_nested(self) -> None:
        """Should count all elements in deeply nested structures."""
        data = {
            "level1": {
                "level2": {"level3": [1, 2, 3, 4, 5]},
                "level2b": [1, 2, 3],
            }
        }
        # Total: 3 dicts + 8 list items = 11 elements
        validate_collection_size(data, max_size=15)

    def test_custom_size_limit(self) -> None:
        """Should respect custom size limit."""
        data = list(range(50))

        validate_collection_size(data, max_size=100)  # OK
        with pytest.raises(ValidationError):
            validate_collection_size(data, max_size=40)  # Too large


class TestStateValueValidation:
    """Test combined state value validation."""

    def test_accepts_valid_state_value(self) -> None:
        """Should accept valid state value."""
        data = {"user": {"name": "test", "age": 30, "tags": ["admin", "user"]}}
        validate_state_value(data)

    def test_rejects_too_deep(self) -> None:
        """Should reject value that's too deep."""
        data: dict[str, any] = {"value": 1}
        for _ in range(MAX_JSON_DEPTH + 1):
            data = {"nested": data}

        with pytest.raises(ValidationError, match="nesting too deep"):
            validate_state_value(data)

    def test_rejects_too_large(self) -> None:
        """Should reject value that's too large."""
        data = list(range(MAX_COLLECTION_SIZE + 1))

        with pytest.raises(ValidationError, match="too large"):
            validate_state_value(data)

    def test_validates_complex_structures(self) -> None:
        """Should validate complex real-world structures."""
        # Simulate a realistic configuration
        config = {
            "database": {"host": "localhost", "port": 5432, "name": "mydb"},
            "services": [
                {"name": "api", "port": 8000, "workers": 4},
                {"name": "worker", "port": 8001, "workers": 2},
            ],
            "features": {"auth": True, "cache": True, "debug": False},
        }
        validate_state_value(config)  # Should pass


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_exactly_at_depth_limit(self) -> None:
        """Should accept structure exactly at depth limit."""
        data: any = 1
        for _ in range(MAX_JSON_DEPTH):
            data = {"nested": data}
        validate_json_depth(data)  # Should pass

    def test_exactly_at_size_limit(self) -> None:
        """Should accept collection exactly at size limit."""
        data = list(range(MAX_COLLECTION_SIZE))
        validate_collection_size(data)  # Should pass

    def test_unicode_strings(self) -> None:
        """Should handle unicode strings."""
        data = {"emoji": "🚀", "chinese": "你好", "arabic": "مرحبا"}
        validate_state_value(data)

    def test_mixed_types(self) -> None:
        """Should handle mixed types in collections."""
        data = {
            "string": "value",
            "number": 42,
            "float": 3.14,
            "bool": True,
            "null": None,
            "list": [1, "two", 3.0],
            "dict": {"nested": "data"},
        }
        validate_state_value(data)
