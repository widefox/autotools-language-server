# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a language server implementation for autotools (make, configure.ac, Makefile.am) that provides IDE features like diagnostics, hover, completion, go-to-definition, and find-references. The implementation uses tree-sitter for parsing and pygls for the Language Server Protocol.

## Development Setup

Install dependencies:
```bash
pip install -e '.[dev]'
```

## Key Commands

### Testing
```bash
# Run all tests with coverage
pytest --cov

# Run a specific test file
pytest tests/test_finders.py

# Run a specific test method
pytest tests/test_finders.py::Test::test_DefinitionFinder
```

### Linting
```bash
# Run all pre-commit hooks
pre-commit run --all-files

# Run specific hook
pre-commit run ruff-check --all-files
pre-commit run pyright --all-files
```

### Building
```bash
pyproject-build
```

### Checking Files
```bash
# Check makefile for errors
make-language-server --check path/to/Makefile

# Generate schema
make-language-server --generate-schema make --output-format json
```

## Architecture

### Dual Language Server Design

The codebase implements **two separate language servers** that share similar patterns:

1. **`make_language_server`**: Full-featured server for Makefiles
   - Located in `src/make_language_server/`
   - Implements all LSP features using tree-sitter
   - Has custom finders for definitions, references, and diagnostics

2. **`autoconf_language_server`**: Simpler server for configure.ac files
   - Located in `src/autoconf_language_server/`
   - Implements hover and completion only (no tree-sitter parsing)
   - Uses simpler text-based matching

### Key Components

#### Server (`server.py`)
- Main language server class extending `pygls.lsp.server.LanguageServer`
- Stores syntax trees in `self.trees` dictionary keyed by document URI
- Registers LSP feature handlers using decorators (`@self.feature()`)
- For make: `MakeLanguageServer` with full LSP features
- For autoconf: `AutoconfLanguageServer` with limited features

#### Finders (`finders.py` - make only)
Custom finder classes that extend `lsp-tree-sitter` base finders:
- **`DefinitionFinder`**: Finds variable/function/target definitions
  - Handles variable assignments, define directives, and target rules
  - Different logic based on parent node type
- **`ReferenceFinder`**: Finds all references to a symbol
  - Inverse of DefinitionFinder logic
- **`InvalidPathFinder`**: Diagnostic finder for missing include files
- **`RepeatedTargetFinder`**: Diagnostic finder for duplicate targets
- **`ErrorFinder`**: Tree-sitter syntax error detection (from lsp-tree-sitter)

All finder classes work by:
1. Taking a tree-sitter node as input
2. Filtering nodes based on type and context
3. Returning `UNI` (Universal Node Interface) objects with location info

#### Utils (`utils.py`)
- **Parser setup**: Configures tree-sitter parser with `tree_sitter_make` language
- **Schema loading**: Loads JSON schemas from `assets/json/` for completions/hover
- **Query loading**: Loads tree-sitter queries from `assets/queries/` (.scm files)
- Caches schemas and queries in module-level dictionaries

#### Assets
- `assets/json/`: JSON schemas containing function/macro documentation
- `assets/queries/`: Tree-sitter query files (.scm) for pattern matching
  - Used by finders to locate specific syntax patterns
  - Example: `include.scm` finds include directives with paths

### LSP Feature Implementation Pattern

Each LSP feature follows this pattern:
1. Get document from workspace
2. Get syntax tree from `self.trees[uri]`
3. Use `PositionFinder` to get node at cursor
4. Use specialized finder to get results
5. Return LSP-compatible data structure

Example (go-to-definition):
```python
uni = PositionFinder(params.position).find(document.uri, self.trees[document.uri])
return [uni.location for uni in DefinitionFinder(uni.node).find_all(...)]
```

## Code Style

- Python 3.10+ (uses modern type hints like `Hover | None`)
- Ruff for linting and formatting (line length: 79)
- Docstrings use reStructuredText format
- Type hints required (checked by pyright)

## Testing

Tests are in `tests/` directory:
- Use pytest framework
- Test fixtures include test Makefiles
- Tests access syntax tree nodes by index (`tree.root_node.children[13]...`)
- Coverage reporting enabled

## Important Notes

- The project is built on top of `lsp-tree-sitter` which provides base finder classes
- Tree-sitter parsing only available for Makefiles (using `tree-sitter-make`)
- Autoconf server uses schema-based completion only (no parsing)
- The `query()` method has been deprecated (see commit c038244)
