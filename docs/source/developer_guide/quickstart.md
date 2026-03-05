# Developer Quickstart

This page provides instructions for setting up a local development environment 
for OVO and contributing to the [OVO repository](https://github.com/MSDLLCpapers/ovo).

For instructions on how to develop a separate plugin for OVO, please refer to the [plugin development guide](plugin_development.md).

## 1. Clone the OVO repository

Clone the OVO repository from GitHub:

```
# Clone the repository
git clone https://github.com/MSDLLCpapers/ovo
# Navigate into the cloned directory
cd ovo
```

## 2. Install OVO for development

### Using uv

First, if not already installed, install the `uv` package manager 
and `rust-just` command runner into your default Python environment:

```bash
pip install uv rust-just
```

Initialize the `.venv` directory with `uv`:

```bash
uv sync
```

### Using conda

```bash
# Create and activate conda environment
conda create -n ovo-dev python=3.13
conda activate ovo-dev

# Install OVO with pip in editable mode
pip install -e .

# Save instructions to .env file to avoid using uv
echo 'RUN=" "' >> .env
```

## 3. Development commands

Run Streamlit app with live reload:
```
just run
# or using ovo cli
ovo app --server.runOnSave=1
```

Run unit tests:
```
just test
# or using pytest directly 
pytest tests/unit_tests
```

Run full workflow tests (using the default scheduler from your local OVO config):
```
just integration-test
# or using pytest directly (-s to print detailed output)
pytest -s tests/integration_tests
```

Run Ruff formatter:
```
just format
# or using ruff directly
ruff format .
```

Run Ruff linter (optional):
```
just lint-check
# or using ruff directly
ruff check .
```

## 4. Contribute your first issue and pull request

Before you start working on a feature or bug fix, please [create an issue](https://github.com/MSDLLCpapers/ovo/issues)
describing your proposed changes. This helps us track work and coordinate contributions.

To contribute a separate plugin, please refer to the [plugin development guide](plugin_development.md).
