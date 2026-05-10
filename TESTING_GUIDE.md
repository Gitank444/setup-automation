# Testing Guide

## Quick Start

### Run All Tests
```bash
python run_tests.py
```

### Run Specific Test Type
```bash
python run_tests.py unit          # Unit tests only
python run_tests.py integration   # Integration tests only
python run_tests.py verbose       # Verbose output
```

### Debug Detection Issues
```bash
python debug_detection.py          # Full report
python debug_detection.py docker   # Debug specific tool
python debug_detection.py stacks   # Stack readiness
```

---

## Test Structure

```
tests/
├── __init__.py
├── unit/                    # Unit tests
│   ├── __init__.py
│   ├── test_checker.py      # Software checker tests
│   └── test_orchestrator.py # Orchestrator tests
└── integration/             # Integration tests
    ├── __init__.py
    └── test_setup_flow.py   # Full workflow tests
```

---

## Test Files

### 1. `tests/unit/test_checker.py`
Tests for software detection functions.

**What it tests:**
- ✅ System tool detection (installed/not installed)
- ✅ Python library detection
- ✅ Intelligent software checking

**Run it:**
```bash
python -m unittest tests.unit.test_checker -v
```

### 2. `tests/unit/test_orchestrator.py`
Tests for the main orchestrator.

**What it tests:**
- ✅ Stack display
- ✅ User input handling
- ✅ Valid/invalid choices

**Run it:**
```bash
python -m unittest tests.unit.test_orchestrator -v
```

### 3. `tests/integration/test_setup_flow.py`
Tests the complete setup workflow.

**What it tests:**
- ✅ Stack definitions exist
- ✅ Tool detection flow
- ✅ Installation workflow

**Run it:**
```bash
python -m unittest tests.integration.test_setup_flow -v
```

---

## Debug Script: `debug_detection.py`

### Purpose
Identify why tools are or aren't being detected.

### Features

1. **Full System Report**
   ```bash
   python debug_detection.py
   ```
   Shows:
   - All tools across all stacks
   - Which are detected
   - Which are missing
   - Detection percentage

2. **Stack Readiness**
   ```bash
   python debug_detection.py stacks
   ```
   Shows:
   - Each stack's status
   - Tools per stack
   - Missing tools

3. **Debug Specific Tool**
   ```bash
   python debug_detection.py docker
   ```
   Shows:
   - Basic vs Advanced detection
   - Tool info (command, type, flags)
   - All detection strategies
   - System info

4. **Debug Multiple Tools**
   ```bash
   python debug_detection.py docker vscode python node
   ```

---

## Test Runner: `run_tests.py`

### Purpose
Run all tests with optional filtering and verbosity.

### Options
```bash
python run_tests.py                 # All tests
python run_tests.py unit            # Unit tests only
python run_tests.py integration     # Integration tests only
python run_tests.py verbose         # Verbose output
python run_tests.py unit verbose    # Unit tests, verbose
```

### Output Example
```
Running all tests...

test_tool_command_fails (tests.unit.test_checker.TestCheckSystemTool) ... ok
test_tool_installed (tests.unit.test_checker.TestCheckSystemTool) ... ok
test_tool_not_installed (tests.unit.test_checker.TestCheckSystemTool) ... ok
test_library_installed (tests.unit.test_checker.TestCheckPythonLib) ... ok
test_library_not_installed (tests.unit.test_checker.TestCheckPythonLib) ... ok
test_check_system_tool_type (tests.unit.test_checker.TestCheckSoftware) ... ok
test_check_python_lib_type (tests.unit.test_checker.TestCheckSoftware) ... ok
test_display_stacks (tests.unit.test_orchestrator.TestSetupOrchestrator) ... ok
test_get_user_choice_invalid (tests.unit.test_orchestrator.TestSetupOrchestrator) ... ok
test_get_user_choice_valid (tests.unit.test_orchestrator.TestSetupOrchestrator) ... ok
test_stacks_are_defined (tests.integration.test_setup_flow.TestFullSetupFlow) ... ok
test_missing_tools_detection (tests.integration.test_setup_flow.TestFullSetupFlow) ... ok
test_installation_flow (tests.integration.test_setup_flow.TestFullSetupFlow) ... ok

Ran 13 tests in 0.234s

OK
```

---

## Advanced Detection Strategies

### 1. PATH Check
```python
detector.strategy_path_check("docker")  # Quick check if in PATH
```

### 2. Version Check
```python
detector.strategy_version_check("docker", ["--version", "-v"])
```

### 3. Known Paths
```python
detector.strategy_known_paths("docker.exe", [
    r"C:\Program Files\Docker\Docker"
])
```

### 4. Windows Registry (Windows only)
```python
detector.strategy_windows_registry("Docker")
```

### 5. Special Handlers
Built-in smart detection for:
- Docker
- VSCode
- Android Studio
- Unity
- Blender
- Ollama

---

## How to Add Tests

### Example: Test a New Detector

```python
# tests/unit/test_advanced_checker.py
import unittest
from unittest.mock import patch
from checkers import AdvancedDetector

class TestAdvancedDetector(unittest.TestCase):
    
    def setUp(self):
        self.detector = AdvancedDetector()
    
    @patch('os.path.exists')
    def test_detect_docker_from_path(self, mock_exists):
        """Test Docker detection from known path."""
        mock_exists.return_value = True
        result = self.detector.detect_docker()
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
```

### Example: Test a New Installer

```python
# tests/unit/test_installers.py
import unittest
from unittest.mock import patch, MagicMock
from installers import WingetInstaller

class TestWingetInstaller(unittest.TestCase):
    
    def setUp(self):
        self.installer = WingetInstaller()
    
    @patch('installers.winget_installer.subprocess.run')
    def test_install_success(self, mock_run):
        """Test successful installation."""
        mock_run.return_value = MagicMock(returncode=0)
        result = self.installer.install("Git.Git")
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
```

---

## Troubleshooting Tests

### Test Fails: "ModuleNotFoundError"

**Solution:**
```bash
# Make sure you're in project root
cd c:\Users\Gitank\Projects\setup-automation

# Run tests
python run_tests.py
```

### Test Fails: "Subprocess Errors"

**Solution:**
Tests use mocking, so they should work without actual tools installed. If you get subprocess errors:

```bash
# Ensure mock is imported correctly in test file
from unittest.mock import patch, MagicMock

# Use @patch decorator correctly
@patch('module.function')
def test_something(self, mock_func):
    pass
```

### Test Fails: "Import Errors"

**Solution:**
```bash
# Run from project root directory
cd setup-automation

# Ensure __init__.py files exist in all packages
# tests/, tests/unit/, tests/integration/

# Run with explicit path
python -m unittest discover -s tests -p "test_*.py" -v
```

---

## Continuous Testing

### Run Tests After Each Change

```bash
# After modifying code
python run_tests.py verbose

# If any test fails, fix the issue
# Then run again
```

### Run Specific Test

```bash
# Run only one test class
python -m unittest tests.unit.test_checker.TestCheckSystemTool

# Run only one test method
python -m unittest tests.unit.test_checker.TestCheckSystemTool.test_tool_installed
```

---

## Performance Testing

### Check Detection Speed

```python
import time
from checkers import check_software_advanced

tools = ["docker", "vscode", "python", "node", "git"]

start = time.time()
for tool in tools:
    check_software_advanced(tool)
end = time.time()

print(f"Checked {len(tools)} tools in {end-start:.2f}s")
```

### Expected: ~0.5-1.0 seconds for 5 tools

---

## Coverage Analysis

```bash
# Install coverage
pip install coverage

# Run tests with coverage
coverage run -m unittest discover

# Generate report
coverage report

# Generate HTML report
coverage html
# Open htmlcov/index.html in browser
```

---

## Best Practices

1. **Write tests as you code** - Don't wait until the end
2. **Test edge cases** - Not just the happy path
3. **Use mocking** - Don't depend on actual system state
4. **Keep tests isolated** - No test should affect another
5. **Use descriptive names** - `test_docker_not_detected` not `test_1`
6. **Run tests frequently** - Before each commit

---

## Debugging Tests

### Add Debug Output

```python
def test_something(self):
    print(f"Debug: {variable}")  # Will show if test fails with -v
    self.assertTrue(condition)
```

### Use pdb (Python Debugger)

```python
import pdb

def test_something(self):
    pdb.set_trace()  # Execution pauses here
    result = function_to_test()
    self.assertTrue(result)

# Run test, then use debugger commands:
# n - next line
# s - step into function
# c - continue
# p variable - print variable
# l - list current code
```

---

## CI/CD Integration

Example GitHub Actions workflow:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - run: pip install -r requirements.txt
      - run: python run_tests.py verbose
```

---

## Test Results Summary

After running tests, you should see:

✅ All tests pass  
✅ No errors or warnings  
✅ Detection works correctly  
✅ Orchestrator works correctly  
✅ Full workflow works correctly  

If any test fails:
1. Run `python debug_detection.py` to check system state
2. Check [DETECTION_ISSUES.md](DETECTION_ISSUES.md) for solutions
3. Review test output for specific error
4. Debug specific tool with: `python debug_detection.py <tool_name>`

---

## Getting Help

1. **Check test output** - Clear error messages
2. **Run debug script** - `python debug_detection.py`
3. **Check DETECTION_ISSUES.md** - Common issues and fixes
4. **Review test files** - See what's being tested
5. **Check logs** - System tool availability

---

## Next Steps

1. ✅ Run: `python run_tests.py`
2. ✅ Verify: All tests pass
3. ✅ Debug: `python debug_detection.py`
4. ✅ Fix: Any detection issues (see DETECTION_ISSUES.md)
5. ✅ Test: `python main.py` - Full setup workflow
