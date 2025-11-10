# Example Makefile for autotools-language-server
# This demonstrates various Makefile features and syntax

# Variables
CC := gcc
CXX := g++
CFLAGS := -Wall -Wextra -std=c99
CXXFLAGS := -Wall -Wextra -std=c++11
LDFLAGS := -lm -lpthread
PREFIX := /usr/local
DESTDIR ?=

# Source and object files
SOURCES := main.c utils.c helper.c
HEADERS := utils.h helper.h
OBJECTS := $(SOURCES:.c=.o)
TARGET := example-program

# Directories
SRC_DIR := src
BUILD_DIR := build
OBJ_DIR := $(BUILD_DIR)/obj
BIN_DIR := $(BUILD_DIR)/bin

# Pattern rules
%.o: %.c $(HEADERS)
	$(CC) $(CFLAGS) -c $< -o $@

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Default target
.DEFAULT_GOAL := all

# Phony targets
.PHONY: all clean install uninstall test help

# Main targets
all: $(TARGET)

$(TARGET): $(OBJECTS)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

# Build with debug symbols
debug: CFLAGS += -g -O0 -DDEBUG
debug: clean $(TARGET)

# Build with optimization
release: CFLAGS += -O3 -DNDEBUG
release: clean $(TARGET)

# Clean build artifacts
clean:
	rm -f $(OBJECTS) $(TARGET)
	rm -rf $(BUILD_DIR)

# Install the program
install: $(TARGET)
	install -d $(DESTDIR)$(PREFIX)/bin
	install -m 755 $(TARGET) $(DESTDIR)$(PREFIX)/bin/

# Uninstall the program
uninstall:
	rm -f $(DESTDIR)$(PREFIX)/bin/$(TARGET)

# Run tests
test: $(TARGET)
	./$(TARGET) --test
	@echo "All tests passed!"

# Static code analysis
check: $(SOURCES)
	cppcheck --enable=all $^

# Generate documentation
docs:
	doxygen Doxyfile

# Create distribution tarball
DIST_NAME := example-1.0.0
dist: clean
	mkdir -p $(DIST_NAME)
	cp -r $(SOURCES) $(HEADERS) Makefile README.md $(DIST_NAME)/
	tar czf $(DIST_NAME).tar.gz $(DIST_NAME)
	rm -rf $(DIST_NAME)

# Conditional compilation
ifdef DEBUG
CFLAGS += -g -O0
else
CFLAGS += -O2
endif

# Functions
define compile-source
	@echo "Compiling $(1)..."
	$(CC) $(CFLAGS) -c $(1) -o $(2)
endef

# Include additional makefiles
-include dependencies.mk

# Special variables examples
info:
	@echo "Target: $@"
	@echo "First prerequisite: $<"
	@echo "All prerequisites: $^"
	@echo "Changed prerequisites: $?"
	@echo "Target stem: $*"
	@echo "Current directory: $(CURDIR)"

# Help target
help:
	@echo "Available targets:"
	@echo "  all      - Build the program (default)"
	@echo "  debug    - Build with debug symbols"
	@echo "  release  - Build with optimizations"
	@echo "  clean    - Remove build artifacts"
	@echo "  install  - Install the program"
	@echo "  uninstall - Uninstall the program"
	@echo "  test     - Run tests"
	@echo "  check    - Run static analysis"
	@echo "  docs     - Generate documentation"
	@echo "  dist     - Create distribution tarball"
	@echo "  help     - Show this help message"

# Export/unexport variables
export PATH
unexport TEMP_VAR

# Automatic dependencies
-include $(OBJECTS:.o=.d)

%.d: %.c
	@$(CC) -MM $(CFLAGS) $< > $@
