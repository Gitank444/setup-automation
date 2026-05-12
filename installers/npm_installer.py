"""NPM installer implementation."""
import subprocess
from .base_installer import BaseInstaller


class NpmInstaller(BaseInstaller):
    """Install packages using npm."""
    
    def is_available(self):
        """Check if npm is available."""
        try:
            subprocess.run(
                ["npm", "--version"],
                capture_output=True,
                check=True
            )
            return True
        except:
            return False
    
    def install(self, package, global_flag=False, version=None):
        """
        Install a package using npm.
        
        Args:
            package (str): Package name or package spec
            global_flag (bool): Install globally if True
            version (str|None): Optional version to install
            
        Returns:
            bool: True if installation was successful
        """
        install_target = package
        if version and "@" not in package:
            install_target = f"{package}@{version}"

        cmd = [
            "npm",
            "install",
            install_target
        ]
        
        if global_flag:
            cmd.insert(2, "-g")
        
        print(f"\n📦 Installing {package} via npm...")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        print(result.stdout)

        if result.returncode == 0:
            print(f"✅ {package} installed via npm")
            return True

        print(f"❌ Failed installing {package} via npm")
        print(result.stderr)
        return False

    def uninstall(self, package, global_flag=False, version=None):
        """
        Uninstall a package using npm.

        Args:
            package (str): Package name or package spec
            global_flag (bool): Uninstall globally if True
            version (str|None): Optional version (ignored)

        Returns:
            bool: True if uninstallation was successful
        """
        pkg = package.split("@")[0]

        cmd = [
            "npm",
            "uninstall",
            pkg
        ]
        if global_flag:
            cmd.insert(2, "-g")

        print(f"\n🗑️ Uninstalling {pkg} via npm...")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        print(result.stdout)

        if result.returncode == 0:
            print(f"✅ {pkg} uninstalled via npm")
            return True

        print(f"❌ Failed uninstalling {pkg} via npm")
        print(result.stderr)
        return False
