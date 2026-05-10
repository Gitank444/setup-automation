"""
Run tests for the setup automation project.

Usage:
    python run_tests.py                 # Run all tests
    python run_tests.py unit            # Run only unit tests
    python run_tests.py integration     # Run only integration tests
    python run_tests.py verbose         # Run with verbose output
    python run_tests.py --help          # Print usage information
"""

import sys
import unittest
import os


def usage():
    print("Usage: python run_tests.py [unit|integration|all] [verbose|v]")
    print("")
    print("Options:")
    print("  unit          Run unit tests only")
    print("  integration   Run integration tests only")
    print("  all           Run all tests (default)")
    print("  verbose, v    Run tests with verbose output")
    print("  -h, --help    Show this help message")


def run_tests(test_path, verbosity=1):
    """Run tests discovered under the given path."""
    loader = unittest.TestLoader()
    suite = loader.discover(test_path, pattern='test_*.py')
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


def run_all_tests(verbosity=1):
    """Run all tests in the tests directory."""
    return run_tests('tests', verbosity)


def run_unit_tests(verbosity=1):
    """Run only unit tests."""
    return run_tests('tests/unit', verbosity)


def run_integration_tests(verbosity=1):
    """Run only integration tests."""
    return run_tests('tests/integration', verbosity)


def main():
    """Main entry point."""
    args = sys.argv[1:]

    if '-h' in args or '--help' in args:
        usage()
        return 0

    verbosity = 2 if 'verbose' in args or 'v' in args else 1

    if 'unit' in args:
        print("Running unit tests...\n")
        return run_unit_tests(verbosity)
    if 'integration' in args:
        print("Running integration tests...\n")
        return run_integration_tests(verbosity)

    print("Running all tests...\n")
    return run_all_tests(verbosity)


if __name__ == '__main__':
    exit(main())
