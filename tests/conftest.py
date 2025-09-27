"""Test configuration and auto-marking for pytest."""

import pytest


def pytest_collection_modifyitems(config, items):
    """Auto-mark tests based on their location."""
    for item in items:
        # Path-based markers
        if "tests/unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "tests/integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)

        # Component-based markers
        if "/parser/" in str(item.fspath):
            item.add_marker(pytest.mark.parser)
        elif "/execution/" in str(item.fspath) or "subprocess" in item.name:
            item.add_marker(pytest.mark.executor)
        elif "/design/" in str(item.fspath):
            item.add_marker(pytest.mark.design)
        elif "/ui/" in str(item.fspath):
            item.add_marker(pytest.mark.ui)