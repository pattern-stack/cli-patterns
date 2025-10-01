"""Core data models for CLI Patterns.

This module defines Pydantic models for the wizard configuration structure.
All models use MyPy strict mode and Pydantic v2 features including:
- Discriminated unions for extensibility
- Field validation
- JSON serialization/deserialization
- StrictModel base class for type safety
"""

from __future__ import annotations

import re
from typing import Any, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from cli_patterns.core.types import (
    ActionId,
    BranchId,
    MenuId,
    OptionKey,
)
from cli_patterns.core.validators import ValidationError, validate_state_value

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

    Security:
        By default, shell features (pipes, redirects, command substitution) are
        disabled to prevent command injection attacks. Set allow_shell_features=True
        only for trusted commands that require shell features.
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
    allow_shell_features: bool = Field(
        default=False,
        description=(
            "Allow shell features (pipes, redirects, command substitution). "
            "SECURITY RISK: Only enable for trusted commands. When False, "
            "command is executed without shell interpretation to prevent injection."
        ),
    )

    @model_validator(mode="after")
    def validate_command_safety(self) -> BashActionConfig:
        """Validate command doesn't contain dangerous patterns.

        This validator blocks shell injection attempts when allow_shell_features=False.

        Returns:
            Validated model

        Raises:
            ValueError: If command contains dangerous shell metacharacters
        """
        if not self.allow_shell_features:
            # Dangerous shell metacharacters
            dangerous_patterns = [
                (r"[;&|]", "command chaining (;, &, |)"),
                (r"`", "command substitution (backticks)"),
                (r"\$\(", "command substitution ($())"),
                (r"[<>]", "redirection (<, >)"),
                (r"\$\{", "variable expansion (${})"),
                (r"^\s*\w+\s*=", "variable assignment"),
            ]

            for pattern, description in dangerous_patterns:
                if re.search(pattern, self.command):
                    raise ValueError(
                        f"Command contains {description}. "
                        f"Set allow_shell_features=True to enable shell features "
                        f"(SECURITY RISK: only do this for trusted commands)."
                    )

        return self


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

    Limits:
        - Actions: 100 maximum
        - Options: 50 maximum
        - Menus: 20 maximum
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

    @field_validator("actions")
    @classmethod
    def validate_actions_size(
        cls, v: list[ActionConfigUnion]
    ) -> list[ActionConfigUnion]:
        """Validate number of actions is reasonable."""
        if len(v) > 100:
            raise ValueError("Too many actions in branch (maximum: 100)")
        return v

    @field_validator("options")
    @classmethod
    def validate_options_size(
        cls, v: list[OptionConfigUnion]
    ) -> list[OptionConfigUnion]:
        """Validate number of options is reasonable."""
        if len(v) > 50:
            raise ValueError("Too many options in branch (maximum: 50)")
        return v

    @field_validator("menus")
    @classmethod
    def validate_menus_size(cls, v: list[MenuConfig]) -> list[MenuConfig]:
        """Validate number of menus is reasonable."""
        if len(v) > 20:
            raise ValueError("Too many menus in branch (maximum: 20)")
        return v


# ============================================================================
# Wizard Configuration
# ============================================================================


class WizardConfig(BaseConfig):
    """Complete wizard configuration.

    This is the top-level configuration that defines an entire wizard,
    including all branches and the entry point.

    Limits:
        - Branches: 100 maximum
    """

    name: str = Field(description="Wizard name (identifier)")
    version: str = Field(description="Wizard version (semver recommended)")
    description: Optional[str] = Field(default=None, description="Wizard description")
    entry_branch: BranchId = Field(
        description="Initial branch to display when wizard starts"
    )
    branches: list[BranchConfig] = Field(description="All branches in the wizard tree")

    @field_validator("branches")
    @classmethod
    def validate_branches_size(cls, v: list[BranchConfig]) -> list[BranchConfig]:
        """Validate number of branches is reasonable."""
        if len(v) > 100:
            raise ValueError("Too many branches in wizard (maximum: 100)")
        return v

    @model_validator(mode="after")
    def validate_entry_branch_exists(self) -> WizardConfig:
        """Validate that entry_branch exists in branches list."""
        branch_ids = {b.id for b in self.branches}
        if self.entry_branch not in branch_ids:
            raise ValueError(
                f"entry_branch '{self.entry_branch}' not found in branches. "
                f"Available branches: {sorted(branch_ids)}"
            )
        return self


# ============================================================================
# Session State
# ============================================================================


class SessionState(StrictModel):
    """Unified session state for wizard and parser.

    This model combines both wizard state (navigation, options) and
    parser state (mode, history) into a single unified state.

    Security:
        All StateValue fields (option_values, variables) are validated for:
        - Maximum nesting depth (50 levels)
        - Maximum collection size (1000 items)
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

    @field_validator("option_values")
    @classmethod
    def validate_option_values(
        cls, v: dict[OptionKey, StateValue]
    ) -> dict[OptionKey, StateValue]:
        """Validate all option values meet safety requirements.

        Checks each value for:
        - Maximum nesting depth (50 levels)
        - Maximum collection size (1000 items)

        Args:
            v: Option values dict to validate

        Returns:
            Validated dict

        Raises:
            ValueError: If any value violates safety limits
        """
        # Check total number of options
        if len(v) > 1000:
            raise ValueError("Too many options (maximum: 1000)")

        # Validate each value
        for key, value in v.items():
            try:
                validate_state_value(value)
            except ValidationError as e:
                raise ValueError(f"Invalid value for option '{key}': {e}") from e

        return v

    @field_validator("variables")
    @classmethod
    def validate_variables(cls, v: dict[str, StateValue]) -> dict[str, StateValue]:
        """Validate all variables meet safety requirements.

        Checks each value for:
        - Maximum nesting depth (50 levels)
        - Maximum collection size (1000 items)

        Args:
            v: Variables dict to validate

        Returns:
            Validated dict

        Raises:
            ValueError: If any value violates safety limits
        """
        if len(v) > 1000:
            raise ValueError("Too many variables (maximum: 1000)")

        for key, value in v.items():
            try:
                validate_state_value(value)
            except ValidationError as e:
                raise ValueError(f"Invalid value for variable '{key}': {e}") from e

        return v


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
