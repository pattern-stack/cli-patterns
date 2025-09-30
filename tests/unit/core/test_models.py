"""Tests for core data models.

This module tests the Pydantic models that define the wizard configuration structure,
including actions, options, branches, and the complete wizard configuration.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

# Import the models we're testing (these will fail initially)
try:
    from cli_patterns.core.models import (
        ActionResult,
        BaseConfig,
        BashActionConfig,
        BooleanOptionConfig,
        BranchConfig,
        CollectionResult,
        MenuConfig,
        NavigationResult,
        NumberOptionConfig,
        PathOptionConfig,
        PythonActionConfig,
        SelectOptionConfig,
        SessionState,
        StringOptionConfig,
        WizardConfig,
    )
    from cli_patterns.core.types import (
        make_action_id,
        make_branch_id,
        make_menu_id,
        make_option_key,
    )
except ImportError:
    # These imports will fail initially since the implementation doesn't exist
    pass

pytestmark = pytest.mark.unit


class TestBaseConfig:
    """Test the BaseConfig model that provides common fields."""

    def test_base_config_with_defaults(self) -> None:
        """
        GIVEN: No metadata or tags provided
        WHEN: Creating a BaseConfig
        THEN: Default values are used
        """
        config = BaseConfig()
        assert config.metadata == {}
        assert config.tags == []

    def test_base_config_with_metadata(self) -> None:
        """
        GIVEN: Custom metadata
        WHEN: Creating a BaseConfig
        THEN: Metadata is stored correctly
        """
        metadata = {"author": "test", "version": "1.0"}
        config = BaseConfig(metadata=metadata)
        assert config.metadata == metadata

    def test_base_config_with_tags(self) -> None:
        """
        GIVEN: Custom tags
        WHEN: Creating a BaseConfig
        THEN: Tags are stored correctly
        """
        tags = ["production", "important"]
        config = BaseConfig(tags=tags)
        assert config.tags == tags


class TestActionConfigs:
    """Test action configuration models."""

    def test_bash_action_config_minimal(self) -> None:
        """
        GIVEN: Minimal bash action configuration
        WHEN: Creating a BashActionConfig
        THEN: Configuration is created with required fields
        """
        config = BashActionConfig(
            type="bash",
            id=make_action_id("deploy"),
            name="Deploy Application",
            command="kubectl apply -f deploy.yaml",
        )
        assert config.type == "bash"
        assert config.id == make_action_id("deploy")
        assert config.name == "Deploy Application"
        assert config.command == "kubectl apply -f deploy.yaml"
        assert config.env == {}
        assert config.metadata == {}
        assert config.tags == []

    def test_bash_action_config_with_env(self) -> None:
        """
        GIVEN: Bash action with environment variables
        WHEN: Creating a BashActionConfig
        THEN: Environment variables are stored
        """
        config = BashActionConfig(
            type="bash",
            id=make_action_id("deploy"),
            name="Deploy",
            command="deploy.sh",
            env={"ENV": "production", "REGION": "us-west-2"},
        )
        assert config.env == {"ENV": "production", "REGION": "us-west-2"}

    def test_python_action_config_minimal(self) -> None:
        """
        GIVEN: Minimal python action configuration
        WHEN: Creating a PythonActionConfig
        THEN: Configuration is created with required fields
        """
        config = PythonActionConfig(
            type="python",
            id=make_action_id("process"),
            name="Process Data",
            module="myapp.tasks",
            function="process_data",
        )
        assert config.type == "python"
        assert config.id == make_action_id("process")
        assert config.name == "Process Data"
        assert config.module == "myapp.tasks"
        assert config.function == "process_data"

    def test_action_discriminated_union(self) -> None:
        """
        GIVEN: Different action types
        WHEN: Using discriminated unions
        THEN: Pydantic discriminates based on 'type' field
        """
        bash_data = {
            "type": "bash",
            "id": "deploy",
            "name": "Deploy",
            "command": "deploy.sh",
        }
        python_data = {
            "type": "python",
            "id": "process",
            "name": "Process",
            "module": "app",
            "function": "run",
        }

        bash_config = BashActionConfig(**bash_data)
        python_config = PythonActionConfig(**python_data)

        assert bash_config.type == "bash"
        assert python_config.type == "python"


class TestOptionConfigs:
    """Test option configuration models."""

    def test_string_option_config(self) -> None:
        """
        GIVEN: String option configuration
        WHEN: Creating a StringOptionConfig
        THEN: Configuration is created correctly
        """
        config = StringOptionConfig(
            type="string",
            id=make_option_key("username"),
            name="Username",
            description="Enter your username",
            default="admin",
        )
        assert config.type == "string"
        assert config.id == make_option_key("username")
        assert config.name == "Username"
        assert config.description == "Enter your username"
        assert config.default == "admin"
        assert config.required is False

    def test_select_option_config(self) -> None:
        """
        GIVEN: Select option with choices
        WHEN: Creating a SelectOptionConfig
        THEN: Choices are stored correctly
        """
        config = SelectOptionConfig(
            type="select",
            id=make_option_key("environment"),
            name="Environment",
            description="Select environment",
            choices=["dev", "staging", "production"],
            default="dev",
        )
        assert config.type == "select"
        assert config.choices == ["dev", "staging", "production"]
        assert config.default == "dev"

    def test_path_option_config(self) -> None:
        """
        GIVEN: Path option configuration
        WHEN: Creating a PathOptionConfig
        THEN: Must_exist flag works correctly
        """
        config = PathOptionConfig(
            type="path",
            id=make_option_key("config_file"),
            name="Config File",
            description="Path to config file",
            must_exist=True,
            default="./config.yaml",
        )
        assert config.type == "path"
        assert config.must_exist is True
        assert config.default == "./config.yaml"

    def test_number_option_config(self) -> None:
        """
        GIVEN: Number option with constraints
        WHEN: Creating a NumberOptionConfig
        THEN: Constraints are stored correctly
        """
        config = NumberOptionConfig(
            type="number",
            id=make_option_key("port"),
            name="Port",
            description="Server port",
            min_value=1024,
            max_value=65535,
            default=8080,
        )
        assert config.type == "number"
        assert config.min_value == 1024
        assert config.max_value == 65535
        assert config.default == 8080

    def test_boolean_option_config(self) -> None:
        """
        GIVEN: Boolean option configuration
        WHEN: Creating a BooleanOptionConfig
        THEN: Configuration is created correctly
        """
        config = BooleanOptionConfig(
            type="boolean",
            id=make_option_key("verbose"),
            name="Verbose",
            description="Enable verbose logging",
            default=False,
        )
        assert config.type == "boolean"
        assert config.default is False

    def test_required_option(self) -> None:
        """
        GIVEN: Required option without default
        WHEN: Creating an option config
        THEN: Required flag is set appropriately
        """
        config = StringOptionConfig(
            type="string",
            id=make_option_key("api_key"),
            name="API Key",
            description="Required API key",
            required=True,
        )
        assert config.required is True
        assert config.default is None


class TestMenuConfig:
    """Test menu configuration for navigation."""

    def test_menu_config_creation(self) -> None:
        """
        GIVEN: Menu configuration data
        WHEN: Creating a MenuConfig
        THEN: Configuration is created correctly
        """
        config = MenuConfig(
            id=make_menu_id("settings_menu"),
            label="Settings",
            target=make_branch_id("settings_branch"),
        )
        assert config.id == make_menu_id("settings_menu")
        assert config.label == "Settings"
        assert config.target == make_branch_id("settings_branch")

    def test_menu_config_with_description(self) -> None:
        """
        GIVEN: Menu with optional description
        WHEN: Creating a MenuConfig
        THEN: Description is stored
        """
        config = MenuConfig(
            id=make_menu_id("advanced"),
            label="Advanced Settings",
            target=make_branch_id("advanced_branch"),
            description="Configure advanced options",
        )
        assert config.description == "Configure advanced options"


class TestBranchConfig:
    """Test branch configuration models."""

    def test_branch_config_minimal(self) -> None:
        """
        GIVEN: Minimal branch configuration
        WHEN: Creating a BranchConfig
        THEN: Configuration is created with defaults
        """
        config = BranchConfig(
            id=make_branch_id("main"),
            title="Main Menu",
        )
        assert config.id == make_branch_id("main")
        assert config.title == "Main Menu"
        assert config.description is None
        assert config.actions == []
        assert config.options == []
        assert config.menus == []

    def test_branch_config_with_actions(self) -> None:
        """
        GIVEN: Branch with actions
        WHEN: Creating a BranchConfig
        THEN: Actions are stored correctly
        """
        action = BashActionConfig(
            type="bash",
            id=make_action_id("deploy"),
            name="Deploy",
            command="deploy.sh",
        )
        config = BranchConfig(
            id=make_branch_id("deploy_branch"),
            title="Deploy Menu",
            actions=[action],
        )
        assert len(config.actions) == 1
        assert config.actions[0].id == make_action_id("deploy")

    def test_branch_config_with_options(self) -> None:
        """
        GIVEN: Branch with options
        WHEN: Creating a BranchConfig
        THEN: Options are stored correctly
        """
        option = StringOptionConfig(
            type="string",
            id=make_option_key("username"),
            name="Username",
            description="Enter username",
        )
        config = BranchConfig(
            id=make_branch_id("config_branch"),
            title="Configuration",
            options=[option],
        )
        assert len(config.options) == 1
        assert config.options[0].id == make_option_key("username")

    def test_branch_config_with_menus(self) -> None:
        """
        GIVEN: Branch with navigation menus
        WHEN: Creating a BranchConfig
        THEN: Menus are stored correctly
        """
        menu = MenuConfig(
            id=make_menu_id("settings"),
            label="Settings",
            target=make_branch_id("settings_branch"),
        )
        config = BranchConfig(
            id=make_branch_id("main"),
            title="Main Menu",
            menus=[menu],
        )
        assert len(config.menus) == 1
        assert config.menus[0].id == make_menu_id("settings")

    def test_branch_config_complete(self) -> None:
        """
        GIVEN: Branch with all components
        WHEN: Creating a complete BranchConfig
        THEN: All components are stored correctly
        """
        action = BashActionConfig(
            type="bash",
            id=make_action_id("deploy"),
            name="Deploy",
            command="deploy.sh",
        )
        option = StringOptionConfig(
            type="string",
            id=make_option_key("env"),
            name="Environment",
            description="Target environment",
        )
        menu = MenuConfig(
            id=make_menu_id("settings"),
            label="Settings",
            target=make_branch_id("settings"),
        )

        config = BranchConfig(
            id=make_branch_id("main"),
            title="Main Menu",
            description="Main application menu",
            actions=[action],
            options=[option],
            menus=[menu],
            metadata={"version": "1.0"},
            tags=["main", "entry"],
        )

        assert config.id == make_branch_id("main")
        assert config.title == "Main Menu"
        assert config.description == "Main application menu"
        assert len(config.actions) == 1
        assert len(config.options) == 1
        assert len(config.menus) == 1
        assert config.metadata == {"version": "1.0"}
        assert config.tags == ["main", "entry"]


class TestWizardConfig:
    """Test complete wizard configuration."""

    def test_wizard_config_minimal(self) -> None:
        """
        GIVEN: Minimal wizard configuration
        WHEN: Creating a WizardConfig
        THEN: Configuration is created with required fields
        """
        branch = BranchConfig(
            id=make_branch_id("main"),
            title="Main Menu",
        )
        config = WizardConfig(
            name="test-wizard",
            version="1.0.0",
            entry_branch=make_branch_id("main"),
            branches=[branch],
        )
        assert config.name == "test-wizard"
        assert config.version == "1.0.0"
        assert config.entry_branch == make_branch_id("main")
        assert len(config.branches) == 1

    def test_wizard_config_with_description(self) -> None:
        """
        GIVEN: Wizard with description
        WHEN: Creating a WizardConfig
        THEN: Description is stored
        """
        branch = BranchConfig(id=make_branch_id("main"), title="Main")
        config = WizardConfig(
            name="test-wizard",
            version="1.0.0",
            description="A test wizard",
            entry_branch=make_branch_id("main"),
            branches=[branch],
        )
        assert config.description == "A test wizard"

    def test_wizard_config_validates_entry_branch_exists(self) -> None:
        """
        GIVEN: Wizard with entry_branch that doesn't exist in branches
        WHEN: Creating a WizardConfig
        THEN: Validation should succeed (validation is runtime, not construction)
        """
        branch = BranchConfig(id=make_branch_id("main"), title="Main")
        # Entry branch points to non-existent branch - this is allowed at construction
        config = WizardConfig(
            name="test-wizard",
            version="1.0.0",
            entry_branch=make_branch_id("nonexistent"),
            branches=[branch],
        )
        assert config.entry_branch == make_branch_id("nonexistent")

    def test_wizard_config_multiple_branches(self) -> None:
        """
        GIVEN: Wizard with multiple branches
        WHEN: Creating a WizardConfig
        THEN: All branches are stored
        """
        main_branch = BranchConfig(id=make_branch_id("main"), title="Main")
        settings_branch = BranchConfig(id=make_branch_id("settings"), title="Settings")
        deploy_branch = BranchConfig(id=make_branch_id("deploy"), title="Deploy")

        config = WizardConfig(
            name="multi-branch-wizard",
            version="1.0.0",
            entry_branch=make_branch_id("main"),
            branches=[main_branch, settings_branch, deploy_branch],
        )
        assert len(config.branches) == 3


class TestSessionState:
    """Test session state model."""

    def test_session_state_defaults(self) -> None:
        """
        GIVEN: No initial state provided
        WHEN: Creating a SessionState
        THEN: Default values are used
        """
        state = SessionState()
        assert state.current_branch is None
        assert state.navigation_history == []
        assert state.option_values == {}
        assert state.variables == {}
        assert state.parse_mode == "interactive"
        assert state.command_history == []

    def test_session_state_with_current_branch(self) -> None:
        """
        GIVEN: Initial current branch
        WHEN: Creating a SessionState
        THEN: Current branch is set
        """
        state = SessionState(current_branch=make_branch_id("main"))
        assert state.current_branch == make_branch_id("main")

    def test_session_state_with_navigation_history(self) -> None:
        """
        GIVEN: Navigation history
        WHEN: Creating a SessionState
        THEN: History is stored
        """
        history = [make_branch_id("main"), make_branch_id("settings")]
        state = SessionState(navigation_history=history)
        assert state.navigation_history == history

    def test_session_state_with_option_values(self) -> None:
        """
        GIVEN: Option values
        WHEN: Creating a SessionState
        THEN: Values are stored
        """
        options = {
            make_option_key("username"): "admin",
            make_option_key("port"): 8080,
        }
        state = SessionState(option_values=options)
        assert state.option_values == options

    def test_session_state_with_variables(self) -> None:
        """
        GIVEN: Variables for interpolation
        WHEN: Creating a SessionState
        THEN: Variables are stored
        """
        variables = {"env": "production", "region": "us-west-2"}
        state = SessionState(variables=variables)
        assert state.variables == variables

    def test_session_state_with_parse_mode(self) -> None:
        """
        GIVEN: Custom parse mode
        WHEN: Creating a SessionState
        THEN: Parse mode is set
        """
        state = SessionState(parse_mode="shell")
        assert state.parse_mode == "shell"

    def test_session_state_with_command_history(self) -> None:
        """
        GIVEN: Command history
        WHEN: Creating a SessionState
        THEN: History is stored
        """
        history = ["deploy", "status", "help"]
        state = SessionState(command_history=history)
        assert state.command_history == history

    def test_session_state_complete(self) -> None:
        """
        GIVEN: Complete session state
        WHEN: Creating a SessionState
        THEN: All fields are stored correctly
        """
        state = SessionState(
            current_branch=make_branch_id("main"),
            navigation_history=[make_branch_id("main")],
            option_values={make_option_key("env"): "prod"},
            variables={"region": "us-west"},
            parse_mode="interactive",
            command_history=["help"],
        )
        assert state.current_branch == make_branch_id("main")
        assert len(state.navigation_history) == 1
        assert len(state.option_values) == 1
        assert len(state.variables) == 1
        assert state.parse_mode == "interactive"
        assert len(state.command_history) == 1


class TestResultTypes:
    """Test result types returned by protocols."""

    def test_action_result_success(self) -> None:
        """
        GIVEN: Successful action execution
        WHEN: Creating an ActionResult
        THEN: Success status is recorded
        """
        result = ActionResult(
            action_id=make_action_id("deploy"),
            success=True,
            output="Deployment successful",
        )
        assert result.action_id == make_action_id("deploy")
        assert result.success is True
        assert result.output == "Deployment successful"
        assert result.exit_code == 0

    def test_action_result_failure(self) -> None:
        """
        GIVEN: Failed action execution
        WHEN: Creating an ActionResult
        THEN: Failure status and error are recorded
        """
        result = ActionResult(
            action_id=make_action_id("deploy"),
            success=False,
            output="Deployment failed",
            exit_code=1,
            error="Connection timeout",
        )
        assert result.success is False
        assert result.exit_code == 1
        assert result.error == "Connection timeout"

    def test_collection_result_success(self) -> None:
        """
        GIVEN: Successful option collection
        WHEN: Creating a CollectionResult
        THEN: Collected value is stored
        """
        result = CollectionResult(
            option_key=make_option_key("username"),
            success=True,
            value="admin",
        )
        assert result.option_key == make_option_key("username")
        assert result.success is True
        assert result.value == "admin"
        assert result.error is None

    def test_collection_result_failure(self) -> None:
        """
        GIVEN: Failed option collection
        WHEN: Creating a CollectionResult
        THEN: Error is recorded
        """
        result = CollectionResult(
            option_key=make_option_key("port"),
            success=False,
            value=None,
            error="Invalid port number",
        )
        assert result.success is False
        assert result.value is None
        assert result.error == "Invalid port number"

    def test_navigation_result_success(self) -> None:
        """
        GIVEN: Successful navigation
        WHEN: Creating a NavigationResult
        THEN: Target branch is recorded
        """
        result = NavigationResult(
            success=True,
            target=make_branch_id("settings"),
        )
        assert result.success is True
        assert result.target == make_branch_id("settings")
        assert result.error is None

    def test_navigation_result_failure(self) -> None:
        """
        GIVEN: Failed navigation
        WHEN: Creating a NavigationResult
        THEN: Error is recorded
        """
        result = NavigationResult(
            success=False,
            target=make_branch_id("invalid"),
            error="Branch not found",
        )
        assert result.success is False
        assert result.error == "Branch not found"


class TestPydanticValidation:
    """Test Pydantic validation features."""

    def test_required_fields_validation(self) -> None:
        """
        GIVEN: Missing required fields
        WHEN: Creating a model
        THEN: ValidationError is raised
        """
        with pytest.raises(ValidationError):
            BashActionConfig(type="bash", name="Deploy")  # Missing id and command

    def test_type_field_validation(self) -> None:
        """
        GIVEN: Invalid type field
        WHEN: Creating an action config
        THEN: ValidationError is raised
        """
        with pytest.raises(ValidationError):
            BashActionConfig(
                type="invalid",  # Should be "bash"
                id=make_action_id("deploy"),
                name="Deploy",
                command="deploy.sh",
            )

    def test_json_serialization(self) -> None:
        """
        GIVEN: A valid model
        WHEN: Serializing to JSON
        THEN: JSON is correctly formatted
        """
        config = BashActionConfig(
            type="bash",
            id=make_action_id("deploy"),
            name="Deploy",
            command="deploy.sh",
        )
        json_data = config.model_dump()
        assert json_data["type"] == "bash"
        assert json_data["id"] == "deploy"
        assert json_data["name"] == "Deploy"
        assert json_data["command"] == "deploy.sh"

    def test_json_deserialization(self) -> None:
        """
        GIVEN: JSON data
        WHEN: Deserializing to model
        THEN: Model is correctly created
        """
        json_data = {
            "type": "bash",
            "id": "deploy",
            "name": "Deploy",
            "command": "deploy.sh",
        }
        config = BashActionConfig(**json_data)
        assert config.id == make_action_id("deploy")
        assert config.name == "Deploy"
