# Example configure.ac for autotools-language-server
# This is a simple autoconf configuration file demonstrating basic features

AC_PREREQ([2.69])
AC_INIT([example-project], [1.0.0], [bug-report@example.com])
AC_CONFIG_SRCDIR([src/main.c])
AC_CONFIG_HEADERS([config.h])
AM_INIT_AUTOMAKE([-Wall -Werror foreign])

# Checks for programs
AC_PROG_CC
AC_PROG_INSTALL
AC_PROG_MAKE_SET

# Checks for libraries
AC_CHECK_LIB([m], [sqrt])
AC_CHECK_LIB([pthread], [pthread_create])

# Checks for header files
AC_CHECK_HEADERS([stdlib.h string.h unistd.h])

# Checks for typedefs, structures, and compiler characteristics
AC_TYPE_SIZE_T
AC_TYPE_SSIZE_T

# Checks for library functions
AC_FUNC_MALLOC
AC_CHECK_FUNCS([memset strchr strdup])

# Optional features
AC_ARG_ENABLE([debug],
    AS_HELP_STRING([--enable-debug], [Enable debug mode]))

AS_IF([test "x$enable_debug" = "xyes"], [
    AC_DEFINE([DEBUG], [1], [Define to 1 if debug mode is enabled])
    CFLAGS="$CFLAGS -g -O0"
], [
    CFLAGS="$CFLAGS -O2"
])

# Custom variables
MY_VAR="example value"
AC_SUBST([MY_VAR])

# Output files
AC_CONFIG_FILES([
    Makefile
    src/Makefile
    tests/Makefile
])

AC_OUTPUT
