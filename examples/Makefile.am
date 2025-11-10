# Example Makefile.am for autotools-language-server
# This is a sample automake file demonstrating various features

# Subdirectories to build
SUBDIRS = src tests

# Additional files to distribute
EXTRA_DIST = README.md AUTHORS COPYING

# Programs to build
bin_PROGRAMS = example-program
example_program_SOURCES = main.c utils.c utils.h
example_program_CFLAGS = $(AM_CFLAGS) -Wall -Wextra
example_program_LDADD = $(LDADD) -lm

# Libraries to build
lib_LTLIBRARIES = libexample.la
libexample_la_SOURCES = lib.c lib.h
libexample_la_CFLAGS = $(AM_CFLAGS)
libexample_la_LDFLAGS = -version-info 1:0:0

# Headers to install
include_HEADERS = example.h

# Scripts to install
dist_bin_SCRIPTS = example-script.sh

# Data files
pkgdata_DATA = example.conf
example.conf: example.conf.in
	$(SED) 's|@prefix@|$(prefix)|g' $< > $@

# Man pages
man_MANS = example.1

# Custom targets
.PHONY: custom-target
custom-target:
	@echo "Running custom target"

# Variables
AM_CPPFLAGS = -I$(top_srcdir)/include
AM_CFLAGS = -std=c99 -pedantic

# Clean up generated files
CLEANFILES = example.conf
DISTCLEANFILES = *~

# Tests
TESTS = test-example
check_PROGRAMS = test-example
test_example_SOURCES = test.c
test_example_LDADD = libexample.la
