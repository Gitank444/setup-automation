"""Installers package with multiple installation methods."""
from .base_installer import BaseInstaller
from .winget_installer import WingetInstaller
from .pip_installer import PipInstaller
from .npm_installer import NpmInstaller
from .conda_installer import CondaInstaller
from .chocolatey_installer import ChocolateyInstaller

__all__ = [
    'BaseInstaller',
    'WingetInstaller',
    'PipInstaller',
    'NpmInstaller',
    'CondaInstaller',
    'ChocolateyInstaller'
]
