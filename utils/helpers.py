"""Helper utilities."""


def print_banner(text):
    """Print a formatted banner."""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def print_success(text):
    """Print success message."""
    print(f"✅ {text}")


def print_error(text):
    """Print error message."""
    print(f"❌ {text}")


def print_warning(text):
    """Print warning message."""
    print(f"⚠️  {text}")


def print_info(text):
    """Print info message."""
    print(f"ℹ️  {text}")
