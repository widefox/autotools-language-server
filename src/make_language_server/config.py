r"""Configuration Management
============================

Load and manage configuration for the make language server.
Supports project-specific settings via .autotools-ls.json files.
"""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class DiagnosticsConfig:
    """Configuration for diagnostics."""

    # Whether to suppress known false positive error patterns
    suppress_false_positives: bool = True

    # Maximum number of errors to report per file
    max_errors: int = 100

    # Error patterns to suppress (regex patterns)
    suppressed_error_patterns: list[str] = field(default_factory=lambda: [
        r'= -.*: error',  # Flags that look like operators: = -fstack-protector
        r'= --.*: error',  # Long flags: = --foo-bar
        r'^=:? error$',  # Generic assignment operator errors
        r'^\(: error$',  # Parentheses errors from $(VAR) in names
        r'^,\): error$',  # Function call syntax
        r':/=: error$',  # Path substitutions
        r'^,: error$',  # Comma in function arguments
        r'^\|: error$',  # Order-only prerequisites
        r'^;: error$',  # Inline commands
    ])

    # Whether to allow repeated target definitions
    allow_repeated_targets: bool = True

    # Whether to check included files
    check_includes: bool = True


@dataclass
class PerformanceConfig:
    """Configuration for performance tuning."""

    # Maximum file size to process (bytes, 0 = unlimited)
    max_file_size: int = 10 * 1024 * 1024  # 10 MB

    # Maximum lines to process (0 = unlimited)
    max_lines: int = 0

    # Enable performance logging
    log_performance: bool = False


@dataclass
class MakeLanguageServerConfig:
    """Main configuration for make language server."""

    diagnostics: DiagnosticsConfig = field(default_factory=DiagnosticsConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MakeLanguageServerConfig":
        """Create config from dictionary.

        :param data: Configuration dictionary
        :type data: dict[str, Any]
        :rtype: MakeLanguageServerConfig
        """
        config = cls()

        if diag_data := data.get("diagnostics"):
            config.diagnostics = DiagnosticsConfig(
                suppress_false_positives=diag_data.get(
                    "suppress_false_positives",
                    config.diagnostics.suppress_false_positives,
                ),
                max_errors=diag_data.get(
                    "max_errors",
                    config.diagnostics.max_errors,
                ),
                suppressed_error_patterns=diag_data.get(
                    "suppressed_error_patterns",
                    config.diagnostics.suppressed_error_patterns,
                ),
                allow_repeated_targets=diag_data.get(
                    "allow_repeated_targets",
                    config.diagnostics.allow_repeated_targets,
                ),
                check_includes=diag_data.get(
                    "check_includes",
                    config.diagnostics.check_includes,
                ),
            )

        if perf_data := data.get("performance"):
            config.performance = PerformanceConfig(
                max_file_size=perf_data.get(
                    "max_file_size",
                    config.performance.max_file_size,
                ),
                max_lines=perf_data.get(
                    "max_lines",
                    config.performance.max_lines,
                ),
                log_performance=perf_data.get(
                    "log_performance",
                    config.performance.log_performance,
                ),
            )

        return config

    @classmethod
    def load_from_file(cls, filepath: str | Path) -> "MakeLanguageServerConfig":
        """Load configuration from a JSON file.

        :param filepath: Path to config file
        :type filepath: str | Path
        :rtype: MakeLanguageServerConfig
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            return cls.from_dict(data)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            # Return default config if file doesn't exist or is invalid
            return cls()

    @classmethod
    def find_and_load(cls, start_path: str | Path) -> "MakeLanguageServerConfig":
        """Find and load configuration file starting from a path.

        Searches for .autotools-ls.json in current directory and parent
        directories up to the root.

        :param start_path: Path to start searching from
        :type start_path: str | Path
        :rtype: MakeLanguageServerConfig
        """
        config_filename = ".autotools-ls.json"
        current = Path(start_path).resolve()

        # If start_path is a file, start from its directory
        if current.is_file():
            current = current.parent

        # Search up to root
        while True:
            config_path = current / config_filename
            if config_path.exists():
                return cls.load_from_file(config_path)

            # Check if we've reached the root
            parent = current.parent
            if parent == current:
                break
            current = parent

        # No config file found, return defaults
        return cls()


# Global configuration instance
_global_config: MakeLanguageServerConfig | None = None


def get_config(uri: str | None = None) -> MakeLanguageServerConfig:
    """Get configuration for a file URI or use global config.

    :param uri: File URI (optional)
    :type uri: str | None
    :rtype: MakeLanguageServerConfig
    """
    global _global_config

    if uri:
        # Try to find config file near the URI
        path = uri.replace("file://", "")
        return MakeLanguageServerConfig.find_and_load(path)

    # Return or create global config
    if _global_config is None:
        _global_config = MakeLanguageServerConfig()

    return _global_config


def set_config(config: MakeLanguageServerConfig) -> None:
    """Set global configuration.

    :param config: Configuration to set
    :type config: MakeLanguageServerConfig
    :rtype: None
    """
    global _global_config
    _global_config = config
