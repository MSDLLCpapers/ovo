# OVO Tests

This directory contains tests for the OVO project.

Each subfolder should be executed separately, either through `pytest tests/...` or through `just ...-test`.

## Integration tests

Tests that use your real local OVO HOME directory and configuration
to run Nextflow end to end pipelines and store them in the database.

Requires all reference files to be initialized in your OVO HOME.

- Folder: [tests/integration_tests](./integration_tests)
- Command: `pytest tests/integration_tests`
- Through Just: `just integration-tests`

## Plugin tests

Tests that use a temporary `uv` environment to create and install new OVO plugins 
and test their functionality.

- Folder: [tests/plugin_tests](./plugin_tests)
- Command: `pytest tests/plugin_tests`
- Through Just: `just plugin-tests`

## Unit tests

Tests that use mocks to test individual functions and classes in isolation,
without running any pipelines or creating any additional environments.

- Folder: [tests/unit_tests](./unit_tests)
- Command: `pytest tests/unit_tests`
- Through Just: `just unit-tests`
