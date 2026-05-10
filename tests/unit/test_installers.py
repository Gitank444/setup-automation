import unittest
from unittest.mock import MagicMock
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from orchestrator.setup_orchestrator import SetupOrchestrator


class DummyInstaller:
    def __init__(self):
        self.installed = []

    def install(self, package, **kwargs):
        self.installed.append((package, kwargs))
        return True

    def is_available(self):
        return True


class TestInstallers(unittest.TestCase):
    """Verify the orchestrator chooses the correct installer strategy."""

    def setUp(self):
        # Replace real installers with dummy installers for isolated tests.
        self.orchestrator = SetupOrchestrator()
        self.dummy_winget = DummyInstaller()
        self.dummy_pip = DummyInstaller()
        self.dummy_npm = DummyInstaller()
        self.dummy_conda = DummyInstaller()
        self.dummy_choco = DummyInstaller()

        self.orchestrator.installers = {
            'winget': self.dummy_winget,
            'pip': self.dummy_pip,
            'npm': self.dummy_npm,
            'conda': self.dummy_conda,
            'chocolatey': self.dummy_choco,
        }

    def test_installs_python_library_with_pip(self):
        self.assertTrue(self.orchestrator.install_tool('pandas'))
        self.assertEqual(self.dummy_pip.installed[0][0], 'pandas')

    def test_installs_npm_package_with_npm(self):
        self.assertTrue(self.orchestrator.install_tool('react'))
        self.assertEqual(self.dummy_npm.installed[0][0], 'react')

    def test_installs_system_tool_with_winget(self):
        self.assertTrue(self.orchestrator.install_tool('node'))
        self.assertEqual(self.dummy_winget.installed[0][0], 'OpenJS.NodeJS')


if __name__ == '__main__':
    unittest.main()
