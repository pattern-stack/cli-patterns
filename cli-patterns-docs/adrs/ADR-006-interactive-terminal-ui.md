# ADR-006: Interactive Terminal UI with prompt_toolkit

## Status
Accepted

## Context
CLI Patterns is designed as an interactive wizard system that users launch and operate within, not a one-shot command-line tool. We need a framework that supports:
1. Long-running interactive sessions
2. Stateful navigation between branches
3. Rich terminal UI elements (menus, prompts, completions)
4. Async operation support
5. Type-safe integration with our protocol-based design

We evaluated several options:
- **Click/Typer**: Designed for one-shot command execution, not interactive shells
- **cmd/cmd2**: Basic interactive shells but limited UI capabilities
- **Rich/Textual**: Modern but potentially overly complex for MVP
- **prompt_toolkit**: Purpose-built for interactive terminal applications

## Decision
We will use **prompt_toolkit** as the framework for implementing our interactive terminal UI. This will be the primary implementation of the `UIRenderer` protocol defined in ADR-004.

## Consequences

### Positive
- **Purpose-built**: Specifically designed for interactive terminal applications
- **Rich interactions**: Built-in support for menus, completions, multi-line editing
- **Async support**: Native async/await compatibility with our execution model
- **Proven**: Powers IPython, pgcli, and other major interactive tools
- **Flexible**: Can start simple and add sophistication gradually
- **State management**: Natural fit for maintaining `SessionState` during interaction

### Negative
- **Additional dependency**: Adds prompt_toolkit to our dependency list
- **Learning curve**: Developers need to understand prompt_toolkit patterns
- **Terminal-specific**: Ties this implementation to terminal (not a web UI)

### Neutral
- This is an implementation of the UIRenderer protocol, not a core dependency
- Other UI implementations can be added later (web, TUI, etc.)

## Implementation

### Interactive Session Flow
```python
# User launches the wizard
$ cli-patterns my-wizard

# Enters interactive mode
Welcome to MyWizard v1.0.0
Type 'help' for available commands, 'quit' to exit

wizard[main]> list actions
Available actions:
  1. setup - Setup environment
  2. config - Configure database
  3. test - Run tests

wizard[main]> run setup
Executing: Setup environment...
✓ Environment configured successfully

wizard[main]> navigate config
→ Entering branch: configuration

wizard[config]> back
← Returning to: main

wizard[main]> quit
Goodbye!
```

### UIRenderer Implementation
```python
from prompt_toolkit import Application
from prompt_toolkit.shortcuts import prompt
from prompt_toolkit.completion import WordCompleter
from typing import Dict, List, Optional

class InteractiveUIRenderer:
    """prompt_toolkit implementation of UIRenderer protocol."""

    def __init__(self):
        self.session = PromptSession()
        self.current_branch = None

    async def render_branch(
        self,
        branch: BranchConfig,
        state: SessionState
    ) -> None:
        """Display branch information and available actions."""
        self.current_branch = branch
        print(f"\n═══ {branch.name} ═══")
        if branch.description:
            print(f"{branch.description}\n")

    async def collect_options(
        self,
        options: List[OptionConfigUnion],
        state: SessionState
    ) -> Dict[OptionKey, StateValue]:
        """Interactively collect options with validation."""
        results = {}
        for option in options:
            if option.type == "select":
                completer = WordCompleter(option.choices)
                value = await prompt(
                    f"{option.prompt}: ",
                    completer=completer
                )
            else:
                value = await prompt(f"{option.prompt}: ")

            results[option.key] = value
        return results

    async def show_menu(
        self,
        menus: List[MenuConfig],
        state: SessionState
    ) -> Optional[MenuId]:
        """Display interactive menu for navigation."""
        # Build menu with numbers
        for i, menu in enumerate(menus, 1):
            print(f"{i}. {menu.label}")

        choice = await prompt("Select option: ")
        # Return selected menu ID
```

### Integration with Execution Engine
```python
class InteractiveExecutionEngine:
    def __init__(self, wizard: WizardConfig):
        self.wizard = wizard
        self.ui = InteractiveUIRenderer()
        self.state = SessionState()

    async def run_interactive(self):
        """Main interactive loop."""
        app = Application(
            layout=self.create_layout(),
            key_bindings=self.create_keybindings(),
            full_screen=False
        )
        await app.run_async()
```

## Future Considerations
- Could add Rich for enhanced formatting within prompt_toolkit
- May want to support vi/emacs key bindings
- Could implement command history persistence
- Potential for custom themes/styling

## Migration Path
If we need to migrate away from prompt_toolkit:
1. The UIRenderer protocol insulates core logic
2. Create new implementation of UIRenderer
3. Swap implementation via dependency injection
4. No changes needed to wizard definitions or execution engine

## References
- ADR-004: Branch-Level UI Protocol
- prompt_toolkit documentation: https://python-prompt-toolkit.readthedocs.io/
- Discussion on interactive vs one-shot CLI design