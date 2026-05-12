"""Base installer class."""
from abc import ABC, abstractmethod


class BaseInstaller(ABC):
    """Abstract base class for all installers."""
    
    def __init__(self):
        """Initialize the installer."""
        self.name = self.__class__.__name__
    
    @abstractmethod
    def install(self, package):
        """
        Install a package.
        
        Args:
            package (str): Package name to install
            
        Returns:
            bool: True if installation was successful, False otherwise
        """
        pass

    def uninstall(self, package, global_flag=False):
        """
        Uninstall a package.

        Args:
            package (str): Package name or package spec to uninstall
            global_flag (bool): Optional global uninstall for npm

        Returns:
            bool: True if uninstallation was successful, False otherwise
        """
        raise NotImplementedError
    
    @abstractmethod
    def is_available(self):
        """
        Check if this installer is available on the system.
        
        Returns:
            bool: True if installer is available, False otherwise
        """
        pass
