import unittest
from unittest.mock import patch, MagicMock
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from checkers.advanced_checker import AdvancedDetector


class TestSignalScanner(unittest.TestCase):
    """Ensure the advanced signal scanner returns consistent tool detection data."""

    @patch('checkers.advanced_checker.shutil.which')
    @patch('checkers.advanced_checker.subprocess.run')
    def test_detects_path_and_version(self, mock_run, mock_which):
        """A tool in PATH should be classified as found with a valid version."""
        mock_which.return_value = r"C:\Program Files\Git\cmd\git.exe"
        mock_run.return_value = MagicMock(returncode=0, stdout="git version 2.40.1\n", stderr="")

        detector = AdvancedDetector()
        signal = detector.check_software('git')

        self.assertTrue(signal.binary_found)
        self.assertTrue(signal.path_found)
        self.assertEqual(signal.version, '2.40.1')
        self.assertEqual(signal.location, r"C:\Program Files\Git\cmd\git.exe")

    @patch('checkers.advanced_checker.shutil.which', return_value=None)
    @patch('checkers.advanced_checker.AdvancedDetector.strategy_known_paths')
    @patch('checkers.advanced_checker.subprocess.run')
    def test_detects_partial_installation(self, mock_run, mock_known_paths, mock_which):
        """A binary found outside PATH should be marked as partial."""
        mock_known_paths.return_value = r"C:\Program Files\Git\cmd\git.exe"
        mock_run.return_value = MagicMock(returncode=0, stdout="git version 2.40.1\n", stderr="")

        detector = AdvancedDetector()
        signal = detector.check_software('git')

        self.assertTrue(signal.binary_found)
        self.assertFalse(signal.path_found)
        self.assertEqual(signal.version, '2.40.1')
        self.assertEqual(signal.location, r"C:\Program Files\Git\cmd\git.exe")

    @patch('checkers.advanced_checker.shutil.which')
    @patch('checkers.advanced_checker.subprocess.run')
    def test_detects_broken_tool_when_version_fails(self, mock_run, mock_which):
        """A tool that exists but cannot report a version should be considered broken."""
        mock_which.return_value = r"C:\Program Files\Git\cmd\git.exe"
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="error")

        detector = AdvancedDetector()
        signal = detector.check_software('git')

        self.assertTrue(signal.binary_found)
        self.assertTrue(signal.path_found)
        self.assertTrue(signal.broken)
        self.assertIsNone(signal.version)


if __name__ == '__main__':
    unittest.main()
