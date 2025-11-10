# Autotools Language Server Examples

This directory contains example files that demonstrate the features of the autotools-language-server.

## Files

### configure.ac
An example autoconf configuration file showing:
- Package initialization with `AC_INIT`
- Program checks (`AC_PROG_CC`, `AC_PROG_INSTALL`)
- Library checks (`AC_CHECK_LIB`)
- Header file checks (`AC_CHECK_HEADERS`)
- Custom variables and substitutions
- Conditional compilation features
- Configuration file generation

### Makefile.am
An example automake file demonstrating:
- Program building with `bin_PROGRAMS`
- Library creation with `lib_LTLIBRARIES`
- Source file definitions
- Compiler flags configuration
- Script and data file installation
- Custom targets
- Test integration

### Makefile
A comprehensive GNU Make example showing:
- Variable definitions and assignments
- Pattern rules and implicit rules
- Phony targets
- Conditional compilation
- Functions and macros
- Automatic dependency generation
- Multiple build configurations (debug/release)
- Installation targets

## Usage

These files serve as:
1. **Reference examples** - Learn autotools syntax and conventions
2. **Testing files** - Test the language server features (hover, completion, goto definition, etc.)
3. **Development aid** - Use as templates for new projects

## Testing the Language Server

Open any of these files in your editor with the autotools-language-server installed to test:
- **Hover**: Hover over functions, variables, and targets to see documentation
- **Completion**: Trigger auto-completion for autotools macros and Make functions
- **Goto Definition**: Jump to variable or target definitions
- **Find References**: Find all uses of variables and targets
- **Diagnostics**: See syntax errors and warnings
