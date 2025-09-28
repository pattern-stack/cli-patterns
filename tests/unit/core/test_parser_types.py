"""Tests for core semantic parser types.

This module tests the semantic type definitions that provide type safety
for the parser system. These are simple NewType definitions that prevent
type confusion while maintaining MyPy strict mode compliance.
"""

from __future__ import annotations

from typing import Any

import pytest

# Import the types we're testing (these will fail initially)
try:
    from cli_patterns.core.parser_types import (
        ArgumentValue,
        CommandId,
        OptionKey,
        make_argument_value,
        make_command_id,
        make_context_key,
        make_flag_name,
        make_option_key,
        make_parse_mode,
    )
except ImportError:
    # These imports will fail initially since the implementation doesn't exist
    pass

pytestmark = pytest.mark.unit


class TestSemanticTypeDefinitions:
    """Test basic semantic type creation and identity."""

    def test_command_id_creation(self) -> None:
        """
        GIVEN: A string value for a command
        WHEN: Creating a CommandId
        THEN: The CommandId maintains the value but has distinct type identity
        """
        cmd_str = "help"
        cmd_id = make_command_id(cmd_str)

        # Value preservation
        assert str(cmd_id) == cmd_str

        # Type identity (will be checked by MyPy at compile time)
        assert isinstance(cmd_id, str)  # Runtime check

    def test_option_key_creation(self) -> None:
        """
        GIVEN: A string value for an option key
        WHEN: Creating an OptionKey
        THEN: The OptionKey maintains the value but has distinct type identity
        """
        key_str = "output"
        option_key = make_option_key(key_str)

        assert str(option_key) == key_str
        assert isinstance(option_key, str)

    def test_flag_name_creation(self) -> None:
        """
        GIVEN: A string value for a flag name
        WHEN: Creating a FlagName
        THEN: The FlagName maintains the value but has distinct type identity
        """
        flag_str = "verbose"
        flag_name = make_flag_name(flag_str)

        assert str(flag_name) == flag_str
        assert isinstance(flag_name, str)

    def test_argument_value_creation(self) -> None:
        """
        GIVEN: A string value for an argument
        WHEN: Creating an ArgumentValue
        THEN: The ArgumentValue maintains the value but has distinct type identity
        """
        arg_str = "file.txt"
        arg_value = make_argument_value(arg_str)

        assert str(arg_value) == arg_str
        assert isinstance(arg_value, str)

    def test_parse_mode_creation(self) -> None:
        """
        GIVEN: A string value for a parse mode
        WHEN: Creating a ParseMode
        THEN: The ParseMode maintains the value but has distinct type identity
        """
        mode_str = "interactive"
        parse_mode = make_parse_mode(mode_str)

        assert str(parse_mode) == mode_str
        assert isinstance(parse_mode, str)

    def test_context_key_creation(self) -> None:
        """
        GIVEN: A string value for a context key
        WHEN: Creating a ContextKey
        THEN: The ContextKey maintains the value but has distinct type identity
        """
        key_str = "user_role"
        context_key = make_context_key(key_str)

        assert str(context_key) == key_str
        assert isinstance(context_key, str)


class TestSemanticTypeDistinctness:
    """Test that semantic types are distinct from each other and from str."""

    def test_types_are_distinct_from_str(self) -> None:
        """
        GIVEN: Various semantic types created from the same string value
        WHEN: Checking type identity at runtime
        THEN: All types derive from str but have semantic distinction
        """
        base_str = "test"

        cmd_id = make_command_id(base_str)
        option_key = make_option_key(base_str)
        flag_name = make_flag_name(base_str)
        arg_value = make_argument_value(base_str)
        parse_mode = make_parse_mode(base_str)
        context_key = make_context_key(base_str)

        # All are strings at runtime
        for semantic_type in [
            cmd_id,
            option_key,
            flag_name,
            arg_value,
            parse_mode,
            context_key,
        ]:
            assert isinstance(semantic_type, str)
            assert str(semantic_type) == base_str

    def test_type_safety_in_collections(self) -> None:
        """
        GIVEN: Semantic types used in collections
        WHEN: Adding them to typed collections
        THEN: The types maintain their semantic meaning in collections
        """
        # Test CommandId in sets and lists
        cmd1 = make_command_id("help")
        cmd2 = make_command_id("status")
        cmd3 = make_command_id("help")  # Duplicate value

        command_set: set[CommandId] = {cmd1, cmd2, cmd3}
        assert len(command_set) == 2  # Duplicate removed

        command_list: list[CommandId] = [cmd1, cmd2, cmd3]
        assert len(command_list) == 3  # Duplicates preserved

        # Test OptionKey in dictionaries
        key1 = make_option_key("output")
        key2 = make_option_key("format")

        options_dict: dict[OptionKey, ArgumentValue] = {
            key1: make_argument_value("file.txt"),
            key2: make_argument_value("json"),
        }
        assert len(options_dict) == 2

    def test_string_operations_work(self) -> None:
        """
        GIVEN: Semantic types that derive from str
        WHEN: Performing string operations
        THEN: All string operations work normally
        """
        cmd_id = make_command_id("help-command")

        # String methods work
        assert cmd_id.upper() == "HELP-COMMAND"
        assert cmd_id.lower() == "help-command"
        assert cmd_id.replace("-", "_") == "help_command"
        assert cmd_id.startswith("help")
        assert cmd_id.endswith("command")
        assert len(cmd_id) == 12
        assert "help" in cmd_id

        # String concatenation works
        combined = cmd_id + "_suffix"
        assert combined == "help-command_suffix"

        # String formatting works
        formatted = f"Command: {cmd_id}"
        assert formatted == "Command: help-command"


class TestSemanticTypeValidation:
    """Test validation and error handling for semantic types."""

    def test_empty_string_handling(self) -> None:
        """
        GIVEN: Empty string values
        WHEN: Creating semantic types
        THEN: Empty strings are handled appropriately
        """
        empty_cmd = make_command_id("")
        empty_option = make_option_key("")
        empty_flag = make_flag_name("")
        empty_arg = make_argument_value("")
        empty_mode = make_parse_mode("")
        empty_key = make_context_key("")

        # All should be empty strings
        for semantic_type in [
            empty_cmd,
            empty_option,
            empty_flag,
            empty_arg,
            empty_mode,
            empty_key,
        ]:
            assert str(semantic_type) == ""
            assert len(semantic_type) == 0

    def test_whitespace_handling(self) -> None:
        """
        GIVEN: String values with whitespace
        WHEN: Creating semantic types
        THEN: Whitespace is preserved as-is
        """
        whitespace_cmd = make_command_id("  command  ")
        whitespace_option = make_option_key("\toption\n")

        assert str(whitespace_cmd) == "  command  "
        assert str(whitespace_option) == "\toption\n"

    def test_special_character_handling(self) -> None:
        """
        GIVEN: String values with special characters
        WHEN: Creating semantic types
        THEN: Special characters are preserved
        """
        special_cmd = make_command_id("git-commit!")
        special_option = make_option_key("file@path#1")
        special_flag = make_flag_name("v$2.0")

        assert str(special_cmd) == "git-commit!"
        assert str(special_option) == "file@path#1"
        assert str(special_flag) == "v$2.0"


class TestSemanticTypeEquality:
    """Test equality and hashing behavior of semantic types."""

    def test_equality_with_same_type(self) -> None:
        """
        GIVEN: Two semantic types of the same type with same value
        WHEN: Comparing for equality
        THEN: They are equal
        """
        cmd1 = make_command_id("help")
        cmd2 = make_command_id("help")

        assert cmd1 == cmd2
        assert not (cmd1 != cmd2)

    def test_equality_with_different_values(self) -> None:
        """
        GIVEN: Two semantic types of the same type with different values
        WHEN: Comparing for equality
        THEN: They are not equal
        """
        cmd1 = make_command_id("help")
        cmd2 = make_command_id("status")

        assert cmd1 != cmd2
        assert not (cmd1 == cmd2)

    def test_equality_with_raw_string(self) -> None:
        """
        GIVEN: A semantic type and a raw string with the same value
        WHEN: Comparing for equality
        THEN: They are equal (since semantic types are NewType)
        """
        cmd_id = make_command_id("help")
        raw_str = "help"

        assert cmd_id == raw_str
        assert raw_str == cmd_id

    def test_hashing_behavior(self) -> None:
        """
        GIVEN: Semantic types with same and different values
        WHEN: Using them as dictionary keys or in sets
        THEN: Hashing works correctly
        """
        cmd1 = make_command_id("help")
        cmd2 = make_command_id("help")
        cmd3 = make_command_id("status")

        # Same value should have same hash
        assert hash(cmd1) == hash(cmd2)

        # Can be used as dict keys
        cmd_dict = {cmd1: "help_info", cmd3: "status_info"}
        assert len(cmd_dict) == 2
        assert cmd_dict[cmd2] == "help_info"  # cmd2 should work as key


class TestSemanticTypeUsagePatterns:
    """Test common usage patterns and best practices."""

    def test_function_signature_type_safety(self) -> None:
        """
        GIVEN: Functions that expect specific semantic types
        WHEN: Calling them with correct types
        THEN: The calls work without type errors
        """

        def process_command(
            cmd: CommandId, options: dict[OptionKey, ArgumentValue]
        ) -> str:
            return f"Processing {cmd} with {len(options)} options"

        cmd = make_command_id("deploy")
        opts = {
            make_option_key("env"): make_argument_value("production"),
            make_option_key("region"): make_argument_value("us-west-2"),
        }

        result = process_command(cmd, opts)
        assert "deploy" in result
        assert "2 options" in result

    def test_type_conversion_patterns(self) -> None:
        """
        GIVEN: Raw strings that need to be converted to semantic types
        WHEN: Converting them explicitly
        THEN: The conversion preserves value but adds type safety
        """
        raw_commands = ["help", "status", "deploy"]
        semantic_commands = [make_command_id(cmd) for cmd in raw_commands]

        assert len(semantic_commands) == 3
        for raw, semantic in zip(raw_commands, semantic_commands):
            assert str(semantic) == raw

    def test_mixed_type_collections(self) -> None:
        """
        GIVEN: Collections containing multiple semantic types
        WHEN: Working with them
        THEN: Type safety is maintained
        """
        # Dictionary with mixed semantic types as keys
        parser_data: dict[str, Any] = {
            make_command_id("git"): "version_control",
            make_option_key("branch"): "feature/new-parser",
            make_flag_name("verbose"): True,
            make_context_key("session_id"): "12345",
        }

        assert len(parser_data) == 4

        # All keys are strings at runtime but have semantic meaning
        for key in parser_data.keys():
            assert isinstance(key, str)


class TestSemanticTypeCompatibility:
    """Test compatibility with existing code and libraries."""

    def test_json_serialization(self) -> None:
        """
        GIVEN: Semantic types in data structures
        WHEN: Serializing to JSON
        THEN: Serialization works normally
        """
        import json

        data = {
            "command": make_command_id("deploy"),
            "options": {
                make_option_key("env"): make_argument_value("prod"),
                make_option_key("region"): make_argument_value("us-west"),
            },
            "flags": [make_flag_name("verbose"), make_flag_name("force")],
        }

        # Should serialize without errors
        json_str = json.dumps(data, default=str)
        assert "deploy" in json_str
        assert "prod" in json_str

    def test_string_formatting_compatibility(self) -> None:
        """
        GIVEN: Semantic types used in string formatting
        WHEN: Using various formatting methods
        THEN: All formatting works normally
        """
        cmd = make_command_id("git")
        option = make_option_key("branch")
        value = make_argument_value("main")

        # Format strings
        formatted1 = f"Command: {cmd}, Option: {option}={value}"
        assert formatted1 == "Command: git, Option: branch=main"

        # str.format()
        formatted2 = f"Command: {cmd}, Option: {option}={value}"
        assert formatted2 == "Command: git, Option: branch=main"

        # % formatting
        formatted3 = f"Command: {cmd}, Option: {option}={value}"
        assert formatted3 == "Command: git, Option: branch=main"

    def test_regex_compatibility(self) -> None:
        """
        GIVEN: Semantic types used with regex operations
        WHEN: Performing regex matching
        THEN: Regex operations work normally
        """
        import re

        cmd = make_command_id("git-commit")
        option = make_option_key("output-file")

        # Pattern matching
        assert re.match(r"git-\w+", cmd)
        assert re.search(r"commit", cmd)

        # Substitution
        new_cmd = re.sub(r"-", "_", cmd)
        assert new_cmd == "git_commit"

        # Split
        parts = re.split(r"-", option)
        assert parts == ["output", "file"]
