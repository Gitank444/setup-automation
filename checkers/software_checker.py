"""Software checker utilities."""
import subprocess
import sys
from config import COMMAND_MAP, VERSION_FLAG, TOOL_TYPE

def check_system_tool(cmd):
    """
    Check if a system tool is installed by running its version command.
    
    Args:
        cmd (str or list): Command to check
        
    Returns:
        bool: True if tool is installed and accessible, False otherwise
    """
    try:
        if isinstance(cmd, str):
            cmd_list = [cmd]
        else:
            cmd_list = cmd

        # Get version flags, default to --version
        tool_key = None
        for key, val in COMMAND_MAP.items():
            if val == cmd_list[0]:
                tool_key = key
                break
        flags = VERSION_FLAG.get(tool_key, ["--version"])

        result = subprocess.run(
            cmd_list + flags,
            capture_output=True,
            text=True,
            timeout=5
        )

        return result.returncode == 0

    except FileNotFoundError:
        return False
    except Exception:
        return False


def check_python_lib(lib):
    """
    Check if a Python library is installed.
    
    Args:
        lib (str): Library name to check
        
    Returns:
        bool: True if library is installed, False otherwise
    """
    try:
        subprocess.run(
            [sys.executable, '-c', f'import {lib}'],
            capture_output=True,
            text=True,
            check=True
        )
        return True
    except Exception:
        return False

def check_software(tool):
    """
    Intelligently check if software is installed based on tool type.
    
    Args:
        tool (str): Tool/package name to check
        
    Returns:
        bool: True if tool is installed, False otherwise
    """
    tool_type = TOOL_TYPE.get(tool)

    if tool_type == "system":
        cmd = COMMAND_MAP.get(tool, tool)
        return check_system_tool(cmd)

    elif tool_type == "python_lib":
        return check_python_lib(tool)

    cmd = COMMAND_MAP.get(tool, tool)
    return check_system_tool(cmd)
