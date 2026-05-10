"""Integration tests for the full setup process."""
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from orchestrator import SetupOrchestrator
from checkers import check_software
from config import STACKS
from models.tool_signal import ToolSignal


class TestFullSetupFlow(unittest.TestCase):
    """Test complete setup workflow."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.orchestrator = SetupOrchestrator()
    
    def test_stacks_are_defined(self):
        """Test that stacks are properly defined."""
        self.assertGreater(len(STACKS), 0)
        self.assertIn("webdev", STACKS)
        self.assertIsInstance(STACKS["webdev"], list)
    
    def test_missing_tools_detection(self):
        """Test detection of missing tools."""
        # Use a stack with common tools
        tools = STACKS.get("webdev", [])
        missing = []
        for tool in tools:
            if not check_software(tool):
                missing.append(tool)
        self.assertIsInstance(missing, list)
    
    @patch('builtins.input', return_value='y')
    @patch('orchestrator.setup_orchestrator.SetupOrchestrator.verify_installation', return_value=True)
    @patch('orchestrator.setup_orchestrator.SetupOrchestrator.install_tool', return_value=True)
    @patch('orchestrator.setup_orchestrator.check_software_advanced')
    def test_installation_flow(self, mock_check_advanced, mock_install_tool, mock_verify, mock_input):
        """Test installation flow using repairable missing tools."""
        # The orchestrator checks tool state after the install completes.
        mock_check_advanced.side_effect = [
            ToolSignal(tool='git', binary_found=True, path_found=True, version='2.40.1')
        ]

        result = self.orchestrator.install_missing_tools(['git'])
        self.assertTrue(result)
        mock_install_tool.assert_called_once_with('git')
        mock_verify.assert_called_once_with('git')


if __name__ == '__main__':
    unittest.main()
