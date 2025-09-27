#!/bin/bash
set -e

# Install system dependencies quietly
apt-get update -qq
apt-get install -y -qq make > /dev/null 2>&1

# Install Python dependencies quietly
pip install -q -e . 2>/dev/null
pip install -q mypy pytest pytest-asyncio pytest-cov black ruff 2>/dev/null

# Execute the passed command
exec "$@"