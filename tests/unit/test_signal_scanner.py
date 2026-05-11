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

    @patch('checkers.advanced_checker.shutil.which')
    @patch('checkers.advanced_checker.subprocess.run')
    def test_detects_vscode_cli_wrapper_and_reports_version(self, mock_run, mock_which):
        """VSCode should use the CLI wrapper for version detection when available."""
        def which_side_effect(arg):
            if arg == 'code':
                return r"C:\Users\Gitank\AppData\Local\Programs\Microsoft VS Code\code.EXE"
            if arg == 'code.cmd':
                return r"C:\Users\Gitank\AppData\Local\Programs\Microsoft VS Code\bin\code.cmd"
            return None

        mock_which.side_effect = which_side_effect

        def run_side_effect(cmd, *args, **kwargs):
            command_path = cmd[0]
            if command_path.endswith('code.EXE'):
                return MagicMock(returncode=1, stdout="", stderr="")
            if command_path.endswith('code.cmd'):
                return MagicMock(returncode=0, stdout="22.22.1\n", stderr="")
            return MagicMock(returncode=1, stdout="", stderr="")

        mock_run.side_effect = run_side_effect

        detector = AdvancedDetector()
        signal = detector.check_software('vscode')

        self.assertTrue(signal.binary_found)
        self.assertTrue(signal.path_found)
        self.assertFalse(signal.broken)
        self.assertEqual(signal.version, '22.22.1')
        self.assertEqual(signal.location, r"C:\Users\Gitank\AppData\Local\Programs\Microsoft VS Code\code.EXE")
        self.assertTrue(any(loc.path.endswith('code.cmd') for loc in signal.all_locations))

    @patch('checkers.advanced_checker.shutil.which')
    @patch('checkers.advanced_checker.subprocess.run')
    def test_vscode_code_exe_without_version_is_not_broken(self, mock_run, mock_which):
        """Code.exe without version output should still be considered installed."""
        def which_side_effect(arg):
            if arg == 'code':
                return r"C:\Users\Gitank\AppData\Local\Programs\Microsoft VS Code\code.EXE"
            if arg in ('code.cmd', 'code.bat'):
                return None
            return None

        mock_which.side_effect = which_side_effect
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="")

        detector = AdvancedDetector()
        signal = detector.check_software('vscode')

        self.assertTrue(signal.binary_found)
        self.assertTrue(signal.path_found)
        self.assertFalse(signal.broken)
        self.assertIsNone(signal.version)


if __name__ == '__main__':
    unittest.main()
