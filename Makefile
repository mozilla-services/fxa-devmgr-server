SHELL := /bin/sh

HERE = $(shell pwd)
BIN := $(HERE)/bin
PATH := $(BIN):$(PATH)

PYTHON := $(BIN)/python
VTENV_OPTS ?= -p `which python3.4 | head -n 1`
VIRTUALENV = virtualenv

BUILD_DIRS = bin include lib src .tox .eggs .coverage

.PHONY: all build clean

all: build

$(PYTHON):
	$(VIRTUALENV) $(VTENV_OPTS) .

build: $(PYTHON)
	$(PYTHON) setup.py develop

clean:
	rm -rf $(BUILD_DIRS)
