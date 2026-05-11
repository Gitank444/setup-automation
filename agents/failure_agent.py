from enum import Enum
from models import LocationVersion
from config import INSTALL_MAP

class FailureType(Enum):
    NETWORK = "network"
    PERMISSION = "permission"
    VERSION_CONFLICT = "version_conflict"
    PATH_ERROR = "path_error"
    OTHER = "other"


class FailureAgent:
    """Provide human-readable guidance when tool detection or installation fails.

    This agent converts a detected problem into a short, actionable message that
    is useful for developers and non-expert operators.
    """

    TOOL_ADVICE = {
        "python": {
            "manual": "winget install Python.Python.3.11",
            "download": "https://www.python.org/downloads",
            "pip_note": "Included with Python installation",
        },
        "pip": {
            "manual": "python -m ensurepip --upgrade",
            "download": "https://pip.pypa.io/en/stable/installing/",
            "note": "Usually included with Python; use above command to repair.",
        },
        "node": {
            "manual": "winget install OpenJS.NodeJS",
            "download": "https://nodejs.org/en/download",
        },
        "npm": {
            "manual": "Included with Node.js",
            "download": "https://nodejs.org/en/download",
        },
        "yarn": {
            "manual": "npm install -g yarn",
            "download": "https://yarnpkg.com/getting-started",
        },
        "git": {
            "manual": "winget install Git.Git",
            "download": "https://git-scm.com/download/win",
        },
        "docker": {
            "manual": "winget install Docker.DockerDesktop",
            "download": "https://docs.docker.com/get-docker",
            "note": "Large download; allow 2GB+ free space.",
        },
        "vscode": {
            "manual": "winget install Microsoft.VisualStudioCode",
            "download": "https://code.visualstudio.com/download",
        },
        "blender": {
            "manual": "winget install BlenderFoundation.Blender",
            "download": "https://www.blender.org/download",
            "note": "Requires 500MB+ disk space.",
        },
        "unity": {
            "manual": "winget install Unity.Hub",
            "download": "https://unity.com/download",
            "note": "Large download; allow 2GB+ free space.",
        },
        "react": {
            "manual": "npx create-react-app <app-name>",
            "download": "https://react.dev/learn/installation",
            "note": "Requires Node.js and npm.",
        },
        "cmake": {
            "manual": "winget install Kitware.CMake",
            "download": "https://cmake.org/download",
        },
        "gcc": {
            "manual": "winget install GnuWin32.Make",
            "download": "https://gcc.gnu.org",
        },
    }

    def get_advice(self, tool: str, status: Enum, signal_details: dict = None) -> list[str]:
        """Return formatted guidance lines for a tool failure status.
        
        Args:
            tool: Tool name
            status: ToolStatus enum value
            signal_details: Optional dict with 'path', 'locations', etc for rich formatting
        """
        advice = []
        tool_data = self.TOOL_ADVICE.get(tool, {})
        signal_details = signal_details or {}

        if status.name == "MISSING":
            # Missing tools need direct install guidance.
            package = INSTALL_MAP.get(tool)
            if package:
                advice.append(f"💡 Run: winget install {package}")
            elif tool_data.get("manual"):
                advice.append(f"💡 Run: {tool_data['manual']}")
            if tool_data.get("download"):
                advice.append(f"   Or download: {tool_data['download']}")
            if tool_data.get("note"):
                advice.append(f"   Note: {tool_data['note']}")
            if not advice:
                advice.append("💡 Install using 'winget install <package-name>' or your preferred package manager.")

        elif status.name == "PARTIAL":
            # Tool found but not in PATH
            path = signal_details.get("path")
            if path:
                advice.append(f"💡 Found at: {path}")
                # Extract directory from path
                import os
                dir_path = os.path.dirname(path)
                advice.append(f"💡 Add to PATH: {dir_path}")
                advice.append("   → Windows: Settings → Edit Environment Variables → Path → New")
            else:
                advice.append("💡 Tool exists but not in PATH. Add its directory to PATH or reinstall.")

        elif status.name == "OUTDATED":
            # Version too old
            current = signal_details.get("current")
            required = signal_details.get("required")
            if current and required:
                advice.append(f"🔄 Current: {current} → Required: {required}")
            advice.append(f"   Run: {tool_data.get('manual', 'winget upgrade ' + tool)}")

        elif status.name == "BROKEN":
            # Binary exists but broken
            advice.append("⚠️  Repair or reinstall:")
            if tool_data.get("manual"):
                advice.append(f"   Run: {tool_data['manual']}")
            else:
                advice.append(f"   Run: winget install {tool}")

        elif status.name == "CONFLICT":
            # Multiple versions detected
            locations = signal_details.get("locations", [])
            primary = signal_details.get("primary_version")
            
            if locations:
                advice.append("⚠️  Conflict: Multiple versions detected")
                for i, loc in enumerate(locations):
                    if isinstance(loc, LocationVersion):
                        marker = " ← recommended" if (primary and loc.version == primary) else ""
                        advice.append(f"   [{i+1}] v{loc.version or '?'} @ {loc.path}{marker}")
                    else:
                        # Fallback for raw dict/tuple
                        path = loc.get("path") if isinstance(loc, dict) else loc[0]
                        ver = loc.get("version") if isinstance(loc, dict) else loc[1]
                        marker = " ← recommended" if (primary and ver == primary) else ""
                        advice.append(f"   [{i+1}] v{ver or '?'} @ {path}{marker}")
                advice.append("   Remove all but your preferred version.")
            else:
                advice.append("⚠️  Conflict: Multiple versions detected.")
                advice.append("   Keep only the version you want to use.")

        return advice
