"""Conda installer implementation."""
import subprocess
from .base_installer import BaseInstaller


class CondaInstaller(BaseInstaller):
    """Install packages using conda (Anaconda)."""
    
    def is_available(self):
        """Check if conda is available."""
        try:
            subprocess.run(
                ["conda", "--version"],
                capture_output=True,
                check=True
            )
            return True
        except:
            return False
    
    def install(self, package):
        """
        Install a package using conda.
        
        Args:
            package (str): Package name
            
        Returns:
            bool: True if installation was successful
        """
        cmd = [
            "conda",
            "install",
            "-y",
            package
        ]
        
        print(f"\n📦 Installing {package} via conda...")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        print(result.stdout)

        if result.returncode == 0:
            print(f"✅ {package} installed via conda")
            return True

        print(f"❌ Failed installing {package} via conda")
        print(result.stderr)
        return False
