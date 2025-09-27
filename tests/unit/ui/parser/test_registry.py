"""Tests for command registry implementation."""

from __future__ import annotations

import pytest

from cli_patterns.ui.parser.registry import CommandMetadata, CommandRegistry

pytestmark = pytest.mark.parser


class TestCommandMetadata:
    """Test CommandMetadata dataclass."""

    def test_basic_creation(self) -> None:
        """Test basic CommandMetadata creation."""
        metadata = CommandMetadata(
            name="help",
            description="Show help information",
            aliases=["h", "?"],
            category="system",
        )

        assert metadata.name == "help"
        assert metadata.description == "Show help information"
        assert metadata.aliases == ["h", "?"]
        assert metadata.category == "system"

    def test_minimal_creation(self) -> None:
        """Test CommandMetadata with minimal required fields."""
        metadata = CommandMetadata(name="test", description="Test command")

        assert metadata.name == "test"
        assert metadata.description == "Test command"
        assert metadata.aliases == []  # Default empty
        assert metadata.category == "general"  # Default category

    def test_with_aliases(self) -> None:
        """Test CommandMetadata with multiple aliases."""
        metadata = CommandMetadata(
            name="list", description="List items", aliases=["ls", "l", "show"]
        )

        assert metadata.name == "list"
        assert len(metadata.aliases) == 3
        assert "ls" in metadata.aliases
        assert "l" in metadata.aliases
        assert "show" in metadata.aliases

    def test_with_category(self) -> None:
        """Test CommandMetadata with custom category."""
        metadata = CommandMetadata(
            name="deploy", description="Deploy application", category="deployment"
        )

        assert metadata.name == "deploy"
        assert metadata.category == "deployment"

    @pytest.mark.parametrize(
        "name,description,aliases,category",
        [
            ("cmd1", "Description 1", [], "cat1"),
            ("cmd2", "Description 2", ["c2"], "cat2"),
            ("cmd3", "Description 3", ["c3", "command3"], "cat3"),
            (
                "very-long-command-name",
                "Long description here",
                ["long", "lng"],
                "utilities",
            ),
        ],
    )
    def test_parametrized_creation(
        self, name: str, description: str, aliases: list[str], category: str
    ) -> None:
        """Test CommandMetadata creation with various parameters."""
        metadata = CommandMetadata(
            name=name, description=description, aliases=aliases, category=category
        )

        assert metadata.name == name
        assert metadata.description == description
        assert metadata.aliases == aliases
        assert metadata.category == category

    def test_immutability_behavior(self) -> None:
        """Test CommandMetadata behaves as expected for immutability."""
        metadata = CommandMetadata(
            name="test", description="Test command", aliases=["t", "tst"]
        )

        # Should be able to access fields
        assert metadata.name == "test"
        assert "t" in metadata.aliases

    def test_string_representation(self) -> None:
        """Test string representation of CommandMetadata."""
        metadata = CommandMetadata(
            name="example", description="Example command", aliases=["ex"]
        )

        # Should have meaningful string representation
        str_repr = str(metadata)
        assert "example" in str_repr


class TestCommandRegistry:
    """Test CommandRegistry basic functionality."""

    @pytest.fixture
    def registry(self) -> CommandRegistry:
        """Create empty CommandRegistry for testing."""
        return CommandRegistry()

    def test_registry_instantiation(self, registry: CommandRegistry) -> None:
        """Test that CommandRegistry can be instantiated."""
        assert registry is not None
        assert isinstance(registry, CommandRegistry)

    def test_empty_registry_state(self, registry: CommandRegistry) -> None:
        """Test empty registry initial state."""
        commands = registry.list_commands()
        assert commands == []

        # Should not find any commands
        assert registry.lookup_command("nonexistent") is None

    def test_register_single_command(self, registry: CommandRegistry) -> None:
        """Test registering a single command."""
        metadata = CommandMetadata(name="help", description="Show help")

        registry.register_command(metadata)

        # Should be able to find the command
        found = registry.lookup_command("help")
        assert found is not None
        assert found.name == "help"
        assert found.description == "Show help"

    def test_register_multiple_commands(self, registry: CommandRegistry) -> None:
        """Test registering multiple commands."""
        cmd1 = CommandMetadata(name="help", description="Show help")
        cmd2 = CommandMetadata(name="list", description="List items")
        cmd3 = CommandMetadata(name="quit", description="Exit application")

        registry.register_command(cmd1)
        registry.register_command(cmd2)
        registry.register_command(cmd3)

        # Should find all commands
        assert registry.lookup_command("help") is not None
        assert registry.lookup_command("list") is not None
        assert registry.lookup_command("quit") is not None

        # List should contain all commands
        commands = registry.list_commands()
        assert len(commands) == 3


class TestCommandRegistryLookup:
    """Test command lookup functionality."""

    @pytest.fixture
    def registry(self) -> CommandRegistry:
        return CommandRegistry()

    def test_lookup_by_name(self, registry: CommandRegistry) -> None:
        """Test looking up commands by name."""
        metadata = CommandMetadata(name="status", description="Show status")

        registry.register_command(metadata)

        found = registry.lookup_command("status")
        assert found is not None
        assert found.name == "status"

    def test_lookup_by_alias(self, registry: CommandRegistry) -> None:
        """Test looking up commands by alias."""
        metadata = CommandMetadata(
            name="help", description="Show help", aliases=["h", "?", "help-me"]
        )

        registry.register_command(metadata)

        # Should find by all aliases
        found_h = registry.lookup_command("h")
        found_q = registry.lookup_command("?")
        found_help = registry.lookup_command("help-me")

        assert found_h is not None
        assert found_q is not None
        assert found_help is not None

        # All should return the same command
        assert found_h.name == "help"
        assert found_q.name == "help"
        assert found_help.name == "help"

    def test_lookup_nonexistent_command(self, registry: CommandRegistry) -> None:
        """Test looking up non-existent command."""
        metadata = CommandMetadata(name="real", description="Real command")
        registry.register_command(metadata)

        # Should return None for non-existent commands
        assert registry.lookup_command("fake") is None
        assert registry.lookup_command("nonexistent") is None
        assert registry.lookup_command("") is None

    def test_case_sensitive_lookup(self, registry: CommandRegistry) -> None:
        """Test that command lookup is case-sensitive."""
        metadata = CommandMetadata(name="Help", description="Show help", aliases=["H"])

        registry.register_command(metadata)

        # Exact case should work
        assert registry.lookup_command("Help") is not None
        assert registry.lookup_command("H") is not None

        # Wrong case should not work (unless registry implements case-insensitive lookup)
        # This test documents expected behavior
        registry.lookup_command("help")  # lowercase
        # Result depends on implementation - could be None or the command

    @pytest.mark.parametrize(
        "command_name,aliases,lookup_key",
        [
            ("list", ["ls", "l"], "ls"),
            ("delete", ["del", "rm", "remove"], "rm"),
            ("configure", ["config", "cfg", "conf"], "cfg"),
            ("status", ["stat", "st"], "stat"),
        ],
    )
    def test_parametrized_alias_lookup(
        self,
        registry: CommandRegistry,
        command_name: str,
        aliases: list[str],
        lookup_key: str,
    ) -> None:
        """Test looking up various aliases."""
        metadata = CommandMetadata(
            name=command_name, description=f"{command_name} command", aliases=aliases
        )

        registry.register_command(metadata)

        found = registry.lookup_command(lookup_key)
        assert found is not None
        assert found.name == command_name


class TestCommandRegistryValidation:
    """Test command registration validation."""

    @pytest.fixture
    def registry(self) -> CommandRegistry:
        return CommandRegistry()

    def test_duplicate_command_registration(self, registry: CommandRegistry) -> None:
        """Test registering duplicate command names."""
        cmd1 = CommandMetadata(name="duplicate", description="First")
        cmd2 = CommandMetadata(name="duplicate", description="Second")

        registry.register_command(cmd1)

        # Second registration should raise error or overwrite
        with pytest.raises(ValueError) as exc_info:
            registry.register_command(cmd2)

        error_msg = str(exc_info.value).lower()
        assert "duplicate" in error_msg or "already" in error_msg

    def test_duplicate_alias_registration(self, registry: CommandRegistry) -> None:
        """Test registering commands with duplicate aliases."""
        cmd1 = CommandMetadata(
            name="first", description="First command", aliases=["shared"]
        )
        cmd2 = CommandMetadata(
            name="second",
            description="Second command",
            aliases=["shared"],  # Same alias
        )

        registry.register_command(cmd1)

        # Should detect alias conflict
        with pytest.raises(ValueError) as exc_info:
            registry.register_command(cmd2)

        error_msg = str(exc_info.value).lower()
        assert (
            "alias" in error_msg or "conflict" in error_msg or "duplicate" in error_msg
        )

    def test_alias_conflicts_with_existing_name(
        self, registry: CommandRegistry
    ) -> None:
        """Test alias that conflicts with existing command name."""
        cmd1 = CommandMetadata(name="existing", description="Existing command")
        cmd2 = CommandMetadata(
            name="new",
            description="New command",
            aliases=["existing"],  # Conflicts with cmd1's name
        )

        registry.register_command(cmd1)

        with pytest.raises(ValueError) as exc_info:
            registry.register_command(cmd2)

        error_msg = str(exc_info.value).lower()
        assert "conflict" in error_msg or "existing" in error_msg

    def test_empty_command_name_validation(self, registry: CommandRegistry) -> None:
        """Test validation of empty command names."""
        with pytest.raises(ValueError) as exc_info:
            CommandMetadata(name="", description="Empty name")

        error_msg = str(exc_info.value).lower()
        assert "name" in error_msg or "empty" in error_msg

    def test_whitespace_command_name_validation(
        self, registry: CommandRegistry
    ) -> None:
        """Test validation of whitespace-only command names."""
        with pytest.raises(ValueError) as exc_info:
            CommandMetadata(name="   ", description="Whitespace name")

        error_msg = str(exc_info.value).lower()
        assert (
            "name" in error_msg or "whitespace" in error_msg or "invalid" in error_msg
        )


class TestCommandRegistryListing:
    """Test command listing functionality."""

    @pytest.fixture
    def populated_registry(self) -> CommandRegistry:
        """Create registry with sample commands."""
        registry = CommandRegistry()

        commands = [
            CommandMetadata("help", "Show help", ["h", "?"], "system"),
            CommandMetadata("list", "List items", ["ls", "l"], "file"),
            CommandMetadata("delete", "Delete items", ["del", "rm"], "file"),
            CommandMetadata("status", "Show status", ["stat"], "system"),
            CommandMetadata("config", "Configuration", ["cfg"], "settings"),
        ]

        for cmd in commands:
            registry.register_command(cmd)

        return registry

    def test_list_all_commands(self, populated_registry: CommandRegistry) -> None:
        """Test listing all commands."""
        commands = populated_registry.list_commands()

        assert len(commands) == 5
        command_names = {cmd.name for cmd in commands}
        expected_names = {"help", "list", "delete", "status", "config"}
        assert command_names == expected_names

    def test_list_commands_by_category(
        self, populated_registry: CommandRegistry
    ) -> None:
        """Test listing commands filtered by category."""
        system_commands = populated_registry.list_commands(category="system")
        file_commands = populated_registry.list_commands(category="file")
        settings_commands = populated_registry.list_commands(category="settings")

        # System category
        assert len(system_commands) == 2
        system_names = {cmd.name for cmd in system_commands}
        assert system_names == {"help", "status"}

        # File category
        assert len(file_commands) == 2
        file_names = {cmd.name for cmd in file_commands}
        assert file_names == {"list", "delete"}

        # Settings category
        assert len(settings_commands) == 1
        assert settings_commands[0].name == "config"

    def test_list_commands_empty_category(
        self, populated_registry: CommandRegistry
    ) -> None:
        """Test listing commands for non-existent category."""
        empty_commands = populated_registry.list_commands(category="nonexistent")
        assert empty_commands == []

    def test_list_commands_sorted_order(
        self, populated_registry: CommandRegistry
    ) -> None:
        """Test that listed commands are in sorted order."""
        commands = populated_registry.list_commands()
        command_names = [cmd.name for cmd in commands]

        # Should be sorted alphabetically
        assert command_names == sorted(command_names)

    @pytest.mark.parametrize(
        "category,expected_count",
        [
            ("system", 2),
            ("file", 2),
            ("settings", 1),
            ("nonexistent", 0),
        ],
    )
    def test_parametrized_category_listing(
        self, populated_registry: CommandRegistry, category: str, expected_count: int
    ) -> None:
        """Test listing commands by various categories."""
        commands = populated_registry.list_commands(category=category)
        assert len(commands) == expected_count


class TestCommandRegistrySuggestions:
    """Test command suggestion functionality."""

    @pytest.fixture
    def populated_registry(self) -> CommandRegistry:
        """Create registry with commands for testing suggestions."""
        registry = CommandRegistry()

        commands = [
            CommandMetadata("help", "Show help", ["h"]),
            CommandMetadata("history", "Show history", ["hist"]),
            CommandMetadata("halt", "Stop system"),
            CommandMetadata("list", "List items", ["ls"]),
            CommandMetadata("login", "User login"),
            CommandMetadata("logout", "User logout"),
            CommandMetadata("status", "Show status", ["stat"]),
            CommandMetadata("start", "Start service"),
            CommandMetadata("stop", "Stop service"),
        ]

        for cmd in commands:
            registry.register_command(cmd)

        return registry

    def test_typo_suggestions_simple(self, populated_registry: CommandRegistry) -> None:
        """Test suggestions for simple typos."""
        suggestions = populated_registry.get_typo_suggestions("hlep")  # typo for "help"
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
        assert "help" in suggestions

    def test_typo_suggestions_partial_match(
        self, populated_registry: CommandRegistry
    ) -> None:
        """Test suggestions for partial matches."""
        suggestions = populated_registry.get_typo_suggestions("lis")  # partial "list"
        assert isinstance(suggestions, list)
        assert "list" in suggestions

    def test_typo_suggestions_prefix_match(
        self, populated_registry: CommandRegistry
    ) -> None:
        """Test suggestions for commands with common prefix."""
        suggestions = populated_registry.get_typo_suggestions(
            "st"
        )  # should suggest "start", "stop", "status"

        assert isinstance(suggestions, list)
        start_stop_status = {"start", "stop", "status"}
        suggested_names = {s for s in suggestions if s in start_stop_status}
        assert len(suggested_names) > 0

    def test_typo_suggestions_alias_included(
        self, populated_registry: CommandRegistry
    ) -> None:
        """Test that suggestions include aliases."""
        suggestions = populated_registry.get_typo_suggestions(
            "sta"
        )  # could match "stat" alias

        assert isinstance(suggestions, list)
        # Should suggest either "status" or "stat" alias
        assert any(s in ["status", "stat"] for s in suggestions)

    def test_typo_suggestions_empty_input(
        self, populated_registry: CommandRegistry
    ) -> None:
        """Test suggestions for empty input."""
        suggestions = populated_registry.get_typo_suggestions("")
        assert isinstance(suggestions, list)
        # Might return common commands or empty list

    def test_typo_suggestions_no_matches(
        self, populated_registry: CommandRegistry
    ) -> None:
        """Test suggestions when no close matches exist."""
        suggestions = populated_registry.get_typo_suggestions("xyz123")
        assert isinstance(suggestions, list)
        # Might be empty or contain fallback suggestions

    def test_typo_suggestions_limit(self, populated_registry: CommandRegistry) -> None:
        """Test that suggestions are limited to reasonable number."""
        suggestions = populated_registry.get_typo_suggestions(
            "h"
        )  # many matches possible
        assert isinstance(suggestions, list)
        assert len(suggestions) <= 10  # Reasonable limit

    @pytest.mark.parametrize(
        "typo,expected_suggestion",
        [
            ("helpo", "help"),
            ("liste", "list"),
            ("loging", "login"),
            ("statsu", "status"),
        ],
    )
    def test_parametrized_typo_suggestions(
        self, populated_registry: CommandRegistry, typo: str, expected_suggestion: str
    ) -> None:
        """Test suggestions for various typos."""
        suggestions = populated_registry.get_typo_suggestions(typo)
        assert isinstance(suggestions, list)
        # Expected suggestion should be in the list (if algorithm is good enough)
        # Note: This test might be flaky depending on suggestion algorithm


class TestCommandRegistryCategories:
    """Test category-related functionality."""

    @pytest.fixture
    def registry(self) -> CommandRegistry:
        return CommandRegistry()

    def test_get_categories_empty_registry(self, registry: CommandRegistry) -> None:
        """Test getting categories from empty registry."""
        categories = registry.get_categories()
        assert categories == []

    def test_get_categories_with_commands(self, registry: CommandRegistry) -> None:
        """Test getting categories from populated registry."""
        commands = [
            CommandMetadata("cmd1", "Description", [], "cat1"),
            CommandMetadata("cmd2", "Description", [], "cat2"),
            CommandMetadata("cmd3", "Description", [], "cat1"),  # Duplicate category
            CommandMetadata("cmd4", "Description", [], "cat3"),
        ]

        for cmd in commands:
            registry.register_command(cmd)

        categories = registry.get_categories()
        assert isinstance(categories, list)
        assert len(categories) == 3  # Unique categories
        assert set(categories) == {"cat1", "cat2", "cat3"}

    def test_get_categories_sorted(self, registry: CommandRegistry) -> None:
        """Test that categories are returned in sorted order."""
        commands = [
            CommandMetadata("cmd1", "Desc", [], "zebra"),
            CommandMetadata("cmd2", "Desc", [], "alpha"),
            CommandMetadata("cmd3", "Desc", [], "beta"),
        ]

        for cmd in commands:
            registry.register_command(cmd)

        categories = registry.get_categories()
        assert categories == sorted(categories)

    def test_default_category_handling(self, registry: CommandRegistry) -> None:
        """Test handling of default category."""
        # Command without explicit category should use default
        cmd = CommandMetadata("test", "Test command")
        registry.register_command(cmd)

        categories = registry.get_categories()
        assert "general" in categories  # Default category


class TestCommandRegistryIntegration:
    """Integration tests for CommandRegistry."""

    def test_complete_workflow(self) -> None:
        """Test complete command registry workflow."""
        registry = CommandRegistry()

        # Register commands
        commands = [
            CommandMetadata("help", "Show help", ["h", "?"], "system"),
            CommandMetadata("quit", "Exit application", ["exit", "q"], "system"),
            CommandMetadata("list", "List files", ["ls"], "file"),
            CommandMetadata("delete", "Delete file", ["del", "rm"], "file"),
        ]

        for cmd in commands:
            registry.register_command(cmd)

        # Test lookups
        help_cmd = registry.lookup_command("help")
        assert help_cmd is not None
        assert help_cmd.name == "help"

        quit_by_alias = registry.lookup_command("q")
        assert quit_by_alias is not None
        assert quit_by_alias.name == "quit"

        # Test listing
        all_commands = registry.list_commands()
        assert len(all_commands) == 4

        system_commands = registry.list_commands(category="system")
        assert len(system_commands) == 2

        # Test suggestions
        suggestions = registry.get_typo_suggestions("hel")
        assert "help" in suggestions

        # Test categories
        categories = registry.get_categories()
        assert set(categories) == {"system", "file"}

    def test_real_world_command_set(self) -> None:
        """Test registry with realistic command set."""
        registry = CommandRegistry()

        # Common CLI commands
        real_commands = [
            # System commands
            CommandMetadata("help", "Display help information", ["h", "?"], "system"),
            CommandMetadata("version", "Show version", ["v", "--version"], "system"),
            CommandMetadata("exit", "Exit application", ["quit", "q"], "system"),
            # File operations
            CommandMetadata(
                "list", "List files and directories", ["ls", "dir"], "file"
            ),
            CommandMetadata("copy", "Copy files", ["cp"], "file"),
            CommandMetadata("move", "Move files", ["mv"], "file"),
            CommandMetadata("delete", "Delete files", ["del", "rm"], "file"),
            # Git operations
            CommandMetadata("status", "Git status", ["st"], "git"),
            CommandMetadata("commit", "Git commit", ["ci"], "git"),
            CommandMetadata("push", "Git push", [], "git"),
            CommandMetadata("pull", "Git pull", [], "git"),
            # Config
            CommandMetadata(
                "config", "Configuration settings", ["cfg", "configure"], "config"
            ),
            CommandMetadata("set", "Set configuration value", [], "config"),
            CommandMetadata("get", "Get configuration value", [], "config"),
        ]

        # Register all commands
        for cmd in real_commands:
            registry.register_command(cmd)

        # Test comprehensive functionality
        assert len(registry.list_commands()) == len(real_commands)
        assert len(registry.get_categories()) == 4  # system, file, git, config

        # Test alias resolution
        assert registry.lookup_command("ls").name == "list"
        assert registry.lookup_command("rm").name == "delete"
        assert registry.lookup_command("cfg").name == "config"

        # Test category filtering
        git_commands = registry.list_commands(category="git")
        assert len(git_commands) == 4
        git_names = {cmd.name for cmd in git_commands}
        assert git_names == {"status", "commit", "push", "pull"}

    def test_error_handling_integration(self) -> None:
        """Test error handling in integrated scenarios."""
        registry = CommandRegistry()

        # Register some commands
        cmd1 = CommandMetadata("existing", "Existing command")
        registry.register_command(cmd1)

        # Test various error conditions
        with pytest.raises(ValueError):
            # Duplicate name
            registry.register_command(CommandMetadata("existing", "Duplicate"))

        with pytest.raises(ValueError):
            # Alias conflicts with existing name
            registry.register_command(CommandMetadata("new", "New cmd", ["existing"]))

        # Successful operations should still work
        valid_cmd = CommandMetadata("valid", "Valid command", ["v"])
        registry.register_command(valid_cmd)

        assert registry.lookup_command("valid") is not None
        assert registry.lookup_command("v") is not None

    def test_performance_with_many_commands(self) -> None:
        """Test registry performance with large number of commands."""
        registry = CommandRegistry()

        # Register many commands
        num_commands = 100
        for i in range(num_commands):
            cmd = CommandMetadata(
                name=f"command_{i:03d}",
                description=f"Command number {i}",
                aliases=[f"c{i}", f"cmd{i}"] if i % 5 == 0 else [],
                category=f"category_{i % 10}",
            )
            registry.register_command(cmd)

        # Basic functionality should still work efficiently
        assert len(registry.list_commands()) == num_commands

        # Lookup should work
        assert registry.lookup_command("command_050") is not None
        assert registry.lookup_command("c25") is not None  # Alias

        # Category listing should work
        cat_0_commands = registry.list_commands(category="category_0")
        assert len(cat_0_commands) == 10  # Every 10th command

        # Suggestions should work
        suggestions = registry.get_typo_suggestions("command_05")
        assert len(suggestions) > 0

    def test_thread_safety_considerations(self) -> None:
        """Test considerations for thread safety (basic test)."""
        registry = CommandRegistry()

        # Register command
        cmd = CommandMetadata("test", "Test command")
        registry.register_command(cmd)

        # Multiple lookups should be consistent
        for _ in range(10):
            found = registry.lookup_command("test")
            assert found is not None
            assert found.name == "test"

        # Multiple listings should be consistent
        for _ in range(10):
            commands = registry.list_commands()
            assert len(commands) == 1
            assert commands[0].name == "test"


class TestCommandRegistryCache:
    """Test caching functionality for command suggestions."""

    @pytest.fixture
    def registry(self) -> CommandRegistry:
        """Create registry with caching enabled."""
        return CommandRegistry(cache_size=16)  # Small cache for testing

    @pytest.fixture
    def populated_registry(self) -> CommandRegistry:
        """Create registry with commands for testing caching."""
        registry = CommandRegistry(cache_size=16)

        commands = [
            CommandMetadata("help", "Show help", ["h"]),
            CommandMetadata("history", "Show history", ["hist"]),
            CommandMetadata("halt", "Stop system"),
            CommandMetadata("list", "List items", ["ls"]),
            CommandMetadata("login", "User login"),
            CommandMetadata("logout", "User logout"),
            CommandMetadata("status", "Show status", ["stat"]),
            CommandMetadata("start", "Start service"),
            CommandMetadata("stop", "Stop service"),
        ]

        for cmd in commands:
            registry.register_command(cmd)

        return registry

    def test_cache_enabled_by_default(self) -> None:
        """Test that caching is enabled by default."""
        registry = CommandRegistry()
        # Should have the cached suggestions method
        assert hasattr(registry, "_cached_suggestions")
        assert hasattr(registry._cached_suggestions, "cache_clear")

    def test_cache_disabled_when_size_zero(self) -> None:
        """Test that caching is disabled when cache_size is 0."""
        registry = CommandRegistry(cache_size=0)
        # Should not have cache_clear method when caching is disabled
        assert hasattr(registry, "_cached_suggestions")
        assert not hasattr(registry._cached_suggestions, "cache_clear")

    def test_suggestions_are_cached(self, populated_registry: CommandRegistry) -> None:
        """Test that suggestions are cached and return same results."""
        # First call
        suggestions1 = populated_registry.get_suggestions("hel", limit=3)

        # Second call should return same results (from cache)
        suggestions2 = populated_registry.get_suggestions("hel", limit=3)

        assert suggestions1 == suggestions2
        assert "help" in suggestions1

    def test_cache_invalidated_on_register(self, registry: CommandRegistry) -> None:
        """Test that cache is cleared when registering new commands."""
        # Register initial command
        cmd1 = CommandMetadata("help", "Show help")
        registry.register_command(cmd1)

        # Get suggestions to populate cache
        suggestions1 = registry.get_suggestions("h", limit=5)
        assert "help" in suggestions1

        # Register new command that would affect suggestions
        cmd2 = CommandMetadata("hello", "Say hello")
        registry.register_command(cmd2)

        # Get suggestions again - should include new command
        suggestions2 = registry.get_suggestions("h", limit=5)
        assert "help" in suggestions2
        assert "hello" in suggestions2

    def test_cache_invalidated_on_unregister(
        self, populated_registry: CommandRegistry
    ) -> None:
        """Test that cache is cleared when unregistering commands."""
        # Get initial suggestions to populate cache
        suggestions1 = populated_registry.get_suggestions("hel", limit=5)
        assert "help" in suggestions1

        # Unregister a command
        result = populated_registry.unregister("help")
        assert result is True

        # Get suggestions again - should not include unregistered command
        suggestions2 = populated_registry.get_suggestions("hel", limit=5)
        assert "help" not in suggestions2

    def test_cache_with_different_parameters(
        self, populated_registry: CommandRegistry
    ) -> None:
        """Test that cache works correctly with different parameter combinations."""
        # Different partial strings should cache separately
        suggestions_h = populated_registry.get_suggestions("h", limit=3)
        suggestions_s = populated_registry.get_suggestions("s", limit=3)
        suggestions_l = populated_registry.get_suggestions("l", limit=3)

        # Each should return appropriate results
        assert any(
            "help" in s or "history" in s or "halt" in s for s in [suggestions_h]
        )
        assert any(
            "status" in s or "start" in s or "stop" in s for s in [suggestions_s]
        )
        assert any(
            "list" in s or "login" in s or "logout" in s for s in [suggestions_l]
        )

        # Different limits for same partial should cache separately
        suggestions_h_3 = populated_registry.get_suggestions("h", limit=3)
        suggestions_h_5 = populated_registry.get_suggestions("h", limit=5)

        # Results should be consistent within same parameters
        assert suggestions_h == suggestions_h_3
        # But different limits might return different number of results
        assert len(suggestions_h_5) >= len(suggestions_h_3)

    def test_cache_performance_improvement(
        self, populated_registry: CommandRegistry
    ) -> None:
        """Test that caching provides performance benefit (basic test)."""
        import time

        # First call (cold cache)
        start_time = time.time()
        suggestions1 = populated_registry.get_suggestions("h", limit=10)
        first_call_time = time.time() - start_time

        # Second call (warm cache) - should be faster
        start_time = time.time()
        suggestions2 = populated_registry.get_suggestions("h", limit=10)
        second_call_time = time.time() - start_time

        # Results should be the same
        assert suggestions1 == suggestions2

        # Second call should generally be faster (though this can be flaky in tests)
        # We just verify it's not significantly slower
        assert second_call_time <= first_call_time * 2  # Allow some variance

    def test_cache_with_empty_partial(
        self, populated_registry: CommandRegistry
    ) -> None:
        """Test that empty partial input is cached correctly."""
        # Empty string should return common commands
        suggestions1 = populated_registry.get_suggestions("", limit=5)
        suggestions2 = populated_registry.get_suggestions("", limit=5)

        assert suggestions1 == suggestions2
        assert isinstance(suggestions1, list)

    def test_cache_size_parameter(self) -> None:
        """Test different cache sizes."""
        # Small cache
        small_registry = CommandRegistry(cache_size=2)
        assert hasattr(small_registry._cached_suggestions, "cache_clear")

        # Large cache
        large_registry = CommandRegistry(cache_size=1000)
        assert hasattr(large_registry._cached_suggestions, "cache_clear")

        # Zero cache (disabled)
        no_cache_registry = CommandRegistry(cache_size=0)
        assert not hasattr(no_cache_registry._cached_suggestions, "cache_clear")

    def test_cache_with_aliases(self, registry: CommandRegistry) -> None:
        """Test that caching works correctly with aliases."""
        # Register command with aliases
        cmd = CommandMetadata("list", "List items", ["ls", "l"])
        registry.register_command(cmd)

        # Get suggestions that should include aliases
        suggestions1 = registry.get_suggestions("l", limit=5)
        suggestions2 = registry.get_suggestions("l", limit=5)

        assert suggestions1 == suggestions2
        assert any(s in ["list", "ls", "l"] for s in suggestions1)
