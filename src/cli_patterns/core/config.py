"""Configuration for CLI Patterns core behavior.

This module provides security and runtime configuration through environment
variables and TypedDict configurations.
"""

from __future__ import annotations

import os
from typing import TypedDict


class SecurityConfig(TypedDict):
    """Security configuration settings.

    These settings control security features like validation strictness,
    DoS protection limits, and shell feature permissions.
    """

    enable_validation: bool
    """Enable strict validation for all factory functions.

    When True, factory functions perform validation on inputs.
    Default: False (for performance in development).
    Recommended for production: True
    """

    max_json_depth: int
    """Maximum nesting depth for JSON values.

    Prevents DoS attacks via deeply nested structures.
    Default: 50 levels
    """

    max_collection_size: int
    """Maximum size for collections.

    Prevents memory exhaustion from large data structures.
    Default: 1000 items
    """

    allow_shell_features: bool
    """Allow shell features by default (INSECURE).

    When True, shell features (pipes, redirects, etc.) are allowed by default.
    Default: False (secure)
    WARNING: Setting this to True is a security risk. Always use per-action
    configuration instead.
    """


def get_security_config() -> SecurityConfig:
    """Get security configuration from environment variables.

    Environment Variables:
        CLI_PATTERNS_ENABLE_VALIDATION: Enable strict validation (default: false)
            Set to 'true' to enable validation in factory functions.

        CLI_PATTERNS_MAX_JSON_DEPTH: Max JSON nesting depth (default: 50)
            Controls maximum depth for nested data structures.

        CLI_PATTERNS_MAX_COLLECTION_SIZE: Max collection size (default: 1000)
            Controls maximum number of items in collections.

        CLI_PATTERNS_ALLOW_SHELL: Allow shell features globally (default: false)
            WARNING: Setting to 'true' is insecure. Use per-action configuration.

    Returns:
        SecurityConfig with settings from environment or defaults

    Example:
        >>> os.environ['CLI_PATTERNS_ENABLE_VALIDATION'] = 'true'
        >>> config = get_security_config()
        >>> config['enable_validation']
        True
    """
    return SecurityConfig(
        enable_validation=os.getenv("CLI_PATTERNS_ENABLE_VALIDATION", "false").lower()
        == "true",
        max_json_depth=int(os.getenv("CLI_PATTERNS_MAX_JSON_DEPTH", "50")),
        max_collection_size=int(os.getenv("CLI_PATTERNS_MAX_COLLECTION_SIZE", "1000")),
        allow_shell_features=os.getenv("CLI_PATTERNS_ALLOW_SHELL", "false").lower()
        == "true",
    )


# Global config instance (cached)
_security_config: SecurityConfig | None = None


def get_config() -> SecurityConfig:
    """Get global security config (cached).

    This function caches the configuration on first call to avoid
    repeated environment variable lookups.

    Returns:
        Cached SecurityConfig instance

    Example:
        >>> config = get_config()
        >>> if config['enable_validation']:
        ...     # Perform validation
        ...     pass
    """
    global _security_config
    if _security_config is None:
        _security_config = get_security_config()
    return _security_config


def reset_config() -> None:
    """Reset cached configuration.

    This is primarily useful for testing when you need to reload
    configuration from environment variables.

    Example:
        >>> reset_config()
        >>> # Config will be reloaded on next get_config() call
    """
    global _security_config
    _security_config = None
