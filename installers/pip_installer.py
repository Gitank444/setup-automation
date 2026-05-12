"""Pip installer implementation."""
import subprocess
import sys
from .base_installer import BaseInstaller


class PipInstaller(BaseInstaller):
    """Install Python packages using pip."""
    
    def is_available(self):
        """Check if pip is available."""
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "--version"],
                capture_output=True,
                check=True
            )
            return True
        except:
            return False
    
    def install(self, package, version=None):
        """
        Install a package using pip.
        
        Args:
            package (str): Package name or package spec
            version (str|None): Optional version to install
            
        Returns:
            bool: True if installation was successful
        """
        install_target = package
        if version and "==" not in package:
            install_target = f"{package}=={version}"

        cmd = [
            sys.executable,
            "-m",
            "pip",
            "install",
            install_target
        ]

        print(f"\n🐍 Installing {package} via pip...")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        print(result.stdout)

        if result.returncode == 0:
            print(f"✅ {package} installed via pip")
            return True

        print(f"❌ Failed installing {package} via pip")
        print(result.stderr)
        return False

    def uninstall(self, package, version=None, global_flag=False):
        """
        Uninstall a package using pip.

        Args:
            package (str): Package name or package spec
            version (str|None): Optional version to uninstall
            global_flag (bool): Ignored for pip

        Returns:
            bool: True if uninstallation was successful
        """
        target = package
        if "==" in package:
            target = package.split("==")[0]
        if version:
            target = version if target == package else target

        cmd = [
            sys.executable,
            "-m",
            "pip",
            "uninstall",
            "-y",
            target
        ]

        print(f"\n🗑️ Uninstalling {target} via pip...")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        print(result.stdout)

        if result.returncode == 0:
            print(f"✅ {target} uninstalled via pip")
            return True

        print(f"❌ Failed uninstalling {target} via pip")
        print(result.stderr)
        return False
