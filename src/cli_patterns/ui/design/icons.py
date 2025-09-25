"""Icon utilities and definitions for CLI interfaces.

This module provides icon sets for different display modes and terminal
capabilities, with fallback logic for maximum compatibility.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class IconSet:
    """Icon mappings for different display modes."""

    success: str
    error: str
    warning: str
    info: str
    running: str
    folder: str
    file: str
    arrow_right: str
    arrow_down: str
    check: str
    cross: str
    bullet: str


EMOJI_ICONS = IconSet(
    success="✅",
    error="❌",
    warning="⚠️",
    info="ℹ️",
    running="🔄",
    folder="📁",
    file="📄",
    arrow_right="➡️",
    arrow_down="⬇️",
    check="✓",
    cross="✗",
    bullet="•",
)

UNICODE_ICONS = IconSet(
    success="✓",
    error="✗",
    warning="⚠",
    info="ⓘ",
    running="◉",
    folder="▸",
    file="▪",
    arrow_right="→",
    arrow_down="↓",
    check="✓",
    cross="✗",
    bullet="•",
)

ASCII_ICONS = IconSet(
    success="[OK]",
    error="[X]",
    warning="[!]",
    info="[i]",
    running="[*]",
    folder=">",
    file="-",
    arrow_right="->",
    arrow_down="v",
    check="[v]",
    cross="[x]",
    bullet="*",
)

NERD_FONT_ICONS = IconSet(
    success="",
    error="",
    warning="",
    info="",
    running="",
    folder="",
    file="",
    arrow_right="",
    arrow_down="",
    check="",
    cross="",
    bullet="",
)

ICON_SETS = {
    "emoji": EMOJI_ICONS,
    "unicode": UNICODE_ICONS,
    "ascii": ASCII_ICONS,
    "nerd": NERD_FONT_ICONS,
}


def get_icon_set(preference_order: list[str] | None = None) -> IconSet:
    """Get best available icon set with fallback.

    Args:
        preference_order: List of icon set names in order of preference.
                         If None, defaults to ["emoji", "unicode", "ascii"].

    Returns:
        The best available icon set, falling back to ASCII_ICONS if
        no preference matches.
    """
    if preference_order is None:
        preference_order = ["emoji", "unicode", "ascii"]

    # In real implementation, would check terminal capabilities
    # For now, just return first preference
    for pref in preference_order:
        if pref in ICON_SETS:
            return ICON_SETS[pref]
    return ASCII_ICONS
