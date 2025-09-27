#!/usr/bin/env python3
"""Quick test of SubprocessExecutor's interactive features."""

import asyncio
from rich.console import Console
from cli_patterns.execution.subprocess_executor import SubprocessExecutor


async def main():
    """Test custom commands with SubprocessExecutor."""
    console = Console()
    executor = SubprocessExecutor(console=console)

    # Test a few custom commands
    commands = [
        ("pwd", None, None),
        ("echo 'Testing custom command'", None, None),
        ("ls -la | grep examples", None, None),
        ("date", None, None),
        ("echo 'VAR is: $TEST_VAR'", None, {"TEST_VAR": "Hello World!"}),
        ("python3 -c 'print(\"Python says hello!\")'", None, None),
    ]

    for cmd, timeout, env in commands:
        print(f"\n{'='*60}")
        print(f"Running: {cmd}")
        if env:
            print(f"With env: {env}")
        print('='*60)

        result = await executor.run(cmd, timeout=timeout, env=env)

        print(f"\nResult:")
        print(f"  Exit code: {result.exit_code}")
        print(f"  Success: {result.success}")
        if result.stdout:
            print(f"  Output: {result.stdout.strip()}")
        if result.stderr:
            print(f"  Error: {result.stderr.strip()}")


if __name__ == "__main__":
    asyncio.run(main())