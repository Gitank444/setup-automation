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
    
    def install(self, package, version=None, retries=2):
        """
        Install a package using winget.
        
        Args:
            package (str): Winget package ID or search term
            version (str|None): Optional explicit version of the package
            retries (int): Number of retry attempts
            
        Returns:
            bool: True if installation was successful
        """
        if not self.is_available():
            print("❌ winget is not available on this system. Please install Windows Package Manager first.")
            return False

        install_cmd = [
            "winget",
            "install",
            "--id", package,
            "-e",
            "--accept-package-agreements",
            "--accept-source-agreements"
        ]

        if version:
            install_cmd.extend(["--version", version])

        for attempt in range(retries):
            print(f"\n📥 Installing {package} via winget (Attempt {attempt+1}/{retries})")
            result = subprocess.run(
                install_cmd,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                print(f"\n✅ {package} installed successfully via winget")
                return True

            print(f"\n⚠️  Attempt failed for {package}")
            if result.stdout:
                print("--- winget stdout ---")
                print(result.stdout)
            if result.stderr:
                print("--- winget stderr ---")
                print(result.stderr)

            # If exact ID install fails, try a fallback without --id and -e.
            if attempt == 0 and "--id" in install_cmd:
                fallback_cmd = [
                    "winget",
                    "install",
                    package,
                    "--accept-package-agreements",
                    "--accept-source-agreements"
                ]
                if version:
                    fallback_cmd.extend(["--version", version])

                print(f"\nℹ️  Trying fallback winget install for {package} without exact ID")
                fallback_result = subprocess.run(
                    fallback_cmd,
                    capture_output=True,
                    text=True
                )

                if fallback_result.returncode == 0:
                    print(f"\n✅ {package} installed successfully via winget fallback")
                    return True

                if fallback_result.stdout:
                    print("--- fallback stdout ---")
                    print(fallback_result.stdout)
                if fallback_result.stderr:
                    print("--- fallback stderr ---")
                    print(fallback_result.stderr)

            time.sleep(3)

        print(f"\n❌ Installation failed for {package} after {retries} attempts")
        return False

    def uninstall(self, package, version=None, global_flag=False):
        """
        Uninstall a package using winget.

        Args:
            package (str): Winget package ID
            version (str|None): Optional explicit version
            global_flag (bool): Ignored for winget

        Returns:
            bool: True if uninstallation was successful
        """
        cmd = [
            "winget",
            "uninstall",
            "--id", package,
            "--accept-package-agreements",
            "--accept-source-agreements"
        ]

        if version:
            cmd.extend(["--version", version])

        print(f"\n🗑️ Uninstalling {package} via winget...")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.returncode == 0:
            print(f"✅ {package} uninstalled successfully via winget")
            return True
        print(f"❌ Failed uninstalling {package} via winget")
        print(result.stderr)
        return False
