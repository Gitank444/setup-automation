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
    
    def install(self, package, global_flag=False):
        """
        Install a package using npm.
        
        Args:
            package (str): Package name
            global_flag (bool): Install globally if True
            
        Returns:
            bool: True if installation was successful
        """
        cmd = [
            "npm",
            "install",
            package
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
