"""Unit tests for orchestrator."""
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from orchestrator import SetupOrchestrator
from models import ToolStatus


class TestSetupOrchestrator(unittest.TestCase):
    """Test setup orchestrator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.orchestrator = SetupOrchestrator()
    
    def test_display_stacks(self):
        """Test stack display."""
        stacks = self.orchestrator.display_stacks()
        self.assertGreater(len(stacks), 0)
        self.assertIn("webdev", stacks)
    
    @patch('builtins.input', return_value='1')
    def test_get_user_choice_valid(self, mock_input):
        """Test valid user choice."""
        stacks = ['webdev', 'ml_dev', 'backend_dev']
        choice, required = self.orchestrator.get_user_choice(stacks)
        self.assertEqual(choice, 'webdev')
        self.assertIsNotNone(required)
    
    @patch('builtins.input', return_value='999')
    def test_get_user_choice_invalid(self, mock_input):
        """Test invalid user choice."""
        stacks = ['webdev', 'ml_dev']
        choice, required = self.orchestrator.get_user_choice(stacks)
        self.assertIsNone(choice)
        self.assertIsNone(required)

    @patch('builtins.input', return_value='')
    def test_select_install_version_default(self, mock_input):
        """Test version selection defaults when user presses Enter."""
        version = self.orchestrator._select_install_version('python')
        self.assertEqual(version, '3.11')

    @patch('builtins.input', return_value='2')
    def test_select_install_version_specific(self, mock_input):
        """Test selecting a specific version by number."""
        version = self.orchestrator._select_install_version('python')
        self.assertEqual(version, '3.12')

    def test_resolve_package_target_versioned(self):
        """Test version resolution to the correct install target."""
        target = self.orchestrator._resolve_package_target('python', '3.12')
        self.assertEqual(target, 'Python.Python.3.12')

    @patch('builtins.input', return_value='y')
    def test_handle_repairs_calls_repair_tool(self, mock_input):
        """Test the repair flow prompts and invokes repair."""
        self.orchestrator._repair_tool = MagicMock(return_value=True)
        self.orchestrator._handle_repairs([('docker', ToolStatus.BROKEN)])
        self.orchestrator._repair_tool.assert_called_once_with('docker', None)

    def test_install_tool_passes_winget_package_for_version(self):
        """Test that selected version is converted to the correct winget package."""
        self.orchestrator.installers['winget'].install = MagicMock(return_value=True)
        success = self.orchestrator.install_tool('python', '3.12')
        self.assertTrue(success)
        self.orchestrator.installers['winget'].install.assert_called_once_with('Python.Python.3.12', version='3.12')


if __name__ == '__main__':
    unittest.main()
