# Quick Reference Guide

## Running the Application
```bash
python main.py
```

## Project Structure at a Glance

```
📁 setup-automation/
├── 📄 main.py                    ← Start here (20 lines!)
├── 📄 ARCHITECTURE.md            ← Detailed design docs
├── 📄 QUICK_REFERENCE.md         ← This file
│
├── 📁 config/                    🔧 All settings here
│   ├── constants.py              Tool mappings
│   └── stacks.py                 Dev stacks
│
├── 📁 checkers/                  ✅ Detect installed tools
│   └── software_checker.py       
│
├── 📁 installers/                📦 Installation methods
│   ├── base_installer.py         Base class
│   ├── winget_installer.py       Windows Package Manager
│   ├── pip_installer.py          Python packages
│   ├── npm_installer.py          Node packages
│   ├── conda_installer.py        Anaconda packages
│   └── chocolatey_installer.py   Chocolatey packages
│
├── 📁 orchestrator/              🎯 Main logic
│   └── setup_orchestrator.py     Coordinates everything
│
└── 📁 utils/                     🛠️ Helper functions
    └── helpers.py               Display helpers
```

## Line Count Comparison

| Component | Old main.py | New Structure |
|-----------|-----------|---------------|
| **Total** | 600+ lines | ~300 lines total |
| **Main** | 600 lines | **20 lines** ⬇️ |
| **Entry point readability** | ❌ Confusing | ✅ Crystal clear |

## How It Works

```
User runs: python main.py
    ↓
SetupOrchestrator.run()
    ├→ Display available stacks
    ├→ Get user choice (1-13 options)
    ├→ Check which tools are missing
    ├→ Ask for confirmation
    ├→ Install each tool:
    │   ├→ Detect tool type (system/python/npm)
    │   ├→ Select best installer
    │   ├→ Execute installation
    │   └→ Verify success
    └→ Done!
```

## Adding a New Development Stack

**File**: `config/stacks.py`

```python
STACKS = {
    ...
    "your_stack": ["tool1", "tool2", "tool3"],
}
```

That's it! The system will automatically:
- Display it in the menu
- Check for those tools
- Install missing ones using optimal methods

## Adding a New Package Manager

**Example**: Adding MacOS Brew Support

1. Create `installers/brew_installer.py`:
```python
from .base_installer import BaseInstaller

class BrewInstaller(BaseInstaller):
    def is_available(self):
        # Check if brew is available
        pass
    
    def install(self, package):
        # Install using brew
        pass
```

2. Register in `orchestrator/setup_orchestrator.py`:
```python
self.installers = {
    'winget': WingetInstaller(),
    'pip': PipInstaller(),
    'brew': BrewInstaller(),  # ← Add this
    ...
}
```

That's all! No other changes needed.

## Available Development Stacks

| Stack | Tools |
|-------|-------|
| **webdev** | Node, Git, VSCode |
| **frontend** | Node, Git, VSCode, React, TypeScript |
| **backend_dev** | Python, Postman, Docker, Git, VSCode |
| **ml_dev** | Python, Pip, Ollama, Docker |
| **backend_security** | Python, FastAPI, Postman, OpenSSL |
| **data_science** | Python, Anaconda, Jupyter, Pandas, NumPy |
| **cloud_engineer** | Terraform, AWS CLI, Docker, kubectl |
| **devops** | Docker, kubectl, Terraform, Git, VSCode |
| **android_dev** | Java, Android Studio, Kotlin |
| **python_dev** | Python, Git, VSCode, Pip |
| **game_dev** | Unity, Blender, Git, VSCode |
| **rust_dev** | Rust, Cargo, Git, VSCode |
| **nodejs_dev** | Node, Git, VSCode, NPM, Yarn |

## Key Files to Modify

- **Adding tools**: Update `config/constants.py` (COMMAND_MAP, INSTALL_MAP, etc.)
- **Adding stacks**: Update `config/stacks.py` (STACKS dict)
- **Adding installers**: Create new class in `installers/` + register in orchestrator
- **Changing behavior**: Edit `orchestrator/setup_orchestrator.py`

## Testing

```bash
# Check syntax
python -m py_compile main.py

# Run the app
python main.py
```

---

**Before**: 600 lines of spaghetti code 🍝  
**After**: Clean, modular architecture 🏗️
