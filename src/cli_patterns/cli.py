"""Main CLI entry point for CLI Patterns."""

from __future__ import annotations

import sys


def main() -> None:
    """Main entry point for the CLI Patterns interactive shell."""
    try:
        from .ui.shell import run_shell
        run_shell()
    except ImportError as e:
        print(f"Error: Failed to import required modules: {e}")
        print("Please ensure all dependencies are installed: pip install -e .")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterrupted")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
