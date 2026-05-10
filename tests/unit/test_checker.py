"""Unit tests for software checker."""
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from checkers import check_software, check_system_tool, check_python_lib


class TestCheckSystemTool(unittest.TestCase):
    """Test system tool detection."""
    
    @patch('checkers.software_checker.subprocess.run')
    def test_tool_installed(self, mock_run):
        """Test detection of installed tool."""
        mock_run.return_value = MagicMock(returncode=0)
        result = check_system_tool("python")
        self.assertTrue(result)
    
    @patch('checkers.software_checker.subprocess.run')
    def test_tool_not_installed(self, mock_run):
        """Test detection of missing tool."""
        mock_run.side_effect = FileNotFoundError()
        result = check_system_tool("nonexistent_tool")
        self.assertFalse(result)
    
    @patch('checkers.software_checker.subprocess.run')
    def test_tool_command_fails(self, mock_run):
        """Test when tool command fails."""
        mock_run.return_value = MagicMock(returncode=1)
        result = check_system_tool("python")
        self.assertFalse(result)


class TestCheckPythonLib(unittest.TestCase):
    """Test Python library detection."""
    
    @patch('checkers.software_checker.subprocess.run')
    def test_library_installed(self, mock_run):
        """Test detection of installed library."""
        mock_run.return_value = MagicMock(returncode=0)
        result = check_python_lib("sys")
        self.assertTrue(result)
    
    @patch('checkers.software_checker.subprocess.run')
    def test_library_not_installed(self, mock_run):
        """Test detection of missing library."""
        mock_run.side_effect = Exception("Module not found")
        result = check_python_lib("nonexistent_library")
        self.assertFalse(result)


class TestCheckSoftware(unittest.TestCase):
    """Test intelligent software checking."""
    
    @patch('checkers.software_checker.check_system_tool')
    def test_check_system_tool_type(self, mock_check):
        """Test checking a system tool."""
        mock_check.return_value = True
        result = check_software("python")
        self.assertTrue(result)
        mock_check.assert_called()
    
    @patch('checkers.software_checker.check_python_lib')
    def test_check_python_lib_type(self, mock_check):
        """Test checking a Python library."""
        mock_check.return_value = True
        result = check_software("pandas")
        self.assertTrue(result)
        mock_check.assert_called()


if __name__ == '__main__':
    unittest.main()
