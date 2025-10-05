"""Integration tests for semantic type flow through parser system.

This module tests the complete flow of semantic types from input parsing
through the entire parser pipeline, ensuring type safety is maintained
end-to-end while integrating with existing components.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

# Import existing components
from cli_patterns.core.models import SessionState
from cli_patterns.ui.parser.pipeline import ParserPipeline
from cli_patterns.ui.parser.types import ParseError, ParseResult

# Import semantic types and components (these will fail initially)
try:
    from cli_patterns.core.parser_types import (
        CommandId,
        make_argument_value,
        make_command_id,
        make_context_key,
        make_flag_name,
        make_option_key,
        make_parse_mode,
    )
    from cli_patterns.ui.parser.semantic_context import SemanticContext
    from cli_patterns.ui.parser.semantic_parser import SemanticTextParser
    from cli_patterns.ui.parser.semantic_pipeline import SemanticParserPipeline
    from cli_patterns.ui.parser.semantic_registry import SemanticCommandRegistry
    from cli_patterns.ui.parser.semantic_result import SemanticParseResult
except ImportError:
    # These imports will fail initially since the implementation doesn't exist
    pass

pytestmark = [pytest.mark.integration, pytest.mark.parser]


class TestSemanticTypeEndToEndFlow:
    """Test complete semantic type flow from input to output."""

    def test_complete_parsing_workflow_with_semantic_types(self) -> None:
        """
        GIVEN: A complete semantic parser system
        WHEN: Processing user input through the entire pipeline
        THEN: Semantic types are maintained throughout the entire flow
        """
        # Set up semantic parser pipeline
        pipeline = SemanticParserPipeline()
        text_parser = SemanticTextParser()
        registry = SemanticCommandRegistry()

        # Register commands in registry
        git_cmd = make_command_id("git")
        registry.register_command(
            git_cmd,
            description="Version control operations",
            options=[make_option_key("message"), make_option_key("author")],
            flags=[make_flag_name("verbose"), make_flag_name("all")],
        )

        # Configure parser with registry
        text_parser.set_registry(registry)

        # Add parser to pipeline
        def text_condition(input_str: str, context: SemanticContext) -> bool:
            return not input_str.startswith("!")

        pipeline.add_parser(text_parser, text_condition)

        # Create semantic context
        context = SemanticContext(
            mode=make_parse_mode("interactive"),
            history=[
                make_command_id("help"),
                make_command_id("status"),
            ],
            session_state={
                make_context_key("user_id"): "12345",
                make_context_key("session_start"): "2023-01-01T00:00:00Z",
            },
        )
        session = context.to_session_state()

        # Process complex command
        input_command = 'git commit --message="Initial commit" --author="John Doe" -va file1.txt file2.txt'
        result = pipeline.parse(input_command, session)

        # Verify complete semantic type flow
        assert isinstance(result, SemanticParseResult)
        assert str(result.command) == "git"
        assert str(result.args[0]) == "commit"
        assert str(result.args[1]) == "file1.txt"
        assert str(result.args[2]) == "file2.txt"

        # Check semantic flags
        expected_flags = {make_flag_name("v"), make_flag_name("a")}
        assert result.flags == expected_flags

        # Check semantic options
        message_key = make_option_key("message")
        author_key = make_option_key("author")
        assert message_key in result.options
        assert author_key in result.options
        assert str(result.options[message_key]) == "Initial commit"
        assert str(result.options[author_key]) == "John Doe"

        # Verify raw input preserved
        assert result.raw_input == input_command

    def test_semantic_type_interoperability_with_existing_system(self) -> None:
        """
        GIVEN: Mixed semantic and regular parser components
        WHEN: Processing input through both systems
        THEN: Conversion between systems works seamlessly
        """
        # Create regular parser pipeline for comparison
        regular_pipeline = ParserPipeline()
        from cli_patterns.ui.parser.parsers import TextParser

        regular_parser = TextParser()

        regular_pipeline.add_parser(
            regular_parser, lambda input_str, ctx: not input_str.startswith("!")
        )

        # Create semantic pipeline
        semantic_pipeline = SemanticParserPipeline()
        semantic_parser = SemanticTextParser()

        semantic_pipeline.add_parser(
            semantic_parser, lambda input_str, ctx: not input_str.startswith("!")
        )

        # Test input
        test_input = "deploy production --region=us-west-2 --force"

        # Parse with regular system
        regular_context = SessionState(
            parse_mode="interactive", command_history=[], variables={}
        )
        regular_result = regular_pipeline.parse(test_input, regular_context)

        # Convert to semantic context and parse
        semantic_context = SemanticContext.from_session_state(regular_context)
        semantic_result = semantic_pipeline.parse(test_input, semantic_context)

        # Verify equivalent results
        assert str(semantic_result.command) == regular_result.command
        assert len(semantic_result.args) == len(regular_result.args)

        for sem_arg, reg_arg in zip(semantic_result.args, regular_result.args):
            assert str(sem_arg) == reg_arg

        # Convert semantic result back to regular
        converted_result = semantic_result.to_parse_result()
        assert converted_result.command == regular_result.command
        assert converted_result.args == regular_result.args
        assert converted_result.flags == regular_result.flags
        assert converted_result.options == regular_result.options

    def test_semantic_type_persistence_across_session(self) -> None:
        """
        GIVEN: A semantic parser system with session state
        WHEN: Processing multiple commands in sequence
        THEN: Semantic types persist correctly across the session
        """
        pipeline = SemanticParserPipeline()
        parser = SemanticTextParser()
        registry = SemanticCommandRegistry()

        # Register session-aware commands
        login_cmd = make_command_id("login")
        logout_cmd = make_command_id("logout")
        whoami_cmd = make_command_id("whoami")

        for cmd in [login_cmd, logout_cmd, whoami_cmd]:
            registry.register_command(cmd, f"Description for {cmd}")

        parser.set_registry(registry)
        pipeline.add_parser(parser, lambda i, c: True)

        # Start with clean session
        context = SemanticContext(
            mode=make_parse_mode("interactive"), history=[], session_state={}
        )

        # Simulate login
        login_result = pipeline.parse("login --user=admin --password=secret", context)

        # Update context state based on login
        user_key = make_context_key("current_user")
        context.set_state(user_key, "admin")
        context.add_to_history(login_result.command)

        # Check whoami command
        whoami_result = pipeline.parse("whoami", context)
        context.add_to_history(whoami_result.command)

        # Verify session state maintained with semantic types
        assert context.get_state(user_key) == "admin"
        assert len(context.history) == 2
        assert str(context.history[0]) == "login"
        assert str(context.history[1]) == "whoami"

        # Simulate logout
        logout_result = pipeline.parse("logout", context)
        context.set_state(user_key, None)
        context.add_to_history(logout_result.command)

        # Verify final state
        assert context.get_state(user_key) is None
        assert len(context.history) == 3
        assert str(context.history[2]) == "logout"


class TestSemanticTypeErrorFlowIntegration:
    """Test error handling with semantic types across the system."""

    def test_semantic_error_propagation_through_pipeline(self) -> None:
        """
        GIVEN: A parser pipeline with semantic error handling
        WHEN: Errors occur during parsing
        THEN: Semantic error information is maintained through the pipeline
        """
        from cli_patterns.ui.parser.semantic_errors import SemanticParseError

        pipeline = SemanticParserPipeline()

        # Create a parser that raises semantic errors
        class ErrorProneSemanticParser:
            def can_parse(self, input_str: str, context: SemanticContext) -> bool:
                return True

            def parse(
                self, input_str: str, context: SemanticContext
            ) -> SemanticParseResult:
                if input_str.startswith("invalid"):
                    unknown_cmd = make_command_id(input_str.split()[0])
                    raise SemanticParseError(
                        error_type="UNKNOWN_COMMAND",
                        message=f"Unknown command: {unknown_cmd}",
                        command=unknown_cmd,
                        suggestions=[
                            make_command_id("help"),
                            make_command_id("status"),
                        ],
                    )
                return SemanticParseResult(
                    command=make_command_id("valid"),
                    args=[],
                    flags=set(),
                    options={},
                    raw_input=input_str,
                )

            def get_suggestions(self, partial: str) -> list[CommandId]:
                return []

        parser = ErrorProneSemanticParser()
        pipeline.add_parser(parser, lambda i, c: True)

        context = SemanticContext(
            mode=make_parse_mode("interactive"), history=[], session_state={}
        )
        session = context.to_session_state()

        # Test error propagation
        with pytest.raises(SemanticParseError) as exc_info:
            pipeline.parse("invalid-command arg1 arg2", session)

        error = exc_info.value
        assert error.error_type == "UNKNOWN_COMMAND"
        assert str(error.command) == "invalid-command"
        assert len(error.semantic_suggestions) == 2
        assert str(error.semantic_suggestions[0]) == "help"
        assert str(error.semantic_suggestions[1]) == "status"

    def test_semantic_error_recovery_mechanisms(self) -> None:
        """
        GIVEN: A semantic parser system with error recovery
        WHEN: Parsing fails with suggestions
        THEN: Error recovery provides semantic type suggestions
        """
        from cli_patterns.ui.parser.semantic_errors import SemanticParseError

        registry = SemanticCommandRegistry()

        # Register similar commands for suggestion testing
        commands = ["help", "helm", "hello", "health", "status", "start", "stop"]
        for cmd_str in commands:
            cmd = make_command_id(cmd_str)
            registry.register_command(cmd, f"Description for {cmd_str}")

        parser = SemanticTextParser()
        parser.set_registry(registry)

        context = SemanticContext(
            mode=make_parse_mode("interactive"), history=[], session_state={}
        )
        session = context.to_session_state()

        # Test with typo that should generate suggestions
        with pytest.raises(SemanticParseError) as exc_info:
            parser.parse("hlep", session)  # Typo for "help"

        error = exc_info.value
        assert error.error_type == "UNKNOWN_COMMAND"

        # Should have suggestions for similar commands
        suggestion_strs = [str(cmd) for cmd in error.semantic_suggestions]
        assert "help" in suggestion_strs
        assert len(error.semantic_suggestions) <= 5  # Reasonable number of suggestions

    def test_semantic_validation_errors_with_context(self) -> None:
        """
        GIVEN: A semantic parser with context-aware validation
        WHEN: Validation fails based on context
        THEN: Errors include relevant semantic context information
        """
        from cli_patterns.ui.parser.semantic_errors import SemanticParseError

        parser = SemanticTextParser()

        # Create context that lacks required permissions
        context = SemanticContext(
            mode=make_parse_mode("restricted"),
            history=[],
            session_state={
                make_context_key("user_role"): "guest",
                make_context_key("permissions"): "read-only",
            },
        )

        # Mock parser validation that checks context
        with patch.object(parser, "parse") as mock_parse:

            def context_aware_parse(
                input_str: str, ctx: SemanticContext
            ) -> SemanticParseResult:
                if (
                    "deploy" in input_str
                    and ctx.get_state(make_context_key("user_role")) != "admin"
                ):
                    raise SemanticParseError(
                        error_type="INSUFFICIENT_PERMISSIONS",
                        message="Deploy command requires admin role",
                        required_role="admin",
                        current_role=ctx.get_state(make_context_key("user_role")),
                        context_info={
                            "mode": str(ctx.mode),
                            "permissions": ctx.get_state(
                                make_context_key("permissions")
                            ),
                        },
                    )
                return SemanticParseResult(
                    command=make_command_id("allowed"),
                    args=[],
                    flags=set(),
                    options={},
                    raw_input=input_str,
                )

            mock_parse.side_effect = context_aware_parse

            with pytest.raises(SemanticParseError) as exc_info:
                parser.parse("deploy production", context)

            error = exc_info.value
            assert error.error_type == "INSUFFICIENT_PERMISSIONS"
            assert error.required_role == "admin"
            assert error.current_role == "guest"
            assert error.context_info["mode"] == "restricted"
            assert error.context_info["permissions"] == "read-only"


class TestSemanticTypePerformanceIntegration:
    """Test performance characteristics of semantic types in integration scenarios."""

    def test_large_command_history_performance(self) -> None:
        """
        GIVEN: A semantic context with large command history
        WHEN: Processing commands and updating history
        THEN: Performance remains acceptable with semantic types
        """
        import time

        # Create context with large history
        large_history = [make_command_id(f"command_{i}") for i in range(1000)]
        context = SemanticContext(
            mode=make_parse_mode("interactive"), history=large_history, session_state={}
        )

        parser = SemanticTextParser()

        # Time multiple parse operations
        start_time = time.time()
        for i in range(100):
            try:
                result = parser.parse(f"test_{i}", context)
                context.add_to_history(result.command)
            except ParseError:
                # Expected for some invalid commands
                pass

        elapsed_time = time.time() - start_time

        # Should complete in reasonable time (allowing for overhead)
        assert elapsed_time < 5.0  # 5 seconds for 100 operations
        assert len(context.history) >= 1000  # Original history preserved

    def test_large_registry_performance(self) -> None:
        """
        GIVEN: A command registry with many semantic commands
        WHEN: Performing lookups and suggestions
        THEN: Performance is acceptable for large registries
        """
        import time

        registry = SemanticCommandRegistry()

        # Register many commands
        for i in range(1000):
            cmd = make_command_id(f"command_{i:04d}")
            registry.register_command(
                cmd,
                description=f"Description for command {i}",
                options=[make_option_key(f"option_{j}") for j in range(5)],
                flags=[make_flag_name(f"flag_{j}") for j in range(3)],
            )

        # Test lookup performance
        start_time = time.time()
        for i in range(100):
            test_cmd = make_command_id(f"command_{i:04d}")
            assert registry.is_registered(test_cmd)

        lookup_time = time.time() - start_time

        # Test suggestion performance
        start_time = time.time()
        suggestions = registry.get_suggestions("command_")
        suggestion_time = time.time() - start_time

        # Performance should be reasonable
        assert lookup_time < 1.0  # 1 second for 100 lookups
        assert suggestion_time < 2.0  # 2 seconds for suggestion generation
        assert len(suggestions) > 0  # Should find matches

    def test_concurrent_semantic_type_usage(self) -> None:
        """
        GIVEN: Multiple concurrent operations using semantic types
        WHEN: Processing commands in parallel
        THEN: Semantic types are thread-safe and performant
        """
        import time
        from concurrent.futures import ThreadPoolExecutor, as_completed

        # Shared registry
        registry = SemanticCommandRegistry()
        for i in range(100):
            cmd = make_command_id(f"cmd_{i}")
            registry.register_command(cmd, f"Description {i}")

        parser = SemanticTextParser()
        parser.set_registry(registry)

        results = []
        errors = []

        def parse_command(thread_id: int) -> tuple[int, SemanticParseResult]:
            """Parse a command in a separate thread."""
            try:
                context = SemanticContext(
                    mode=make_parse_mode("concurrent"),
                    history=[],
                    session_state={make_context_key("thread_id"): str(thread_id)},
                )
                session = context.to_session_state()

                cmd_id = thread_id % 100  # Cycle through registered commands
                input_str = f"cmd_{cmd_id} arg1 arg2"
                result = parser.parse(input_str, session)
                return thread_id, result
            except Exception as e:
                errors.append((thread_id, e))
                raise

        # Run concurrent parsing
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(parse_command, i) for i in range(50)]

            for future in as_completed(futures):
                try:
                    thread_id, result = future.result()
                    results.append((thread_id, result))
                except Exception:
                    # Errors already captured in parse_command
                    pass

        elapsed_time = time.time() - start_time

        # Verify results
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 50, f"Expected 50 results, got {len(results)}"
        assert elapsed_time < 10.0, f"Took too long: {elapsed_time} seconds"

        # Verify all results have semantic types
        for _thread_id, result in results:
            assert isinstance(result, SemanticParseResult)
            assert isinstance(result.command, str)  # Runtime check for semantic type


class TestSemanticTypeBackwardCompatibility:
    """Test backward compatibility with existing parser system."""

    def test_mixed_semantic_and_regular_parsers(self) -> None:
        """
        GIVEN: A pipeline with both semantic and regular parsers
        WHEN: Processing commands through the mixed pipeline
        THEN: Both parser types work together seamlessly
        """
        from cli_patterns.ui.parser.parsers import TextParser

        # Create mixed pipeline
        pipeline = SemanticParserPipeline()

        # Add regular text parser (with adapter)
        regular_parser = TextParser()

        def regular_condition(input_str: str, context: SemanticContext) -> bool:
            return input_str.startswith("regular")

        # Adapter to make regular parser work with semantic pipeline
        class RegularToSemanticAdapter:
            def __init__(self, regular_parser: TextParser):
                self.parser = regular_parser

            def can_parse(self, input_str: str, context: SemanticContext) -> bool:
                regular_context = context.to_session_state()
                return self.parser.can_parse(input_str, regular_context)

            def parse(
                self, input_str: str, context: SemanticContext
            ) -> SemanticParseResult:
                regular_context = context.to_session_state()
                regular_result = self.parser.parse(input_str, regular_context)
                return SemanticParseResult.from_parse_result(regular_result)

            def get_suggestions(self, partial: str) -> list[CommandId]:
                suggestions = self.parser.get_suggestions(partial)
                return [make_command_id(s) for s in suggestions]

        adapter = RegularToSemanticAdapter(regular_parser)
        pipeline.add_parser(adapter, regular_condition)

        # Add semantic parser
        semantic_parser = SemanticTextParser()

        def semantic_condition(input_str: str, context: SemanticContext) -> bool:
            return input_str.startswith("semantic")

        pipeline.add_parser(semantic_parser, semantic_condition)

        # Test both parser types
        context = SemanticContext(
            mode=make_parse_mode("mixed"), history=[], session_state={}
        )

        # Test regular parser through adapter
        regular_result = pipeline.parse("regular command arg1", context)
        assert isinstance(regular_result, SemanticParseResult)
        assert str(regular_result.command) == "regular"

        # Test semantic parser directly
        semantic_result = pipeline.parse("semantic command arg2", context)
        assert isinstance(semantic_result, SemanticParseResult)
        assert str(semantic_result.command) == "semantic"

    def test_semantic_type_migration_path(self) -> None:
        """
        GIVEN: Existing regular parser system data
        WHEN: Migrating to semantic types
        THEN: Migration preserves all data and functionality
        """
        # Simulate existing regular system data
        regular_data = {
            "commands": ["help", "status", "deploy", "rollback"],
            "recent_history": ["help", "status", "deploy production"],
            "session_state": {
                "user": "admin",
                "role": "administrator",
                "last_command": "status",
            },
            "registered_options": {
                "deploy": ["environment", "region", "force"],
                "rollback": ["version", "confirm"],
            },
        }

        # Migration function
        def migrate_to_semantic_types(
            data: dict,
        ) -> tuple[SemanticCommandRegistry, SemanticContext]:
            registry = SemanticCommandRegistry()

            # Migrate commands and options
            for cmd_str in data["commands"]:
                cmd = make_command_id(cmd_str)
                options = data["registered_options"].get(cmd_str, [])
                semantic_options = [make_option_key(opt) for opt in options]

                registry.register_command(
                    cmd,
                    description=f"Migrated command: {cmd_str}",
                    options=semantic_options,
                )

            # Migrate context
            semantic_history = [make_command_id(cmd) for cmd in data["recent_history"]]
            semantic_session_state = {
                make_context_key(k): v for k, v in data["session_state"].items()
            }

            context = SemanticContext(
                mode=make_parse_mode("migrated"),
                history=semantic_history,
                session_state=semantic_session_state,
            )

            return registry, context

        # Perform migration
        registry, context = migrate_to_semantic_types(regular_data)

        # Verify migration results
        assert registry.is_registered(make_command_id("help"))
        assert registry.is_registered(make_command_id("deploy"))

        deploy_metadata = registry.get_command_metadata(make_command_id("deploy"))
        assert deploy_metadata is not None
        option_strs = [str(opt) for opt in deploy_metadata.options]
        assert "environment" in option_strs
        assert "region" in option_strs
        assert "force" in option_strs

        # Verify context migration
        assert len(context.history) == 3
        assert str(context.history[0]) == "help"
        assert str(context.history[2]) == "deploy production"

        user_key = make_context_key("user")
        role_key = make_context_key("role")
        assert context.get_state(user_key) == "admin"
        assert context.get_state(role_key) == "administrator"

    def test_semantic_type_api_compatibility(self) -> None:
        """
        GIVEN: Existing code that expects regular parser API
        WHEN: Using semantic parser with compatibility layer
        THEN: Existing code continues to work without modification
        """

        # Simulate existing code that expects regular ParseResult
        def existing_command_processor(result: ParseResult) -> dict:
            """Existing function that processes regular ParseResult."""
            return {
                "command": result.command,
                "arg_count": len(result.args),
                "has_verbose": "v" in result.flags,
                "output_format": result.options.get("format", "text"),
            }

        # Create semantic result
        semantic_result = SemanticParseResult(
            command=make_command_id("process"),
            args=[make_argument_value("file1.txt"), make_argument_value("file2.txt")],
            flags={make_flag_name("v"), make_flag_name("q")},
            options={make_option_key("format"): make_argument_value("json")},
            raw_input="process file1.txt file2.txt -vq --format=json",
        )

        # Convert to regular result for compatibility
        regular_result = semantic_result.to_parse_result()

        # Existing code should work unchanged
        processed = existing_command_processor(regular_result)

        assert processed["command"] == "process"
        assert processed["arg_count"] == 2
        assert processed["has_verbose"] is True
        assert processed["output_format"] == "json"
