from dataclasses import dataclass
from typing import List


@dataclass
class ToolEvidence:
    tool: str
    command_exists: bool
    pip_installed: bool
    conda_installed: bool
    path_found: bool
    errors: List[str]


@dataclass
class ToolResolution:
    tool: str
    status: str
    confidence: float
    reason: str
    suggested_fix: List[str]
    
    