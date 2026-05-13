# Setup Automation - Comprehensive Bug Report

## Summary
Found **10 critical bugs** causing detection failures, partial installations, and broken retry logic. Most relate to Python library detection and PATH environment handling.

---

## Bug #1: Python Libraries Incorrectly Configured ❌
**Severity**: CRITICAL | **Affected**: fastapi, numpy, pandas, and all python_lib tools

### Problem
FastAPI and other Python libraries show as "NOT FOUND" even when installed via pip.

### Root Cause
- FastAPI.yaml defines `command: fastapi` which doesn't exist as an executable
- The system tries to run `fastapi --version` instead of importing the library
- Python libraries need import checks, not command execution

### Evidence
```yaml
# registry/tools/fastapi.yaml (WRONG)
name: fastapi
command: fastapi          # ← This executable doesn't exist!
version_flags:
  - --version
type: python_lib          # ← Says python_lib but uses command
```

### Impact
- ❌ FastAPI always shows as MISSING
- ❌ NumPy shows as NOT FOUND
- ❌ Pandas detection fails
- ❌ All Python libraries fail

### Fix Required
Remove `command` field from python_lib entries and ensure detection uses import logic only.

---

## Bug #2: Partial Installation Not Auto-Repaired ❌
**Severity**: HIGH | **Affected**: Any tool with binary not in PATH

### Problem
When a tool is detected as PARTIAL (binary exists but not in PATH), the system only asks the user to fix it manually.

### Root Cause
- `_handle_repairs()` only prompts user for confirmation
- No automatic repair or reinstall for PARTIAL status
- System detects the problem but can't fix it

### Evidence
```python
# orchestrator/setup_orchestrator.py line ~120
def _handle_repairs(self, repair_tools):
    # Only prompts user, doesn't auto-repair
    for tool, status in repair_tools:
        answer = input(f"\nDo you want to fix {tool}? (y/n): ")
        if answer.strip().lower() != 'y':
            continue
        # ... manual repair only
```

### Impact
- ⚠️ User must manually intervene for PARTIAL tools
- ⚠️ Installation incomplete
- ⚠️ No automatic PATH repair

### Fix Required
Add automatic repair logic that reinstalls tools when PARTIAL is detected.

---

## Bug #3: No PATH Reload After Installation ❌
**Severity**: HIGH | **Affected**: All system-level installs (winget, chocolatey)

### Problem
After installing a tool via winget, Python doesn't reload the PATH environment. Verification fails because the tool is not yet visible to subprocess calls.

### Root Cause
- When winget installs a tool, it updates Windows PATH
- Python's `os.environ['PATH']` still has the old value
- Subprocess calls use the stale PATH
- `verify_installation()` can't find the newly installed tool

### Evidence
```
Timeline:
1. User installs Docker via winget ✅
2. Docker executable added to Windows PATH ✅
3. System re-checks for docker in subprocess
4. Python's os.environ['PATH'] hasn't been updated ❌
5. Subprocess can't find docker ❌
6. System reports "docker NOT FOUND" ❌
```

### Impact
- ❌ All system installs appear to fail
- ❌ Re-verification returns MISSING even though installed
- ❌ User thinks installation failed

### Fix Required
Add explicit PATH reload after system-level installations using `os.environ.clear()` and `subprocess.check_output()` to refresh.

---

## Bug #4: Broken Detection for Tools Without Version Output ❌
**Severity**: MEDIUM | **Affected**: Some system tools that don't support --version

### Problem
Tools are marked as BROKEN if they exist but don't output version information.

### Root Cause
```python
# advanced_checker.py line ~415
binary_found = len(all_locations_found) > 0
if binary_found and not primary_version and tool != "vscode":
    broken = True  # ← Marks as broken if no version found!
```

- Many tools don't support version flags
- System assumes broken if version can't be extracted
- VSCode is hardcoded exception but others aren't

### Impact
- ⚠️ Valid tools marked as BROKEN
- ⚠️ User sees false error messages
- ⚠️ Causes unnecessary reinstall attempts

### Fix Required
Only mark tool as BROKEN if:
1. Binary found AND
2. Binary cannot execute at all (return code != 0)

Not if version just unavailable.

---

## Bug #5: VSCode Detection Incomplete ❌
**Severity**: MEDIUM | **Affected**: VSCode detection

### Problem
VSCode shows as BROKEN even when installed because the wrapper detection logic is incomplete.

### Root Cause
- `_find_vscode_cli_wrapper()` tries to find `code.cmd` but may fail
- Tool requires version to not be marked broken
- VSCode GUI might not support version output via wrapper

### Evidence
```python
# advanced_checker.py line ~185
def _find_vscode_cli_wrapper(self):
    # Tries multiple approaches but may all fail
    for wrapper in ("code.cmd", "code.bat"):
        wrapper_path = shutil.which(wrapper)
        if wrapper_path:
            return wrapper_path
    # ... falls through and returns None
```

### Impact
- ⚠️ VSCode shows as BROKEN
- ⚠️ False error about installation

### Fix Required
Remove version requirement for VSCode or improve wrapper detection.

---

## Bug #6: Python Library Validation in check_software() ❌
**Severity**: CRITICAL | **Affected**: All python_lib type tools

### Problem
The basic `check_software()` function in software_checker.py doesn't handle python_lib type correctly.

### Root Cause
```python
# software_checker.py line ~65
def check_software(tool):
    tool_type = TOOL_TYPE.get(tool)
    
    if tool_type == "python_lib":
        return check_python_lib(tool)  # ← Calls check_python_lib
    
    # But check_system_tool still called as fallback!
    cmd = COMMAND_MAP.get(tool, tool)
    return check_system_tool(cmd)  # ← Tries to run command
```

The function returns early for python_lib but still tries system command.

### Impact
- ❌ Python libraries always fail detection
- ❌ FastAPI, NumPy, Pandas all show as MISSING

### Fix Required
Ensure python_lib check is the only path and doesn't fall through to system command.

---

## Bug #7: Retry Logic Not Working ❌
**Severity**: HIGH | **Affected**: Installation retry mechanism

### Problem
When installation fails, there's no automatic retry with different strategies or after environment refresh.

### Root Cause
- `verify_installation()` only retries version check
- Doesn't retry actual installation
- No exponential backoff or different strategy attempt
- Winget has internal retry but only 2 attempts (default)

### Impact
- ⚠️ First failure means installation failed
- ⚠️ No alternative methods attempted
- ⚠️ User intervention required

### Fix Required
Add retry loop in `install_tool()` that:
1. Retries same installer
2. Tries alternative installers
3. Refreshes environment between retries

---

## Bug #8: Version Flag Configuration Missing ❌
**Severity**: MEDIUM | **Affected**: Many tools

### Problem
Some tools don't have VERSION_FLAG defined, so system uses only `--version` which might not work.

### Root Cause
VERSION_FLAG loading:
```python
VERSION_FLAG = {
    tool: config.get("version_flags", ["--version"])  # ← Defaults to ["--version"]
    for tool, config in TOOL_CONFIGS.items()
}
```

Many tools need `-v` or `--help` or other flags.

### Impact
- ⚠️ Valid tools marked as broken
- ⚠️ Detection failures for tools with non-standard version flags

### Fix Required
Add comprehensive VERSION_FLAG entries for all tools.

---

## Bug #9: FastAPI Configuration Error ❌
**Severity**: CRITICAL | **Affected**: FastAPI detection

### Problem
FastAPI.yaml is misconfigured for a Python library.

### Current Config
```yaml
name: fastapi
command: fastapi          # ← WRONG: no such command
version_flags:
  - --version
type: python_lib
detection:
  executable_names:
    - fastapi             # ← WRONG: not an executable
    - fastapi.exe
```

### Fix Required
Change to:
```yaml
name: fastapi
# NO command field for python_lib
type: python_lib
# detection section not needed for python_lib
```

---

## Bug #10: Installation Status Not Re-verified with Fresh Environment ❌
**Severity**: HIGH | **Affected**: Post-installation verification

### Problem
After installation, `verify_installation()` uses cached environment variables, so fresh installs aren't detected.

### Root Cause
```python
# orchestrator/setup_orchestrator.py line ~560
def verify_installation(self, tool, retries=5):
    for attempt in range(retries):
        signal = check_software_advanced(tool)  # ← Uses current subprocess env
        # subprocess still uses stale PATH from Python
```

No environment refresh between detection and subprocess calls.

### Impact
- ❌ Tool installed but shows as missing
- ❌ False failures
- ❌ User thinks installation didn't work

### Fix Required
Add explicit environment reload in subprocess calls.

---

## Testing Recommendations

### Test Case 1: FastAPI Detection
```bash
# Should find fastapi even though no 'fastapi' command exists
python -c "from checkers import check_software_advanced; print(check_software_advanced('fastapi'))"
```

### Test Case 2: Partial Installation Handling
```bash
# Simulate partial install by removing from PATH, verify auto-repair
# Expected: Should automatically repair without user input
```

### Test Case 3: PATH Refresh After Install
```bash
# Install new tool, immediately verify
# Expected: Should be detected within 5 seconds
```

### Test Case 4: Multiple Retry Strategies
```bash
# Install with invalid winget ID
# Expected: Should fallback to other installers or search methods
```

---

## Priority Fixes

1. **CRITICAL**: Fix Python library detection (Bugs #1, #6, #9)
2. **CRITICAL**: Add PATH reload after installation (Bug #3)
3. **HIGH**: Implement auto-repair for PARTIAL status (Bug #2)
4. **HIGH**: Improve retry logic (Bug #7)
5. **MEDIUM**: Fix broken detection logic (Bug #4)
6. **MEDIUM**: Complete VSCode detection (Bug #5)
7. **MEDIUM**: Add missing VERSION_FLAG entries (Bug #8)
8. **MEDIUM**: Re-verify with fresh environment (Bug #10)
