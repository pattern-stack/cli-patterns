"""Pytest configuration for CLI Patterns tests."""

import pytest


def pytest_collection_modifyitems(config, items):
    """Automatically add markers based on test file location."""
    for item in items:
        # Add unit/integration markers based on path
        if "tests/unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "tests/integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)

        # Add component markers based on path
        if "parser" in str(item.fspath):
            item.add_marker(pytest.mark.parser)
        elif "executor" in str(item.fspath) or "execution" in str(item.fspath):
            item.add_marker(pytest.mark.executor)
        elif "design" in str(item.fspath):
            item.add_marker(pytest.mark.design)
