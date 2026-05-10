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
