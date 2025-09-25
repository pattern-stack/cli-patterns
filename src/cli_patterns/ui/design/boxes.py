"""Box components and layout utilities for CLI interfaces.

This module provides box drawing styles using dataclasses and predefined
box drawing character sets for different visual styles.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BoxStyle:
    """Box drawing characters for different styles."""

    top: str
    bottom: str
    left: str
    right: str
    top_left: str
    top_right: str
    bottom_left: str
    bottom_right: str
    horizontal_down: str
    horizontal_up: str
    vertical_right: str
    vertical_left: str
    cross: str


# Define standard box styles
ROUNDED = BoxStyle(
    top="─",
    bottom="─",
    left="│",
    right="│",
    top_left="╭",
    top_right="╮",
    bottom_left="╰",
    bottom_right="╯",
    horizontal_down="┬",
    horizontal_up="┴",
    vertical_right="├",
    vertical_left="┤",
    cross="┼",
)

HEAVY = BoxStyle(
    top="━",
    bottom="━",
    left="┃",
    right="┃",
    top_left="┏",
    top_right="┓",
    bottom_left="┗",
    bottom_right="┛",
    horizontal_down="┳",
    horizontal_up="┻",
    vertical_right="┣",
    vertical_left="┫",
    cross="╋",
)

ASCII = BoxStyle(
    top="-",
    bottom="-",
    left="|",
    right="|",
    top_left="+",
    top_right="+",
    bottom_left="+",
    bottom_right="+",
    horizontal_down="+",
    horizontal_up="+",
    vertical_right="+",
    vertical_left="+",
    cross="+",
)

DOUBLE = BoxStyle(
    top="═",
    bottom="═",
    left="║",
    right="║",
    top_left="╔",
    top_right="╗",
    bottom_left="╚",
    bottom_right="╝",
    horizontal_down="╦",
    horizontal_up="╩",
    vertical_right="╠",
    vertical_left="╣",
    cross="╬",
)

# Additional fancy box styles
MINIMAL = BoxStyle(
    top=" ",
    bottom=" ",
    left=" ",
    right=" ",
    top_left=" ",
    top_right=" ",
    bottom_left=" ",
    bottom_right=" ",
    horizontal_down=" ",
    horizontal_up=" ",
    vertical_right=" ",
    vertical_left=" ",
    cross=" ",
)

DOTS = BoxStyle(
    top="·",
    bottom="·",
    left=":",
    right=":",
    top_left="·",
    top_right="·",
    bottom_left="·",
    bottom_right="·",
    horizontal_down="·",
    horizontal_up="·",
    vertical_right=":",
    vertical_left=":",
    cross="·",
)

THICK = BoxStyle(
    top="▀",
    bottom="▄",
    left="▌",
    right="▐",
    top_left="▛",
    top_right="▜",
    bottom_left="▙",
    bottom_right="▟",
    horizontal_down="▀",
    horizontal_up="▄",
    vertical_right="▌",
    vertical_left="▐",
    cross="█",
)

SMOOTH = BoxStyle(
    top="─",
    bottom="─",
    left="│",
    right="│",
    top_left="╭",
    top_right="╮",
    bottom_left="╰",
    bottom_right="╯",
    horizontal_down="┬",
    horizontal_up="┴",
    vertical_right="├",
    vertical_left="┤",
    cross="┼",
)

DASHED = BoxStyle(
    top="╌",
    bottom="╌",
    left="╎",
    right="╎",
    top_left="┌",
    top_right="┐",
    bottom_left="└",
    bottom_right="┘",
    horizontal_down="┬",
    horizontal_up="┴",
    vertical_right="├",
    vertical_left="┤",
    cross="┼",
)

BOLD = BoxStyle(
    top="▬",
    bottom="▬",
    left="▮",
    right="▮",
    top_left="▬",
    top_right="▬",
    bottom_left="▬",
    bottom_right="▬",
    horizontal_down="▬",
    horizontal_up="▬",
    vertical_right="▮",
    vertical_left="▮",
    cross="▬",
)

BOX_STYLES = {
    "rounded": ROUNDED,
    "heavy": HEAVY,
    "ascii": ASCII,
    "double": DOUBLE,
    "minimal": MINIMAL,
    "dots": DOTS,
    "thick": THICK,
    "smooth": SMOOTH,
    "dashed": DASHED,
    "bold": BOLD,
}
