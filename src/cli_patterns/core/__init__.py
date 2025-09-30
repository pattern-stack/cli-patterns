"""Core types and protocols for CLI Patterns.

This module provides the foundational type system for the CLI Patterns framework:

Types:
    - Semantic types: BranchId, ActionId, OptionKey, MenuId
    - State value types: StateValue (JSON-serializable)
    - Type guards and factory functions

Models:
    - Configuration models: WizardConfig, BranchConfig, MenuConfig
    - Action models: BashActionConfig, PythonActionConfig
    - Option models: StringOptionConfig, SelectOptionConfig, etc.
    - State models: SessionState
    - Result models: ActionResult, CollectionResult, NavigationResult

Protocols:
    - ActionExecutor: For executing actions
    - OptionCollector: For collecting option values
    - NavigationController: For navigation control
"""

# Semantic types and utilities
# Configuration models
from cli_patterns.core.models import (
    ActionConfigUnion,
    ActionResult,
    BaseConfig,
    BashActionConfig,
    BooleanOptionConfig,
    BranchConfig,
    CollectionResult,
    MenuConfig,
    NavigationResult,
    NumberOptionConfig,
    OptionConfigUnion,
    PathOptionConfig,
    PythonActionConfig,
    SelectOptionConfig,
    SessionState,
    StringOptionConfig,
    WizardConfig,
)

# Protocols
from cli_patterns.core.protocols import (
    ActionExecutor,
    NavigationController,
    OptionCollector,
)
from cli_patterns.core.types import (
    ActionId,
    ActionList,
    ActionSet,
    BranchId,
    BranchList,
    BranchSet,
    MenuId,
    MenuList,
    OptionDict,
    OptionKey,
    StateValue,
    is_action_id,
    is_branch_id,
    is_menu_id,
    is_option_key,
    make_action_id,
    make_branch_id,
    make_menu_id,
    make_option_key,
)

__all__ = [
    # Types
    "ActionId",
    "ActionList",
    "ActionSet",
    "BranchId",
    "BranchList",
    "BranchSet",
    "MenuId",
    "MenuList",
    "OptionDict",
    "OptionKey",
    "StateValue",
    "is_action_id",
    "is_branch_id",
    "is_menu_id",
    "is_option_key",
    "make_action_id",
    "make_branch_id",
    "make_menu_id",
    "make_option_key",
    # Models
    "ActionConfigUnion",
    "ActionResult",
    "BaseConfig",
    "BashActionConfig",
    "BooleanOptionConfig",
    "BranchConfig",
    "CollectionResult",
    "MenuConfig",
    "NavigationResult",
    "NumberOptionConfig",
    "OptionConfigUnion",
    "PathOptionConfig",
    "PythonActionConfig",
    "SelectOptionConfig",
    "SessionState",
    "StringOptionConfig",
    "WizardConfig",
    # Protocols
    "ActionExecutor",
    "NavigationController",
    "OptionCollector",
]
