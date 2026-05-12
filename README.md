# Setup Automation

Automates developer environment setup on Windows by detecting installed tools, classifying their status, and applying the best available installation method.

## What it does

- Detects whether required tools are installed
- Reports tool status including version and PATH availability
- Classifies problems as `MISSING`, `PARTIAL`, `OUTDATED`, `BROKEN`, or `CONFLICT`
- Provides actionable advice for missing or unhealthy tools
- Installs or repairs tools using `winget`, `pip`, `npm`, `conda`, or `chocolatey`

## Demo

> Demo placeholder: run the setup flow locally with the test harness.

## How to run

1. Install dependencies if required.
2. Run the orchestrator:

```bash
python main.py
```

3. Run tests:

```bash
python run_tests.py
python run_tests.py unit
python run_tests.py integration
python run_tests.py verbose
```

## How to add a new stack

1. Update `config/stacks.py` with a new stack entry.
2. Add any new tool metadata to `config/constants.py`:
   - `COMMAND_MAP` to map tool names to executables
   - `VERSION_FLAG` to define version checks
   - `INSTALL_MAP` to define package IDs for winget
   - `TOOL_TYPE` to classify system tools, Python libraries, or npm packages
3. Add or update detection logic in `checkers/advanced_checker.py` if the tool requires custom heuristics.
4. Add tests under `tests/unit` or `tests/integration`.

## Architecture

- `checkers/`: Detects installed software and extracts version/path evidence
- `agents/`: Contains resolver logic and guidance for broken or missing tools
- `installers/`: Wraps package managers and installation commands
- `orchestrator/`: Coordinates selection, detection, installation, and verification
- `config/`: Stores platform mappings, version flags, and install strategies
- `tests/`: Unit and integration coverage for the tool detection and installation flow
