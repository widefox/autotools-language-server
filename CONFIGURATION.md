# Configuration Guide

The autotools-language-server supports project-specific configuration through `.autotools-ls.json` files.

## Configuration File

Place a `.autotools-ls.json` file in your project root or any parent directory. The language server will search up the directory tree and use the first configuration file it finds.

### Example Configuration

```json
{
  "diagnostics": {
    "suppress_false_positives": true,
    "max_errors": 100,
    "suppressed_error_patterns": [
      "= -.*: error",
      "= --.*: error",
      "^=:? error$"
    ],
    "allow_repeated_targets": false,
    "check_includes": true
  },
  "performance": {
    "max_file_size": 10485760,
    "max_lines": 0,
    "log_performance": false
  }
}
```

## Configuration Options

### Diagnostics Section

#### `suppress_false_positives` (boolean, default: `true`)

Enable automatic suppression of known false positive errors from tree-sitter-make grammar limitations.

When `true`, the language server will filter out parse errors that match known patterns caused by advanced GNU Make syntax that the parser doesn't fully support.

**Example:**
```json
{
  "diagnostics": {
    "suppress_false_positives": true
  }
}
```

#### `max_errors` (integer, default: `100`)

Maximum number of errors to report per file before suppressing additional errors.

This prevents overwhelming the UI when a file has many parse errors. When the limit is reached, an informational diagnostic is added explaining that more errors exist.

Set to `0` for unlimited errors.

**Example:**
```json
{
  "diagnostics": {
    "max_errors": 50
  }
}
```

#### `suppressed_error_patterns` (array of strings, default: see below)

Regular expression patterns for error messages to suppress.

**Default patterns:**
- `"= -.*: error"` - Dynamic variable assignments with flags: `var-$(CONFIG) := -fflag`
- `"= --.*: error"` - Dynamic variable assignments with long flags: `var-$(CONFIG) := --flag`
- `"^=:? error$"` - Generic assignment operator errors
- `"^\\(: error$"` - Parentheses errors from `$(VAR)` in variable names
- `"^,\\): error$"` - Function call syntax errors
- `":/=: error$"` - Path substitution errors
- `"^,: error$"` - Comma in function arguments
- `"^\\|: error$"` - Order-only prerequisites (pipe character)
- `"^;: error$"` - Inline command separator

You can override these patterns completely or add to them.

**Example (add custom patterns):**
```json
{
  "diagnostics": {
    "suppressed_error_patterns": [
      "= -.*: error",
      "= --.*: error",
      "my-custom-pattern: error"
    ]
  }
}
```

#### `allow_repeated_targets` (boolean, default: `true`)

Allow repeated target definitions without warnings.

Many Makefiles (especially Linux kernel Makefiles) intentionally use repeated target declarations to add different prerequisites in multiple places:

```makefile
prepare: scripts
prepare: prepare0
prepare: archprepare
```

When `true`, these repeated targets do not generate warnings.

**Example:**
```json
{
  "diagnostics": {
    "allow_repeated_targets": false
  }
}
```

#### `check_includes` (boolean, default: `true`)

Check that included files exist.

When `true`, the language server will report errors for `include` directives that reference non-existent files. For large projects with generated includes, you may want to disable this.

**Example:**
```json
{
  "diagnostics": {
    "check_includes": false
  }
}
```

### Performance Section

#### `max_file_size` (integer, default: `10485760`)

Maximum file size in bytes to process (default: 10 MB).

Files larger than this will not be processed. Set to `0` for unlimited.

**Example:**
```json
{
  "performance": {
    "max_file_size": 5242880
  }
}
```

#### `max_lines` (integer, default: `0`)

Maximum number of lines to process (default: unlimited).

Files with more lines than this will not be processed. Set to `0` for unlimited.

**Example:**
```json
{
  "performance": {
    "max_lines": 10000
  }
}
```

#### `log_performance` (boolean, default: `false`)

Enable performance logging.

When `true`, the language server will log timing information for parsing and diagnostics.

**Example:**
```json
{
  "performance": {
    "log_performance": true
  }
}
```

## Use Cases

### For Linux Kernel Development

```json
{
  "diagnostics": {
    "suppress_false_positives": true,
    "allow_repeated_targets": true,
    "check_includes": false,
    "max_errors": 100
  }
}
```

This configuration:
- Suppresses false positives from dynamic variable names
- Allows repeated targets (used throughout the kernel)
- Doesn't check includes (many are generated during build)
- Limits errors to avoid overwhelming the UI

### For Standard Makefiles

```json
{
  "diagnostics": {
    "suppress_false_positives": false,
    "allow_repeated_targets": false,
    "check_includes": true,
    "max_errors": 0
  }
}
```

This configuration:
- Shows all errors (no suppression)
- Warns about repeated targets
- Checks that all includes exist
- No error limit

### For Very Large Codebases

```json
{
  "diagnostics": {
    "suppress_false_positives": true,
    "max_errors": 50
  },
  "performance": {
    "max_file_size": 5242880,
    "log_performance": true
  }
}
```

This configuration:
- Suppresses false positives
- Limits errors per file to 50
- Doesn't process files larger than 5 MB
- Logs performance metrics

## Configuration Precedence

The language server searches for configuration files in the following order:

1. In the same directory as the Makefile being edited
2. In parent directories, up to the file system root
3. If no configuration file is found, uses default settings

You can place different configuration files in different directories to have different settings for different parts of your project.

## Testing Your Configuration

To test if your configuration is working:

1. Create a `.autotools-ls.json` file in your project root
2. Open a Makefile in your editor
3. Check the diagnostics/errors reported
4. Adjust patterns or settings as needed

You can also use the command-line tool to check a file:

```bash
make-language-server --check path/to/Makefile
```

## See Also

- [Performance Analysis](PERFORMANCE_ANALYSIS.md) - Performance characteristics and recommendations
- [Linux Kernel Testing](LINUX_KERNEL_TESTING.md) - Testing with Linux kernel Makefiles
- Example configuration: [.autotools-ls.json.example](.autotools-ls.json.example)
