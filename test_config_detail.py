#!/usr/bin/env python3
"""Test configuration filtering in detail."""

import sys
from pathlib import Path

from make_language_server.config import MakeLanguageServerConfig, set_config
from make_language_server.filtered_finders import get_configurable_finder_classes
from make_language_server.utils import parser
from lsp_tree_sitter.diagnose import get_diagnostics


def test_file_detail(filepath: str):
    """Test a file and show all diagnostics."""
    # Load configuration
    config = MakeLanguageServerConfig.find_and_load(filepath)
    set_config(config)

    # Read and parse file
    with open(filepath, 'rb') as f:
        content = f.read()

    tree = parser.parse(content)
    file_uri = f"file://{Path(filepath).absolute()}"

    # Get diagnostics
    finder_classes = get_configurable_finder_classes()
    diagnostics = get_diagnostics(file_uri, tree, finder_classes)

    print(f"\n{filepath}:")
    print(f"Total diagnostics: {len(diagnostics)}")

    if diagnostics:
        print("\nAll diagnostics:")
        for i, diag in enumerate(diagnostics[:10], 1):
            print(f"{i}. [{diag.severity}] {diag.message}")
            print(f"   Range: {diag.range.start.line}:{diag.range.start.character}")


def main():
    """Main function."""
    test_file_detail('examples/Linux/Makefile')
    return 0


if __name__ == '__main__':
    sys.exit(main())
