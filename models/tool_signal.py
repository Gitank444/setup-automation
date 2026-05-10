from dataclasses import dataclass, field


@dataclass
class LocationVersion:
    """Track a tool location and its version."""
    path: str
    version: str | None = None


@dataclass
class ToolSignal:
    """Detection evidence for a tool across the system.
    
    This carries raw detection data: where the tool was found,
    what version each location reports, and any health issues.
    """
    tool: str
    binary_found: bool
    path_found: bool
    
    # Primary location (in PATH if available, else first discovered location)
    location: str | None = None
    version: str | None = None
    
    # All discovered locations and their versions for conflict/duplicate detection
    all_locations: list[LocationVersion] = field(default_factory=list)
    
    # Health flags
    broken: bool = False  # Tool exists but cannot report version
    reason: str | None = None
