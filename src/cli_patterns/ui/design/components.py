"""Reusable UI components for CLI applications.

This module provides component token mappings using dataclasses for simplicity.
Each component class defines the default token mappings for consistent styling
across the CLI interface.
"""

from __future__ import annotations

from dataclasses import dataclass

from .tokens import CategoryToken, EmphasisToken, HierarchyToken, StatusToken


@dataclass
class Panel:
    """Token mappings for panel components."""

    border_category: CategoryToken = CategoryToken.CAT_1
    title_hierarchy: HierarchyToken = HierarchyToken.PRIMARY
    title_emphasis: EmphasisToken = EmphasisToken.STRONG
    content_emphasis: EmphasisToken = EmphasisToken.NORMAL


@dataclass
class ProgressBar:
    """Token mappings for progress indicators."""

    complete_status: StatusToken = StatusToken.SUCCESS
    running_status: StatusToken = StatusToken.RUNNING
    pending_status: StatusToken = StatusToken.MUTED
    bar_category: CategoryToken = CategoryToken.CAT_2


@dataclass
class Prompt:
    """Token mappings for interactive prompts."""

    symbol: str = "►"
    category: CategoryToken = CategoryToken.CAT_1
    emphasis: EmphasisToken = EmphasisToken.NORMAL
    error_status: StatusToken = StatusToken.ERROR


@dataclass
class Output:
    """Token mappings for command output."""

    stdout_emphasis: EmphasisToken = EmphasisToken.NORMAL
    stderr_status: StatusToken = StatusToken.ERROR
    debug_emphasis: EmphasisToken = EmphasisToken.SUBTLE
    info_status: StatusToken = StatusToken.INFO
