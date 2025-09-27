#!/usr/bin/env python3
"""Interactive demo script showing SubprocessExecutor functionality."""

import asyncio
import sys
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.text import Text
from cli_patterns.execution.subprocess_executor import SubprocessExecutor


def wait_for_enter(message="Press Enter to continue..."):
    """Wait for user to press enter."""
    input(f"\n{message}")


async def run_example(executor, title, explanation, command, **kwargs):
    """Run an example command with title and wait for user."""
    print(f"\n{title}")
    print(f"What this will do: {explanation}")
    print(f"Command: {command}")
    print("-" * 50)

    result = await executor.run(command, **kwargs)

    print("\nResult Summary:")
    print(f"  Exit code: {result.exit_code}")
    print(f"  Success: {result.success}")
    if result.timed_out:
        print(f"  Timed out: True")
    if result.interrupted:
        print(f"  Interrupted: True")
    if result.stderr and not result.success:
        print(f"  Error: {result.stderr[:100]}...")

    wait_for_enter()
    return result


async def user_command_loop(executor, console):
    """Allow user to run custom commands."""
    console.print(Panel.fit(
        "[bold cyan]Interactive Command Mode[/bold cyan]\n"
        "Enter commands to run them with the SubprocessExecutor.\n"
        "Type 'exit' or 'quit' to leave.",
        border_style="cyan"
    ))

    while True:
        print()
        command = Prompt.ask("[bold green]Enter command[/bold green]", default="exit")

        if command.lower() in ['exit', 'quit']:
            break

        # Ask for optional parameters
        use_timeout = Confirm.ask("Set a custom timeout?", default=False)
        timeout = None
        if use_timeout:
            timeout = float(Prompt.ask("Timeout (seconds)", default="30"))

        use_env = Confirm.ask("Add environment variables?", default=False)
        env = None
        if use_env:
            env_vars = {}
            console.print("[dim]Enter variables as KEY=VALUE, empty to finish[/dim]")
            while True:
                var = Prompt.ask("Environment variable", default="")
                if not var:
                    break
                if '=' in var:
                    key, value = var.split('=', 1)
                    env_vars[key] = value
            if env_vars:
                env = env_vars

        print("\n" + "=" * 50)
        print(f"What this will do: Execute '{command}'")
        if timeout:
            print(f"  with timeout of {timeout} seconds")
        if env:
            print(f"  with environment variables: {env}")
        print("Executing now...")
        print("=" * 50)
        result = await executor.run(command, timeout=timeout, env=env)
        print("=" * 50)

        print(f"\nExit code: {result.exit_code}")
        print(f"Success: {result.success}")

        if result.stdout:
            show_output = Confirm.ask("Show full stdout?", default=True)
            if show_output:
                console.print(Panel(result.stdout, title="stdout", border_style="green"))

        if result.stderr:
            console.print(Panel(result.stderr, title="stderr", border_style="red"))


async def main():
    """Run subprocess executor demonstrations."""
    console = Console()
    executor = SubprocessExecutor(console=console)

    console.print(Panel.fit(
        Text("SubprocessExecutor Interactive Demo", justify="center", style="bold magenta"),
        subtitle="Learn how CLI-9 works",
        border_style="magenta"
    ))

    console.print("\n[bold]This demo will show you:[/bold]")
    console.print("• Running successful commands")
    console.print("• Handling command failures")
    console.print("• Timeout management")
    console.print("• Output capture")
    console.print("• Custom environments")
    console.print("• Concurrent execution")
    console.print("• Interactive command mode\n")

    wait_for_enter("Press Enter to start the demo...")

    # Example 1: Simple successful command
    await run_example(
        executor,
        "Example 1: Running a successful command",
        "List the first 5 files in the current directory with details",
        "ls -la | head -5"
    )

    # Example 2: Command that fails
    await run_example(
        executor,
        "Example 2: Running a command that fails",
        "Attempt to list a directory that doesn't exist to see error handling",
        "ls /nonexistent/directory"
    )

    # Example 3: Command with timeout
    await run_example(
        executor,
        "Example 3: Running a command with timeout (1 second)",
        "Run a 5-second sleep command but timeout after 1 second",
        "sleep 5",
        timeout=1.0
    )

    # Example 4: Capturing output
    await run_example(
        executor,
        "Example 4: Capturing command output",
        "Echo a message and capture its output for programmatic use",
        "echo 'Hello from subprocess!'"
    )

    # Example 5: Running with custom environment
    await run_example(
        executor,
        "Example 5: Running with custom environment variable",
        "Set a custom environment variable and echo its value",
        "echo 'MY_CUSTOM_VAR=$MY_CUSTOM_VAR'",
        env={"MY_CUSTOM_VAR": "Custom Value!"}
    )

    # Example 6: Running multiple commands concurrently
    print("\nExample 6: Running multiple commands concurrently")
    print("What this will do: Execute 3 commands in parallel with different sleep times")
    print("Expected behavior: All tasks start together, finish at different times")
    print("Commands: Three echo commands with different delays")
    print("-" * 50)

    tasks = [
        executor.run("echo 'Task 1 running' && sleep 0.5 && echo 'Task 1 done'"),
        executor.run("echo 'Task 2 running' && sleep 0.3 && echo 'Task 2 done'"),
        executor.run("echo 'Task 3 running' && sleep 0.1 && echo 'Task 3 done'"),
    ]

    console.print("[yellow]Starting 3 parallel tasks...[/yellow]")
    results = await asyncio.gather(*tasks)

    print("\nAll tasks completed!")
    for i, result in enumerate(results, 1):
        lines = result.stdout.strip().split('\n')
        print(f"  Task {i}: {lines[-1] if lines else 'No output'}")

    wait_for_enter()

    # Interactive mode
    console.print("\n[bold yellow]Ready to try your own commands?[/bold yellow]")
    if Confirm.ask("Enter interactive mode?", default=True):
        await user_command_loop(executor, console)

    console.print(Panel.fit(
        "[bold green]Demo Complete![/bold green]\n"
        "You've learned how the SubprocessExecutor works.\n"
        "Use it in your CLI patterns for async command execution.",
        border_style="green"
    ))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user. Goodbye!")