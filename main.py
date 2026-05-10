"""
Main entry point for the Setup Automation System.

This script orchestrates the installation of development stacks
with intelligent package manager selection and verification.
"""

from orchestrator import SetupOrchestrator
def main():
    """Run the setup orchestrator."""
    orchestrator = SetupOrchestrator()
    success = orchestrator.run()
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())