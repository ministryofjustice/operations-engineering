.PHONY: all clean test local-setup

all: local-setup

clean:
    # Commands to clean the project

test:
    # Commands to run tests

local-setup:
    brew install pre-commit && pre-commit install
