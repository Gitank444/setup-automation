"""Configuration package for setup automation."""
from .constants import COMMAND_MAP, VERSION_FLAG, TOOL_TYPE, INSTALL_MAP, INSTALL_STRATEGY, MINIMUM_VERSION
from .stacks import STACKS

__all__ = [
    'COMMAND_MAP',
    'VERSION_FLAG',
    'TOOL_TYPE',
    'INSTALL_MAP',
    'INSTALL_STRATEGY',
    'MINIMUM_VERSION',
    'STACKS'
]
