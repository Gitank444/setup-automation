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
    
    def install(self, package):
        """
        Install a package using pip.
        
        Args:
            package (str): Package name
            
        Returns:
            bool: True if installation was successful
        """
        cmd = [
            sys.executable,
            "-m",
            "pip",
            "install",
            package
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
