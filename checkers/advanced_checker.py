"""Advanced software detection with multiple strategies."""
import re
import subprocess
import sys
import os
import shutil
from config import COMMAND_MAP, VERSION_FLAG, TOOL_TYPE
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
                os.path.expandvars("~/Applications"),
            ]
        else:  # Linux
            return [
                "/usr/local/bin",
                "/usr/bin",
                "/bin",
                "/opt",
                os.path.expandvars("~/.local/bin"),
            ]
    
    def detect_docker(self):
        """
        Special detection for Docker.
        
        Returns:
            bool: True if Docker is installed
        """
        # Strategy 1: Docker command in PATH
        if self.strategy_path_check("docker"):
            return True
        
        # Strategy 2: Docker Desktop specific paths (Windows/macOS)
        if self.is_windows:
            docker_paths = [
                r"C:\Program Files\Docker\Docker",
                os.path.expandvars(r"%USERPROFILE%\AppData\Local\Docker"),
            ]
            if self.strategy_known_paths("docker.exe", docker_paths):
                return True
            
            # Strategy 3: Windows Registry
            if self.strategy_windows_registry("Docker"):
                return True
        
        elif self.is_macos:
            docker_paths = [
                "/Applications/Docker.app",
            ]
            if any(os.path.exists(p) for p in docker_paths):
                return True
        
        return False
    
    def detect_vscode(self):
        """
        Special detection for VSCode.
        
        Returns:
            bool: True if VSCode is installed
        """
        # Strategy 1: 'code' command in PATH
        if self.strategy_path_check("code"):
            return True
        
        # Strategy 2: VSCode specific paths
        if self.is_windows:
            vscode_paths = [
                r"C:\Program Files\Microsoft VS Code",
                r"C:\Program Files (x86)\Microsoft VS Code",
                os.path.expandvars(r"%USERPROFILE%\AppData\Local\Programs\Microsoft VS Code"),
            ]
            if self.strategy_known_paths("code.exe", vscode_paths):
                return True
            
            # Strategy 3: Windows Registry
            if self.strategy_windows_registry("Visual Studio Code"):
                return True
        
        elif self.is_macos:
            vscode_paths = [
                "/Applications/Visual Studio Code.app",
            ]
            if any(os.path.exists(p) for p in vscode_paths):
                return True
        
        return False
    
    def detect_android_studio(self):
        """
        Special detection for Android Studio.
        
        Returns:
            bool: True if Android Studio is installed
        """
        if self.is_windows:
            # Check Windows Registry
            if self.strategy_windows_registry("Android Studio"):
                return True
            
            # Check common paths
            as_paths = [
                r"C:\Program Files\Android\Android Studio",
                os.path.expandvars(r"%USERPROFILE%\AppData\Local\Android\android-studio"),
            ]
            if self.strategy_known_paths("studio64.exe", as_paths):
                return True
        
        elif self.is_macos:
            if os.path.exists("/Applications/Android Studio.app"):
                return True
        
        return False
    
    def detect_unity(self):
        """
        Special detection for Unity.
        
        Returns:
            bool: True if Unity is installed
        """
        if self.is_windows:
            if self.strategy_windows_registry("Unity"):
                return True
            
            unity_paths = [
                r"C:\Program Files\Unity\Hub",
            ]
            if self.strategy_known_paths("unity.exe", unity_paths):
                return True
        
        elif self.is_macos:
            if os.path.exists("/Applications/Unity/Hub"):
                return True
        
        return False
    
    def detect_blender(self):
        """
        Special detection for Blender.
        
        Returns:
            bool: True if Blender is installed
        """
        if self.strategy_path_check("blender"):
            return True
        
        if self.is_windows:
            blender_paths = [
                r"C:\Program Files\Blender Foundation\Blender",
            ]
            if self.strategy_known_paths("blender.exe", blender_paths):
                return True
            
            if self.strategy_windows_registry("Blender"):
                return True
        
        elif self.is_macos:
            if os.path.exists("/Applications/Blender.app"):
                return True
        
        return False
    
    def detect_ollama(self):
        """
        Special detection for Ollama.
        
        Returns:
            bool: True if Ollama is installed
        """
        if self.strategy_path_check("ollama"):
            return True
        
        if self.is_windows:
            if self.strategy_windows_registry("Ollama"):
                return True
            
            ollama_paths = [
                os.path.expandvars(r"%USERPROFILE%\AppData\Local\Programs\Ollama"),
            ]
            if self.strategy_known_paths("ollama.exe", ollama_paths):
                return True
        
        return False
    
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
