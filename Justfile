# Load environment variables from .env file if it exists
set dotenv-load := true

# Use uv env manager by default (set RUN=" " to .env to use current active environment instead)
RUN := env("RUN", "uv run")

# Set the shell to bash
set shell := ["bash", "-c"]

# Default recipe (runs when just is called without arguments)
default: run

# Show available recipes
help:
    @just --list

# Run the streamlit web application
run:
    {{RUN}} streamlit run ovo/run_app.py --server.runOnSave=1

# Alias for running the application
app: run

# Open python console with OVO modules loaded
python:
    {{RUN}} python -i -c "from ovo import *; print(db.select_dataframe(Project, limit=10));"

# Open SQLite console
sqlite:
    #!/usr/bin/env bash
    set -ex
    DB_PATH=$({{RUN}} python -c "from ovo import config; print(config.db.url.removeprefix('sqlite://'))")
    sqlite3 "$DB_PATH"

build:
    rm -rf ./dist
    # Always use uv for building
    uv build
    ls -lh dist

test: unit-tests plugin-tests

tests: test

# Run unit tests including Streamlit unit tests
unit-tests tests="tests/unit_tests":
    {{RUN}} pytest {{tests}}

unit-test: unit-tests

# Run workflow tests (using full OVO logic including DB entries and processing logic)
integration-tests +tests="tests/integration_tests":
    {{RUN}} pytest -s {{tests}}

integration-test: integration-tests

# Run plugin tests (test plugin creation)
plugin-tests +tests="tests/plugin_tests":
    {{RUN}} pytest -s -v {{tests}}

plugin-test: plugin-tests

# Run pipeline tests (submit scheduler jobs and check results)
pipeline-tests +tests="ovo/pipelines":
    {{RUN}} pytest -s {{tests}}

pipeline-test: pipeline-tests

# Run web application to inspect unit test results (after executing just test)
test-app:
    #!/usr/bin/env bash
    export OVO_HOME=test-results/unit_tests
    export USER=test_user
    just app

# Run python console to inspect unit test results (after executing just test)
test-python:
    #!/usr/bin/env bash
    export OVO_HOME=test-results/unit_tests
    export USER=test_user
    {{RUN}} python -i -c "from ovo import *; print(db.select_dataframe(Project, limit=10));"

# Check linting and formatting with ruff
check: lint-check format-check

# Run linting check with ruff
lint-check:
    {{RUN}} ruff check .

# Fix linting issues with ruff
lint-fix:
    {{RUN}} ruff check --fix .

# Format code with ruff
format:
    {{RUN}} ruff format .

# Check if code is formatted correctly with ruff
format-check:
    {{RUN}} ruff format --check .

docs:
    cd docs; {{RUN}} make html

html-docs: docs
    open docs/build/html/index.html
