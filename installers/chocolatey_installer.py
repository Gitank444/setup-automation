"""Chocolatey installer implementation."""
import subprocess
from .base_installer import BaseInstaller


class ChocolateyInstaller(BaseInstaller):
    """Install packages using Chocolatey."""
    
    def is_available(self):
        """Check if chocolatey is available."""
        try:
            subprocess.run(
                ["choco", "--version"],
                capture_output=True,
                check=True
            )
            return True
        except:
            return False
    
    def install(self, package):
        """
        Install a package using Chocolatey.
        
        Args:
            package (str): Package name
            
        Returns:
            bool: True if installation was successful
        """
        cmd = [
            "choco",
            "install",
            "-y",
            package
        ]
        
        print(f"\n📦 Installing {package} via Chocolatey...")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        print(result.stdout)

        if result.returncode == 0:
            print(f"✅ {package} installed via Chocolatey")
            return True

        print(f"❌ Failed installing {package} via Chocolatey")
        print(result.stderr)
        return False

    def uninstall(self, package, version=None, global_flag=False):
        """
        Uninstall a package using Chocolatey.

        Args:
            package (str): Package name
            version (str|None): Optional version (ignored)
            global_flag (bool): Ignored for Chocolatey

        Returns:
            bool: True if uninstallation was successful
        """
        cmd = [
            "choco",
            "uninstall",
            "-y",
            package
        ]

        print(f"\n🗑️ Uninstalling {package} via Chocolatey...")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        print(result.stdout)

        if result.returncode == 0:
            print(f"✅ {package} uninstalled via Chocolatey")
            return True

        print(f"❌ Failed uninstalling {package} via Chocolatey")
        print(result.stderr)
        return False
