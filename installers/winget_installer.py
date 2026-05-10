"""Winget installer implementation."""
import subprocess
import time
from .base_installer import BaseInstaller


class WingetInstaller(BaseInstaller):
    """Install packages using Windows Package Manager (winget)."""
    
    def is_available(self):
        """Check if winget is available."""
        try:
            subprocess.run(
                ["winget", "--version"],
                capture_output=True,
                check=True
            )
            return True
        except:
            return False
    
    def install(self, package, retries=2):
        """
        Install a package using winget.
        
        Args:
            package (str): Winget package ID
            retries (int): Number of retry attempts
            
        Returns:
            bool: True if installation was successful
        """
        cmd = [
            "winget",
            "install",
            "--id", package,
            "-e",
            "--accept-package-agreements",
            "--accept-source-agreements"
        ]

        for attempt in range(retries):
            print(f"\n📥 Installing {package} via winget (Attempt {attempt+1}/{retries})")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )

            print("\n--- STDOUT ---")
            print(result.stdout)

            if result.stderr:
                print("\n--- STDERR ---")
                print(result.stderr)

            if result.returncode == 0:
                print(f"\n✅ {package} installed successfully via winget")
                return True

            print(f"\n⚠️  Attempt failed for {package}")
            time.sleep(3)

        print(f"\n❌ Installation failed for {package} after {retries} attempts")
        return False
