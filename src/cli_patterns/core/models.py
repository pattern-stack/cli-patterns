"""Core data models for CLI Patterns.

This module defines Pydantic models for the wizard configuration structure.
All models use MyPy strict mode and Pydantic v2 features including:
- Discriminated unions for extensibility
- Field validation
- JSON serialization/deserialization
- StrictModel base class for type safety
"""

from __future__ import annotations

from typing import Any, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

from cli_patterns.core.types import (
    ActionId,
    BranchId,
    MenuId,
    OptionKey,
)

# StateValue is defined as Any for Pydantic compatibility
# The actual type constraint (JSON-serializable) is enforced at serialization time
StateValue = Any


class StrictModel(BaseModel):
    """Base model with strict validation enabled.

    This ensures type safety and proper validation throughout the system.
    """

    model_config = ConfigDict(
        # Strict mode for type safety
        strict=True,
        # Allow arbitrary types (for semantic types)
        arbitrary_types_allowed=True,
        # Extra fields are forbidden
        extra="forbid",
    )


class BaseConfig(StrictModel):
    """Base configuration providing common fields for all config types.

    This class provides metadata and tagging infrastructure that all
    configuration types can use.
    """

    metadata: dict[str, Any] = Field(default_factory=dict)
    """Arbitrary metadata for extensions and tooling."""

    tags: list[str] = Field(default_factory=list)
    """Tags for categorization and filtering."""


# ============================================================================
# Action Configuration Models
# ============================================================================


class BashActionConfig(BaseConfig):
    """Configuration for bash command actions.

    Executes a bash command with optional environment variables.
    """

    type: Literal["bash"] = Field(
        default="bash", description="Action type discriminator"
    )
    id: ActionId = Field(description="Unique action identifier")
    name: str = Field(description="Human-readable action name")
    description: Optional[str] = Field(default=None, description="Action description")
    command: str = Field(description="Bash command to execute")
    env: dict[str, str] = Field(
        default_factory=dict, description="Environment variables for command"
    )


class PythonActionConfig(BaseConfig):
    """Configuration for Python function actions.

    Calls a Python function from a specified module.
    """

    type: Literal["python"] = Field(
        default="python", description="Action type discriminator"
    )
    id: ActionId = Field(description="Unique action identifier")
    name: str = Field(description="Human-readable action name")
    description: Optional[str] = Field(default=None, description="Action description")
    module: str = Field(description="Python module path")
    function: str = Field(description="Function name to call")


# Discriminated union of all action types
# TODO: Future extension point - add new action types here
ActionConfigUnion = Union[BashActionConfig, PythonActionConfig]


# ============================================================================
# Option Configuration Models
# ============================================================================


class StringOptionConfig(BaseConfig):
    """Configuration for string input options."""

    type: Literal["string"] = Field(
        default="string", description="Option type discriminator"
    )
    id: OptionKey = Field(description="Unique option identifier")
    name: str = Field(description="Human-readable option name")
    description: str = Field(description="Option description/prompt")
    default: Optional[str] = Field(default=None, description="Default value")
    required: bool = Field(default=False, description="Whether option is required")


class SelectOptionConfig(BaseConfig):
    """Configuration for selection options (dropdown/menu)."""

    type: Literal["select"] = Field(
        default="select", description="Option type discriminator"
    )
    id: OptionKey = Field(description="Unique option identifier")
    name: str = Field(description="Human-readable option name")
    description: str = Field(description="Option description/prompt")
    choices: list[str] = Field(description="Available choices")
    default: Optional[str] = Field(default=None, description="Default value")
    required: bool = Field(default=False, description="Whether option is required")


class PathOptionConfig(BaseConfig):
    """Configuration for file/directory path options."""

    type: Literal["path"] = Field(
        default="path", description="Option type discriminator"
    )
    id: OptionKey = Field(description="Unique option identifier")
    name: str = Field(description="Human-readable option name")
    description: str = Field(description="Option description/prompt")
    must_exist: bool = Field(
        default=False, description="Whether path must exist for validation"
    )
    default: Optional[str] = Field(default=None, description="Default value")
    required: bool = Field(default=False, description="Whether option is required")


class NumberOptionConfig(BaseConfig):
    """Configuration for numeric input options."""

    type: Literal["number"] = Field(
        default="number", description="Option type discriminator"
    )
    id: OptionKey = Field(description="Unique option identifier")
    name: str = Field(description="Human-readable option name")
    description: str = Field(description="Option description/prompt")
    min_value: Optional[float] = Field(
        default=None, description="Minimum allowed value"
    )
    max_value: Optional[float] = Field(
        default=None, description="Maximum allowed value"
    )
    default: Optional[float] = Field(default=None, description="Default value")
    required: bool = Field(default=False, description="Whether option is required")


class BooleanOptionConfig(BaseConfig):
    """Configuration for boolean (yes/no) options."""

    type: Literal["boolean"] = Field(
        default="boolean", description="Option type discriminator"
    )
    id: OptionKey = Field(description="Unique option identifier")
    name: str = Field(description="Human-readable option name")
    description: str = Field(description="Option description/prompt")
    default: Optional[bool] = Field(default=None, description="Default value")
    required: bool = Field(default=False, description="Whether option is required")


# Discriminated union of all option types
# TODO: Future extension point - add new option types here (e.g., multi-select, date, etc.)
OptionConfigUnion = Union[
    StringOptionConfig,
    SelectOptionConfig,
    PathOptionConfig,
    NumberOptionConfig,
    BooleanOptionConfig,
]


# ============================================================================
# Menu and Navigation Configuration
# ============================================================================


class MenuConfig(StrictModel):
    """Configuration for navigation menu items.

    Menus allow tree-based navigation between branches.
    """

    id: MenuId = Field(description="Unique menu identifier")
    label: str = Field(description="Menu item label displayed to user")
    target: BranchId = Field(description="Target branch to navigate to")
    description: Optional[str] = Field(
        default=None, description="Optional menu description"
    )


# ============================================================================
# Branch Configuration
# ============================================================================


class BranchConfig(BaseConfig):
    """Configuration for a wizard branch.

    A branch represents a screen/step in the wizard with actions, options,
    and navigation menus.
    """

    id: BranchId = Field(description="Unique branch identifier")
    title: str = Field(description="Branch title displayed to user")
    description: Optional[str] = Field(default=None, description="Branch description")
    actions: list[ActionConfigUnion] = Field(
        default_factory=list, description="Actions available in this branch"
    )
    options: list[OptionConfigUnion] = Field(
        default_factory=list, description="Options to collect in this branch"
    )
    menus: list[MenuConfig] = Field(
        default_factory=list, description="Navigation menus in this branch"
    )


# ============================================================================
# Wizard Configuration
# ============================================================================


class WizardConfig(BaseConfig):
    """Complete wizard configuration.

    This is the top-level configuration that defines an entire wizard,
    including all branches and the entry point.
    """

    name: str = Field(description="Wizard name (identifier)")
    version: str = Field(description="Wizard version (semver recommended)")
    description: Optional[str] = Field(default=None, description="Wizard description")
    entry_branch: BranchId = Field(
        description="Initial branch to display when wizard starts"
    )
    branches: list[BranchConfig] = Field(description="All branches in the wizard tree")

    # TODO: Add validator to ensure entry_branch exists in branches
    # This would be done with @model_validator in Pydantic v2


# ============================================================================
# Session State
# ============================================================================


class SessionState(StrictModel):
    """Unified session state for wizard and parser.

    This model combines both wizard state (navigation, options) and
    parser state (mode, history) into a single unified state.
    """

    # Wizard state
    current_branch: Optional[BranchId] = Field(
        default=None, description="Currently active branch"
    )
    navigation_history: list[BranchId] = Field(
        default_factory=list, description="Branch navigation history for 'back' command"
    )
    option_values: dict[OptionKey, StateValue] = Field(
        default_factory=dict, description="Collected option values"
    )

    # Shared state
    variables: dict[str, StateValue] = Field(
        default_factory=dict,
        description="Variables for interpolation (e.g., ${var} in commands)",
    )

    # Parser state
    parse_mode: str = Field(default="interactive", description="Current parsing mode")
    command_history: list[str] = Field(
        default_factory=list, description="Command history for readline/recall"
    )


# ============================================================================
# Result Types
# ============================================================================


class ActionResult(StrictModel):
    """Result from executing an action.

    Contains success status, output, and error information.
    """

    action_id: ActionId = Field(description="ID of executed action")
    success: bool = Field(description="Whether action succeeded")
    output: str = Field(default="", description="Action output (stdout)")
    exit_code: int = Field(default=0, description="Exit code (for bash actions)")
    error: Optional[str] = Field(default=None, description="Error message if failed")


class CollectionResult(StrictModel):
    """Result from collecting an option value.

    Contains the collected value or error information.
    """

    option_key: OptionKey = Field(description="Key of option being collected")
    success: bool = Field(description="Whether collection succeeded")
    value: Optional[StateValue] = Field(
        default=None, description="Collected value if successful"
    )
    error: Optional[str] = Field(
        default=None, description="Error message if collection failed"
    )


class NavigationResult(StrictModel):
    """Result from a navigation operation.

    Contains target branch and success/error information.
    """

    success: bool = Field(description="Whether navigation succeeded")
    target: BranchId = Field(description="Target branch")
    error: Optional[str] = Field(
        default=None, description="Error message if navigation failed"
    )
