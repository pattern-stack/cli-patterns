#!/bin/bash
set -euo pipefail

# Install system dependencies with error handling
if ! apt-get update -qq; then
    echo "Error: Failed to update package lists" >&2
    exit 1
fi

if ! apt-get install -y -qq make > /dev/null 2>&1; then
    echo "Error: Failed to install make" >&2
    exit 1
fi

# Install Python dependencies with error handling
if ! pip install -q -e . 2>/dev/null; then
    echo "Error: Failed to install package" >&2
    exit 1
fi

if ! pip install -q mypy pytest pytest-asyncio pytest-cov black ruff 2>/dev/null; then
    echo "Error: Failed to install development dependencies" >&2
    exit 1
fi

# Execute the passed command
exec "$@"