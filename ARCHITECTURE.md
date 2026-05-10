# Setup Automation System - Project Structure

## Overview
A clean, modular system for automating developer environment setup with multiple installation methods and predefined development stacks.

## Directory Structure

```
setup-automation/
├── main.py                    # Entry point (clean and simple)
├── .gitignore                 # Python gitignore template
│
├── config/                    # Configuration & constants
│   ├── __init__.py
│   ├── constants.py           # Global mappings and configurations
│   └── stacks.py              # Development stack definitions
│
├── checkers/                  # Software detection
│   ├── __init__.py
│   └── software_checker.py    # Functions to verify tool installation
│
├── installers/                # Installation methods (modular)
│   ├── __init__.py
│   ├── base_installer.py      # Abstract base class for all installers
│   ├── winget_installer.py    # Windows Package Manager
│   ├── pip_installer.py       # Python Package Manager
│   ├── npm_installer.py       # Node Package Manager
│   ├── conda_installer.py     # Conda Package Manager
│   └── chocolatey_installer.py # Chocolatey Package Manager
│
├── orchestrator/              # Main logic
│   ├── __init__.py
│   └── setup_orchestrator.py  # Orchestrates entire setup process
│
└── utils/                     # Utility functions
    ├── __init__.py
    └── helpers.py             # Helper functions for display
```

## Module Breakdown

### 1. **config/** - Configuration Management
- **constants.py**: Contains all mappings (commands, flags, tool types, installers)
- **stacks.py**: Predefined development stacks for different roles

### 2. **checkers/** - Software Verification
- **software_checker.py**: Functions to detect if tools are installed
- Supports system tools, Python libraries, and npm packages

### 3. **installers/** - Pluggable Installation System
Each installer is a separate class inheriting from `BaseInstaller`:
- **WingetInstaller**: Windows Package Manager (default)
- **PipInstaller**: Python packages
- **NpmInstaller**: Node.js packages
- **CondaInstaller**: Anaconda packages
- **ChocolateyInstaller**: Chocolatey packages

Easily extend by creating new installer classes!

### 4. **orchestrator/** - Main Orchestration
- **SetupOrchestrator**: Coordinates the entire workflow
  - Displays available stacks
  - Detects missing tools
  - Intelligently selects installation method
  - Verifies installation success

### 5. **utils/** - Helper Utilities
- Formatting functions for consistent output
- Reusable helper functions

## Usage

```bash
python main.py
```

The orchestrator will:
1. Display available development stacks
2. Ask you to select your stack
3. Check which tools are already installed
4. Propose installation of missing tools
5. Use the best installer for each tool
6. Verify successful installation

## Development Stacks

- **webdev** - Node, Git, VSCode
- **frontend** - Node, Git, VSCode, React, TypeScript
- **backend_dev** - Python, Postman, Docker, Git, VSCode
- **ml_dev** - Python, Pip, Ollama, Docker
- **data_science** - Python, Anaconda, Jupyter, Pandas, NumPy
- **cloud_engineer** - Terraform, AWS CLI, Docker, kubectl
- **devops** - Docker, kubectl, Terraform, Git, VSCode
- **android_dev** - Java, Android Studio, Kotlin
- **python_dev** - Python, Git, VSCode, Pip
- **game_dev** - Unity, Blender, Git, VSCode
- **rust_dev** - Rust, Cargo, Git, VSCode
- **nodejs_dev** - Node, Git, VSCode, NPM, Yarn

## Design Principles

✅ **Modularity** - Each component has a single responsibility  
✅ **Extensibility** - Easy to add new installers or stacks  
✅ **Clean Code** - Well-organized, documented, and readable  
✅ **Separation of Concerns** - Config, logic, utilities are isolated  
✅ **Object-Oriented** - Installer classes with common interface  

## Adding New Stacks

Edit `config/stacks.py`:
```python
STACKS = {
    "my_stack": ["tool1", "tool2", "tool3"],
}
```

## Adding New Installers

1. Create a new file in `installers/` 
2. Inherit from `BaseInstaller`
3. Implement `install()` and `is_available()` methods
4. Register in `orchestrator/setup_orchestrator.py`

## Extending for Other OSes

The architecture is OS-agnostic. To support macOS/Linux:
1. Create `MacOSInstaller`, `LinuxInstaller` classes
2. Update installer strategy in `config/constants.py`
3. The rest of the code remains unchanged!

---

**Before**: 600+ lines in a single file  
**After**: Clean, modular architecture that's easy to understand and maintain
