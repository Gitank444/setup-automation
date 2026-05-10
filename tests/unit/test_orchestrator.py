"""Unit tests for orchestrator."""
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from orchestrator import SetupOrchestrator


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


if __name__ == '__main__':
    unittest.main()
