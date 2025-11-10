r"""Filtered Finders
====================

Diagnostic finders that support configuration-based error filtering
to suppress false positives from tree-sitter-make grammar limitations.
"""

import re
from dataclasses import dataclass, field

from lsp_tree_sitter.finders import ErrorFinder, RepeatedFinder
from lsprotocol.types import Diagnostic, DiagnosticSeverity
from tree_sitter import Tree

from .config import DiagnosticsConfig, get_config


@dataclass
class ConfigurableErrorFinder(ErrorFinder):
    """Error finder that respects configuration settings.

    This finder extends ErrorFinder to filter diagnostics based on
    configuration, suppressing known false positives.
    """

    _compiled_patterns: list[re.Pattern] | None = field(
        default=None, init=False, repr=False
    )
    _current_config: DiagnosticsConfig | None = field(
        default=None, init=False, repr=False
    )

    def _get_compiled_patterns(
        self, config: DiagnosticsConfig
    ) -> list[re.Pattern]:
        """Get compiled regex patterns, with caching.

        :param config: Diagnostics configuration
        :type config: DiagnosticsConfig
        :rtype: list[re.Pattern]
        """
        # Cache compiled patterns for performance
        if self._compiled_patterns is None or self._current_config != config:
            self._compiled_patterns = [
                re.compile(pattern)
                for pattern in config.suppressed_error_patterns
            ]
            self._current_config = config

        return self._compiled_patterns

    def is_suppressed(self, error_text: str, config: DiagnosticsConfig) -> bool:
        """Check if an error should be suppressed.

        :param error_text: The error message text
        :type error_text: str
        :param config: Diagnostics configuration
        :type config: DiagnosticsConfig
        :rtype: bool
        """
        if not config.suppress_false_positives:
            return False

        patterns = self._get_compiled_patterns(config)
        return any(pattern.search(error_text) for pattern in patterns)

    def get_diagnostics(self, uri: str, tree: Tree) -> list[Diagnostic]:
        """Get diagnostics, applying configuration filters.

        :param uri: File URI
        :type uri: str
        :param tree: Parsed tree
        :type tree: Tree
        :rtype: list[Diagnostic]
        """
        config = get_config(uri).diagnostics

        # Get diagnostics from parent
        diagnostics = super().get_diagnostics(uri, tree)

        # Filter based on configuration
        filtered = []
        for diagnostic in diagnostics:
            # Check max errors limit
            if config.max_errors > 0 and len(filtered) >= config.max_errors:
                # Add info diagnostic about suppressed errors
                filtered.append(
                    Diagnostic(
                        range=diagnostic.range,
                        message=(
                            f"Too many errors ({config.max_errors}+). "
                            "Additional errors suppressed. "
                            "This may indicate tree-sitter-make grammar "
                            "limitations with advanced GNU Make syntax."
                        ),
                        severity=DiagnosticSeverity.Information,
                    )
                )
                break

            # Check if error should be suppressed
            if self.is_suppressed(diagnostic.message, config):
                continue

            filtered.append(diagnostic)

        return filtered


@dataclass
class ConfigurableRepeatedTargetFinder(RepeatedFinder):
    """Repeated target finder that respects configuration.

    Can be disabled via configuration for projects that intentionally
    use repeated targets (like Linux kernel Makefiles).
    """

    def get_diagnostics(self, uri: str, tree: Tree) -> list[Diagnostic]:
        """Get diagnostics, respecting configuration.

        :param uri: File URI
        :type uri: str
        :param tree: Parsed tree
        :type tree: Tree
        :rtype: list[Diagnostic]
        """
        config = get_config(uri).diagnostics

        # Skip if repeated targets are allowed
        if config.allow_repeated_targets:
            return []

        # Otherwise use parent implementation
        return super().get_diagnostics(uri, tree)


# Export configurable finder classes
def get_configurable_finder_classes() -> list[type]:
    """Get list of configurable finder classes.

    :rtype: list[type]
    """
    from .finders import InvalidPathFinder

    return [
        ConfigurableErrorFinder,
        InvalidPathFinder,
        ConfigurableRepeatedTargetFinder,
    ]
