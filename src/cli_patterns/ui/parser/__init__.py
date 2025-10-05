"""Parser system for command-line input processing.

This module provides a comprehensive system for parsing user input into
structured command data, including support for:

- Text commands with flags and options
- Shell commands with pass-through execution
- Command registration and metadata management
- Parser pipelines for routing input to appropriate parsers
- Intelligent suggestion generation for typos and completions

Core Types:
    ParseResult: Structured result of parsing user input
    CommandArgs: Container for positional and named arguments
    ParseError: Exception raised during parsing failures

Note:
    The parser system now uses SessionState from cli_patterns.core.models
    instead of a parser-specific Context type for unified state management.

Protocols:
    Parser: Protocol for implementing custom parsers

Parsers:
    TextParser: Handles standard text commands with flags/options
    ShellParser: Handles shell commands prefixed with '!'

Pipeline:
    ParserPipeline: Routes input to appropriate parsers based on conditions

Registry:
    CommandRegistry: Manages available commands and provides suggestions
    CommandMetadata: Metadata for registered commands
"""

from cli_patterns.ui.parser.parsers import ShellParser, TextParser
from cli_patterns.ui.parser.pipeline import ParserPipeline
from cli_patterns.ui.parser.protocols import Parser
from cli_patterns.ui.parser.registry import CommandMetadata, CommandRegistry
from cli_patterns.ui.parser.types import CommandArgs, ParseError, ParseResult

# NOTE: SessionState is now imported from core.models instead of parser.types
# Import it from core if you need the unified session state:
#   from cli_patterns.core.models import SessionState

__all__ = [
    # Core Types
    "ParseResult",
    "CommandArgs",
    "ParseError",
    # Protocols
    "Parser",
    # Parsers
    "TextParser",
    "ShellParser",
    # Pipeline
    "ParserPipeline",
    # Registry
    "CommandRegistry",
    "CommandMetadata",
]
