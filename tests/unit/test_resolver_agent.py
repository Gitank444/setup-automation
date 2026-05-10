import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from agents.resolver_agent import ResolverAgent
from models.tool_signal import ToolSignal
from models.tool_status import ToolStatus


class TestResolverAgent(unittest.TestCase):
    """Verify the resolver agent classifies tool signals correctly."""

    def setUp(self):
        self.resolver = ResolverAgent()

    def test_missing_tool(self):
        """Missing tools should be classified as MISSING with install guidance."""
        signal = ToolSignal(tool='git', binary_found=False, path_found=False)
        result = self.resolver.resolve(signal)
        self.assertEqual(result.status, ToolStatus.MISSING)
        self.assertIn('No executable', result.reason)

    def test_partial_tool(self):
        """A binary outside PATH should be classified as PARTIAL."""
        signal = ToolSignal(tool='git', binary_found=True, path_found=False, location='C:\\Program Files\\Git\\cmd\\git.exe')
        result = self.resolver.resolve(signal)
        self.assertEqual(result.status, ToolStatus.PARTIAL)
        self.assertIn('not available through PATH', result.reason)

    def test_outdated_tool(self):
        """Installed tools with a version older than policy should be OUTDATED."""
        signal = ToolSignal(tool='python', binary_found=True, path_found=True, version='3.10.0')
        result = self.resolver.resolve(signal)
        self.assertEqual(result.status, ToolStatus.OUTDATED)
        self.assertIn('older than the required', result.reason)

    def test_broken_tool(self):
        """A tool that is present but unable to report a valid version should be BROKEN."""
        signal = ToolSignal(tool='git', binary_found=True, path_found=True, broken=True)
        result = self.resolver.resolve(signal)
        self.assertEqual(result.status, ToolStatus.BROKEN)
        self.assertIn('cannot produce a valid version', result.reason)

    def test_conflict_tool(self):
        """A tool with multiple different versions across locations should be CONFLICT."""
        from models.tool_signal import LocationVersion
        locations = [
            LocationVersion(path="C:/Python311/python.exe", version="3.11.4"),
            LocationVersion(path="C:/Python38/python.exe", version="3.8.0")
        ]
        signal = ToolSignal(
            tool='python', 
            binary_found=True, 
            path_found=True, 
            version="3.11.4",
            location="C:/Python311/python.exe",
            all_locations=locations
        )
        result = self.resolver.resolve(signal)
        self.assertEqual(result.status, ToolStatus.CONFLICT)
        self.assertIn('Multiple versions', result.reason)


if __name__ == '__main__':
    unittest.main()
