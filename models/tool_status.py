from enum import Enum

class ToolStatus(Enum):
    INSTALLED = "installed"
    MISSING = "missing"
    PARTIAL = "partial"
    BROKEN = "broken"
    OUTDATED = "outdated"
    CONFLICT = "conflict"