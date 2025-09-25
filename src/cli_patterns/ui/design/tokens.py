"""Design tokens for consistent styling across CLI components.

This module provides semantic design tokens that enable consistent styling
and theming across all CLI interface components. The token system separates
concerns between visual styling and semantic meaning.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel


class CategoryToken(str, Enum):
    """Semantic categories for domain differentiation.

    These tokens are used to separate different domain objects and provide
    semantic meaning to UI elements beyond just visual appearance.
    """

    CAT_1 = "cat_1"
    CAT_2 = "cat_2"
    CAT_3 = "cat_3"
    CAT_4 = "cat_4"
    CAT_5 = "cat_5"
    CAT_6 = "cat_6"
    CAT_7 = "cat_7"
    CAT_8 = "cat_8"


class HierarchyToken(str, Enum):
    """Visual importance levels for content hierarchy.

    These tokens define the visual hierarchy of elements, helping users
    understand the relative importance and relationships between UI components.
    """

    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"
    QUATERNARY = "quaternary"


class StatusToken(str, Enum):
    """State-based colors for representing different conditions.

    These tokens provide semantic meaning for various states and conditions
    in the CLI interface, making it easy for users to understand system status.
    """

    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    MUTED = "muted"
    RUNNING = "running"


class EmphasisToken(str, Enum):
    """Visual weight levels for text emphasis.

    These tokens control the visual weight and emphasis of text elements,
    helping to create clear information hierarchies and draw attention
    to important content.
    """

    STRONG = "strong"
    NORMAL = "normal"
    SUBTLE = "subtle"


class DisplayMetadata(BaseModel):
    """Metadata for display styling without specific status information.

    This model represents the base styling metadata that can be applied
    to UI elements. It excludes status information, making it suitable
    for elements that don't have a specific state.
    """

    category: CategoryToken
    hierarchy: HierarchyToken = HierarchyToken.PRIMARY
    emphasis: EmphasisToken = EmphasisToken.NORMAL

    def with_status(self, status: StatusToken) -> DisplayStyle:
        """Create a DisplayStyle by adding status information.

        Args:
            status: The status token to apply to the display style.

        Returns:
            A new DisplayStyle instance with the specified status.
        """
        return DisplayStyle(
            category=self.category,
            hierarchy=self.hierarchy,
            emphasis=self.emphasis,
            status=status,
        )


class DisplayStyle(BaseModel):
    """Complete display styling information including optional status.

    This model represents the complete styling information for a UI element,
    including all visual hierarchy, emphasis, and optional status information.
    """

    category: CategoryToken
    hierarchy: HierarchyToken
    emphasis: EmphasisToken
    status: Optional[StatusToken] = None

    @classmethod
    def from_metadata(
        cls, metadata: DisplayMetadata, status: Optional[StatusToken] = None
    ) -> DisplayStyle:
        """Create a DisplayStyle from DisplayMetadata.

        Args:
            metadata: The base display metadata.
            status: Optional status token to apply.

        Returns:
            A new DisplayStyle instance.
        """
        return cls(
            category=metadata.category,
            hierarchy=metadata.hierarchy,
            emphasis=metadata.emphasis,
            status=status,
        )
