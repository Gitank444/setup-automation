"""Advanced software detection with multiple strategies."""
import re
import subprocess
import sys
import os
import shutil
from config import COMMAND_MAP, VERSION_FLAG, TOOL_TYPE, DETECTION_RULES
from models import ToolSignal, LocationVersion

class AdvancedDetector:
    """
    Advanced software detection with multiple fallback strategies.
    
    Strategies:
    1. Command in PATH (standard)
    2. Common installation directories
    3. Windows Registry (Windows only)
    4. Environment variables
    5. Application-specific checks
    """
    
    def __init__(self):
        """Initialize the detector."""
        self.is_windows = sys.platform == "win32"
        self.is_macos = sys.platform == "darwin"
        self.is_linux = sys.platform == "linux"
    
    def strategy_path_check(self, cmd):
        """
        Strategy 1: Check if command is in PATH.
        
        Args:
            cmd (str): Command name
            
        Returns:
            str|None: Resolved executable path if found, otherwise None
        """
        return shutil.which(cmd)
    
    def strategy_version_extract(self, cmd, flags=None):
        """
        Strategy 2: Extract version string from the target tool.
        
        Args:
            cmd (str): Command name
            flags (list): Version flags to try
            
        Returns:
            str|None: Extracted version string, or None if unavailable
        """
        if flags is None:
            flags = ["--version", "-v", "--help"]
        elif isinstance(flags, str):
            flags = [flags]

        for flag in flags:
            try:
                result = subprocess.run(
                    [cmd, flag],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                output = (result.stdout or "") + (result.stderr or "")
                if output.strip():
                    version = self._extract_version(output)
                    if version:
                        return version
            except Exception:
                continue

        return None

    def strategy_version_check(self, cmd, flags=None):
        """
        Strategy 2: Try to get version.
        
        Args:
            cmd (str): Command name
            flags (list): Version flags to try
            
        Returns:
            bool: True if version command succeeds
        """
        return self.strategy_version_extract(cmd, flags) is not None

    def _extract_version(self, output):
        """Extracts the first semantic version-like string from output."""
        matches = re.findall(r"\d+\.\d+(?:\.\d+)*", output)
        return matches[0] if matches else None

    def strategy_windows_registry(self, app_name):
        """
        Strategy 3: Check Windows registry for installed apps.
        
        Args:
            app_name (str): Application name to search for
            
        Returns:
            bool: True if found in registry
        """
        if not self.is_windows:
            return False
        
        try:
            import winreg
            
            # Search in common registry locations
            hives = [
                winreg.HKEY_LOCAL_MACHINE,
                winreg.HKEY_CURRENT_USER
            ]
            
            paths = [
                r"Software\Microsoft\Windows\CurrentVersion\Uninstall",
                r"Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
            ]
            
            for hive in hives:
                for path in paths:
                    try:
                        with winreg.OpenKey(hive, path) as key:
                            for i in range(winreg.QueryInfoKey(key)[0]):
                                subkey_name = winreg.EnumKey(key, i)
                                if app_name.lower() in subkey_name.lower():
                                    return True
                    except:
                        continue
            
            return False
        except:
            return False
    
    def strategy_known_paths(self, cmd, known_paths):
        """
        Strategy 4: Check common installation directories.
        
        Args:
            cmd (str): Command/executable name
            known_paths (list): List of common paths to check
            
        Returns:
            str|None: Full install path if found, otherwise None
        """
        for base_path in known_paths:
            possible_paths = [
                os.path.join(base_path, cmd),
                os.path.join(base_path, cmd + ".exe"),
                os.path.join(base_path, cmd + ".bat"),
                os.path.join(base_path, cmd + ".cmd"),
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    return path
                
        
        return None

    def _find_vscode_cli_wrapper(self):
        """
        Find the Windows VSCode CLI wrapper script.

        The GUI binary `Code.exe` may be on PATH, but the CLI wrapper
        (`code.cmd` or `code.bat`) is the reliable entry point for version
        checks and avoids accidentally launching the editor UI.
        """
        if not self.is_windows:
            return None

        for wrapper in ("code.cmd", "code.bat"):
            wrapper_path = shutil.which(wrapper)
            if wrapper_path:
                return wrapper_path

        for folder in os.getenv("PATH", "").split(os.pathsep):
            if not folder:
                continue
            for wrapper in ("code.cmd", "code.bat"):
                candidate = os.path.join(folder, wrapper)
                if os.path.isfile(candidate):
                    return candidate

        vscode_install_dirs = [
            os.path.expandvars(r"%USERPROFILE%\AppData\Local\Programs\Microsoft VS Code"),
            r"C:\Program Files\Microsoft VS Code",
            r"C:\Program Files (x86)\Microsoft VS Code",
        ]

        for base in vscode_install_dirs:
            if not base:
                continue
            candidate = os.path.join(base, "bin", "code.cmd")
            if os.path.isfile(candidate):
                return candidate

        return None
    
    def get_common_install_paths(self):
        """Get common installation directories based on OS."""
        if self.is_windows:
            return [
                os.path.expandvars(r"%ProgramFiles%"),
                os.path.expandvars(r"%ProgramFiles(x86)%"),
                os.path.expandvars(r"%USERPROFILE%\AppData\Local"),
                os.path.expandvars(r"%USERPROFILE%\AppData\Roaming"),
                r"C:\Program Files",
                r"C:\Program Files (x86)",
            ]
        elif self.is_macos:
            return [
                "/usr/local/bin",
                "/usr/bin",
                "/Applications",
                os.path.expanduser("~/Applications"),
            ]
        else:  # Linux
            return [
                "/usr/local/bin",
                "/usr/bin",
                "/bin",
                "/opt",
                os.path.expanduser("~/.local/bin"),
            ]

    def _expand_path(self, raw_path):
        if not raw_path:
            return raw_path
        return os.path.expanduser(os.path.expandvars(raw_path))

    def _derive_executable_names(self, tool, cmd, rules):
        names = rules.get("executable_names")
        if names:
            return names

        candidates = [cmd]
        if self.is_windows and not cmd.lower().endswith((".exe", ".cmd", ".bat")):
            candidates.extend([f"{cmd}.exe", f"{cmd}.cmd", f"{cmd}.bat"])
        return candidates

    def _find_in_directories(self, directories, exe_names, recursive=False):
        for raw_path in directories or []:
            base_path = self._expand_path(raw_path)
            if not base_path:
                continue

            if recursive and os.path.isdir(base_path):
                for entry in os.listdir(base_path):
                    candidate_dir = os.path.join(base_path, entry)
                    if not os.path.isdir(candidate_dir):
                        continue
                    for exe in exe_names:
                        candidate = os.path.join(candidate_dir, exe)
                        if os.path.exists(candidate):
                            return candidate

            if os.path.isdir(base_path):
                for exe in exe_names:
                    candidate = os.path.join(base_path, exe)
                    if os.path.exists(candidate):
                        return candidate

            if os.path.isfile(base_path) and os.path.basename(base_path) in exe_names:
                return base_path

        return None

    def _find_existing_path(self, paths):
        for raw_path in paths or []:
            path = self._expand_path(raw_path)
            if path and os.path.exists(path):
                return path
        return None

    def _get_detection_rules(self, tool):
        return DETECTION_RULES.get(tool, {})

    def _search_with_rules(self, tool, cmd, flags, rules):
        all_locations_found = []
        primary_location = None
        primary_version = None
        path_found = False
        broken = False

        exe_names = self._derive_executable_names(tool, cmd, rules)

        # Search the PATH first.
        for exe in exe_names:
            path_location = self.strategy_path_check(exe)
            if path_location:
                path_found = True
                primary_location = path_location
                primary_version = self.strategy_version_extract(path_location, flags)
                all_locations_found.append(LocationVersion(path=path_location, version=primary_version))
                break

        # If VSCode on Windows has a CLI wrapper, prefer it for version checks.
        if tool == "vscode" and self.is_windows and not primary_location:
            vscode_wrapper = self._find_vscode_cli_wrapper()
            if vscode_wrapper:
                path_found = True
                primary_location = vscode_wrapper
                primary_version = self.strategy_version_extract(vscode_wrapper, flags)
                all_locations_found.append(LocationVersion(path=primary_location, version=primary_version))

        # Custom configured search paths.
        if not primary_location:
            known_location = self._find_in_directories(rules.get("search_paths"), exe_names, recursive=False)
            if not known_location:
                known_location = self._find_in_directories(rules.get("subdir_search_paths"), exe_names, recursive=True)

            if known_location:
                primary_location = known_location
                primary_version = self.strategy_version_extract(known_location, flags)
                all_locations_found.append(LocationVersion(path=known_location, version=primary_version))

        # Application bundle existence checks.
        if not primary_location:
            app_location = self._find_existing_path(rules.get("app_paths"))
            if app_location:
                primary_location = app_location
                primary_version = self.strategy_version_extract(cmd, flags)
                all_locations_found.append(LocationVersion(path=primary_location, version=primary_version))

        # Registry fallback for Windows when explicit paths are not enough.
        if self.is_windows and not primary_location and rules.get("registry_names"):
            for app_name in rules.get("registry_names", []):
                if self.strategy_windows_registry(app_name):
                    all_locations_found.append(LocationVersion(path=f"<registry:{app_name}>", version=None))
                    break

        return all_locations_found, path_found, primary_location, primary_version

    def check_software(self, tool):
        """Intelligently detect if software is installed.

        Collects ALL discovered locations and versions to accurately classify conflicts.
        Multiple locations with the SAME version = healthy (just duplicate install paths).
        Multiple locations with DIFFERENT versions = CONFLICT (needs user intervention).

        Args:
            tool (str): Tool name to check

        Returns:
            ToolSignal: Detection results with all locations and versions
        """
        cmd = COMMAND_MAP.get(tool, tool)
        flags = VERSION_FLAG.get(tool, ["--version"])
        known_paths = self.get_common_install_paths()
        
        all_locations_found = []
        primary_location = None
        primary_version = None
        path_found = False
        broken = False

        # Handle Python libraries separately
        if TOOL_TYPE.get(tool) == "python_lib":
            detected = self._check_python_lib(tool)
            location = sys.executable if detected else None
            return ToolSignal(
                tool=tool,
                binary_found=detected,
                path_found=detected,
                version=None,
                location=location,
                all_locations=[]
            )

        # Use generic rule-driven detection for configured tools.
        rules = self._get_detection_rules(tool)
        if rules:
            all_locations_found, path_found, primary_location, primary_version = self._search_with_rules(tool, cmd, flags, rules)

            if not all_locations_found:
                known_location = self.strategy_known_paths(cmd, known_paths)
                if known_location:
                    primary_location = known_location
                    primary_version = self.strategy_version_extract(known_location, flags)
                    all_locations_found.append(LocationVersion(
                        path=known_location,
                        version=primary_version
                    ))

            if not all_locations_found:
                fallback_version = self.strategy_version_extract(cmd, flags)
                if fallback_version:
                    all_locations_found.append(LocationVersion(
                        path="<system-path>",
                        version=fallback_version
                    ))
                    primary_version = fallback_version

            binary_found = len(all_locations_found) > 0
            if binary_found and not primary_version and tool != "vscode":
                broken = True

            return ToolSignal(
                tool=tool,
                binary_found=binary_found,
                path_found=path_found,
                version=primary_version,
                location=primary_location,
                all_locations=all_locations_found,
                broken=broken,
                reason=None
            )

        # Search PATH first (highest priority)
        path_location = self.strategy_path_check(cmd)
        vscode_wrapper = self._find_vscode_cli_wrapper() if tool == "vscode" and self.is_windows else None

        if path_location or vscode_wrapper:
            path_found = True
            primary_location = path_location or vscode_wrapper

            # Prefer the VSCode CLI wrapper for version checks when it exists.
            version_cmd = vscode_wrapper if vscode_wrapper else cmd
            primary_version = self.strategy_version_extract(version_cmd, flags)

            all_locations_found.append(LocationVersion(
                path=primary_location,
                version=primary_version
            ))

            if vscode_wrapper and vscode_wrapper != primary_location:
                wrapper_version = self.strategy_version_extract(vscode_wrapper, flags)
                all_locations_found.append(LocationVersion(
                    path=vscode_wrapper,
                    version=wrapper_version
                ))
                if wrapper_version and not primary_version:
                    primary_version = wrapper_version

            if not primary_version and tool != "vscode":
                broken = True

        # Search known paths (secondary priority)
        known_location = self.strategy_known_paths(cmd, known_paths)
        if known_location and known_location != path_location:
            # Found in known path but not already in PATH
            known_version = self.strategy_version_extract(cmd, flags)
            all_locations_found.append(LocationVersion(
                path=known_location, 
                version=known_version
            ))
            # Only set as primary if no PATH entry found
            if not path_location:
                primary_location = known_location
                primary_version = known_version

        # Fallback: try version check without explicit path
        if not path_location and not known_location:
            fallback_version = self.strategy_version_extract(cmd, flags)
            if fallback_version:
                # Tool is callable but exact path not detected
                all_locations_found.append(LocationVersion(
                    path="<system-path>", 
                    version=fallback_version
                ))
                primary_version = fallback_version

        binary_found = len(all_locations_found) > 0

        return ToolSignal(
            tool=tool,
            binary_found=binary_found,
            path_found=path_found,
            version=primary_version,
            location=primary_location,
            all_locations=all_locations_found,
            broken=broken,
            reason=None
        )
    
    def _check_python_lib(self, lib):
        """
        Check if Python library is installed.
        
        Args:
            lib (str): Library name
            
        Returns:
            bool: True if library installed
        """
        try:
            subprocess.run(
                [sys.executable, '-c', f'import {lib}'],
                capture_output=True,
                text=True,
                check=True,
                timeout=3
            )
            return True
        except:
            return False


# Create a global instance
_detector = AdvancedDetector()


def check_software_advanced(tool):
    """
    Check if software is installed using advanced detection.

    This is the recommended function to use instead of the basic checker.

    Args:
        tool (str): Tool name to check

    Returns:
        ToolSignal: Detection results with evidence
    """
    return _detector.check_software(tool)
