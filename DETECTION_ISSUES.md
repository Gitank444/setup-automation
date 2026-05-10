# Detection Issues & Solutions

## Problems Identified

### 1. Docker Not Detected ❌

**Why it's happening:**
- Docker command is not in `PATH` even though Docker Desktop is installed
- The `docker.exe` might be in a directory not added to PATH
- Docker Desktop service might not be running
- On first install, system needs restart for PATH to update

**Solutions:**

**Quick Fix (Windows):**
```powershell
# Restart Windows (most reliable)
Restart-Computer

# OR manually add Docker to PATH:
# 1. Find Docker installation: Usually C:\Program Files\Docker\Docker\resources\bin
# 2. Add to PATH:
$env:Path += ";C:\Program Files\Docker\Docker\resources\bin"
```

**Docker Desktop Specific:**
- Open Docker Desktop settings
- Ensure "Add Docker to PATH" is enabled
- Restart Docker Desktop
- Restart your terminal/PowerShell

**Verify Docker is detected:**
```bash
python -c "from checkers import check_software_advanced; print(check_software_advanced('docker'))"
```

---

### 2. VSCode Not Detected ❌

**Why it's happening:**
- The `code` command requires shell command installation
- VSCode is installed but shell command is not registered
- `code` command not in PATH

**Solutions:**

**Manual Installation (VSCode):**
1. Open VSCode
2. Press `Ctrl + Shift + P` (or `Cmd + Shift + P` on macOS)
3. Type: "Shell Command: Install 'code' command in PATH"
4. Select it
5. Restart your terminal

**Automated (PowerShell as Admin):**
```powershell
# For VSCode
$codePath = "C:\Program Files\Microsoft VS Code\bin\code"
if (Test-Path $codePath) {
    [Environment]::SetEnvironmentVariable(
        "Path",
        $env:Path + ";C:\Program Files\Microsoft VS Code\bin",
        "User"
    )
    Write-Host "VSCode added to PATH"
}
```

**Verify VSCode is detected:**
```bash
python -c "from checkers import check_software_advanced; print(check_software_advanced('vscode'))"
```

---

### 3. Android Studio Not Detected ❌

**Why it's happening:**
- `studio64.exe` not in PATH
- Installation in non-standard location
- Not installed or partially installed

**Solutions:**

**Add to PATH (Windows):**
```powershell
# Find Android Studio bin directory
$androidStudio = "C:\Program Files\Android\Android Studio\bin"
if (Test-Path $androidStudio) {
    $env:Path += ";$androidStudio"
    echo "Android Studio added to PATH"
}
```

**Or install from scratch:**
- Use our setup automation (when other issues are fixed)
- Or install from [https://developer.android.com/studio](https://developer.android.com/studio)

---

### 4. Other Tools Not Detected

**Common Reasons:**
1. **Not in PATH** - Most common issue
2. **Installation incomplete** - Needs restart
3. **Wrong command name** - Tool might use different command
4. **Environment variables needed** - Tool requires custom env var
5. **Special configuration** - Tool needs setup after installation

**Debug Tool Detection:**

```python
from checkers import AdvancedDetector

detector = AdvancedDetector()

# Check specific strategies for a tool
tool = "docker"  # Change this

print(f"✓ In PATH: {detector.strategy_path_check('docker')}")
print(f"✓ Version Check: {detector.strategy_version_check('docker', ['--version'])}")
print(f"✓ Windows Registry: {detector.strategy_windows_registry('Docker')}")
print(f"✓ Special Detector: {detector.detect_docker()}")
```

---

## New Advanced Detection System

### How It Works

The new `AdvancedDetector` uses **multiple strategies** to find installed tools:

```
Strategy 1: Check if command is in PATH
    ↓ (if not found)
Strategy 2: Try to get version (multiple flags: --version, -v, --help)
    ↓ (if not found)
Strategy 3: Check known installation directories
    ↓ (if not found)
Strategy 4: Windows Registry check (Windows only)
    ↓ (if not found)
Strategy 5: Special handlers for known problematic tools
    ↓
Result: FOUND or NOT FOUND
```

### Special Handlers

These tools have **smart detection** to handle PATH issues:

```python
Special detectors for:
- docker      (checks Docker Desktop paths + registry)
- vscode      (checks VS Code directories + registry)
- android-studio (checks Android Studio directories + registry)
- unity       (checks Unity Hub paths + registry)
- blender     (checks Blender installation)
- ollama      (checks Ollama local paths)
```

---

## Testing Detection

### Run Tests

```bash
# Unit tests for checker
python -m pytest tests/unit/test_checker.py -v

# Or with unittest
python -m unittest tests.unit.test_checker -v

# Integration tests
python -m unittest tests.integration.test_setup_flow -v
```

### Manual Testing

```python
# Test individual tool detection
from checkers import check_software_advanced

tools_to_test = [
    "docker",
    "vscode",
    "python",
    "node",
    "git",
    "android-studio"
]

for tool in tools_to_test:
    result = check_software_advanced(tool)
    status = "✅ FOUND" if result else "❌ NOT FOUND"
    print(f"{tool}: {status}")
```

### Advanced Debug

```python
from checkers import AdvancedDetector

detector = AdvancedDetector()

# Get detailed detection info
print(f"OS: {detector.is_windows=}, {detector.is_macos=}, {detector.is_linux=}")

# Test Docker specifically
print(f"\nDocker Detection:")
print(f"  - In PATH: {detector.strategy_path_check('docker')}")
print(f"  - Known paths: {detector.strategy_known_paths('docker.exe', detector.get_common_install_paths())}")
print(f"  - Registry: {detector.strategy_windows_registry('Docker')}")
print(f"  - Final result: {detector.detect_docker()}")
```

---

## Windows Registry Check

On Windows, the system automatically checks the registry for:
- Docker
- Visual Studio Code
- Android Studio
- Unity
- Blender

This is **very reliable** even if commands aren't in PATH.

---

## Environment Setup After Installation

Some tools need **setup after installation**:

### Docker
```bash
# After installation, restart Docker Desktop
# Then verify:
docker --version

# If still not found:
# 1. Restart Windows
# 2. Or add to PATH manually
```

### VSCode
```bash
# After installation, use the "Install shell command" option
# Then verify:
code --version

# If still not found:
# Run as Administrator and add to PATH
```

### Node.js / npm / yarn
```bash
# After installation:
node --version
npm --version
yarn --version

# If not found, usually just needs restart
```

### Python / pip
```bash
# After installation:
python --version
pip --version

# Usually detected automatically
```

---

## Common Fixes

### Fix 1: Restart (Most Effective)
```powershell
# Restart Windows - most reliable fix for PATH issues
Restart-Computer
```

### Fix 2: Refresh PATH (without restart)
```powershell
# Reload PATH in current session
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
```

### Fix 3: Manual PATH Addition
```powershell
# Add custom path
$tool_path = "C:\Path\To\Tool\Bin"
$env:Path += ";$tool_path"

# Verify
echo $env:Path
```

### Fix 4: Verify Installation
```powershell
# Check if installation actually exists
Test-Path "C:\Program Files\Docker\Docker"

# List available commands in a directory
Get-ChildItem "C:\Program Files\Docker\Docker\resources\bin"
```

---

## Troubleshooting Guide

| Problem | Cause | Solution |
|---------|-------|----------|
| Tool shows as missing but installed | Not in PATH | Add to PATH or restart |
| PATH addition doesn't work | Terminal not reloaded | Restart PowerShell/cmd |
| Can't find installation directory | Custom location | Manual PATH addition |
| Registry check fails | Windows registry issue | Try version command |
| Version command fails | Command format wrong | Check VERSION_FLAG in config |

---

## Using the Advanced Detector

### In Your Code

```python
# Instead of basic check
from checkers import check_software  # ❌ Limited

# Use advanced detection  
from checkers import check_software_advanced  # ✅ Comprehensive

# Example
if check_software_advanced("docker"):
    print("Docker is ready!")
else:
    print("Docker needs installation")
```

### Get More Details

```python
from checkers import AdvancedDetector

detector = AdvancedDetector()

# Check what actually worked
if detector.detect_docker():
    print("Docker detected using smart detection!")
    
# Check each strategy separately
detector.strategy_path_check("docker")  # PATH check
detector.strategy_version_check("docker")  # Version check
detector.strategy_windows_registry("Docker")  # Registry check
```

---

## Next Steps

1. **Run setup.py again** with new advanced detection - it should find more tools now
2. **Verify detection** works: `python -m unittest tests.unit.test_checker -v`
3. **Debug specific tools** using the troubleshooting guide above
4. **Report results** of which tools are now correctly detected

---

## Prevention for Future Issues

### When Installing New Tools

1. **Use winget** - Automatically adds to PATH
```powershell
winget install --id Docker.DockerDesktop
```

2. **After manual installation** - Always restart
3. **Verify detection** - Test with our detector
4. **Report bugs** - Help us improve detection

---

## Advanced Customization

You can extend the AdvancedDetector for custom tools:

```python
class CustomDetector(AdvancedDetector):
    def detect_custom_tool(self):
        """Add custom detection logic."""
        # Your logic here
        pass
    
    def check_software(self, tool):
        if tool == "custom_tool":
            return self.detect_custom_tool()
        return super().check_software(tool)
```

---

**For more help**: Check test files or run detection debug script above.
