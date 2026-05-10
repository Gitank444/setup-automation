"""
Debug and troubleshoot software detection.

This script helps identify why certain tools aren't being detected.

Usage:
    python debug_detection.py                    # Check all tools
    python debug_detection.py docker             # Check specific tool
    python debug_detection.py docker vscode node # Check multiple tools
"""

import sys
import os
from checkers import check_software, check_software_advanced, AdvancedDetector
from config import STACKS, COMMAND_MAP, VERSION_FLAG, TOOL_TYPE


def print_header(text):
    """Print a formatted header."""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")


def debug_tool(tool_name):
    """
    Debug detection for a specific tool.
    
    Args:
        tool_name (str): Name of tool to debug
    """
    print(f"\n📊 DEBUGGING: {tool_name.upper()}")
    print(f"{'-'*70}")
    
    # Basic detection
    basic_result = check_software(tool_name)
    advanced_result = check_software_advanced(tool_name)
    
    print(f"Basic Detection:     {'✅ FOUND' if basic_result else '❌ NOT FOUND'}")
    print(f"Advanced Detection:  {'✅ FOUND' if advanced_result.binary_found else '❌ NOT FOUND'}")
    
    # Tool info
    tool_type = TOOL_TYPE.get(tool_name, "unknown")
    cmd = COMMAND_MAP.get(tool_name, tool_name)
    version_flags = VERSION_FLAG.get(tool_name, ["--version"])
    
    print(f"\nTool Info:")
    print(f"  - Name: {tool_name}")
    print(f"  - Type: {tool_type}")
    print(f"  - Command: {cmd}")
    print(f"  - Version Flags: {version_flags}")
    
    # Advanced detection strategies
    detector = AdvancedDetector()
    
    print(f"\nDetection Strategies:")
    print(f"  - In PATH: {detector.strategy_path_check(cmd)}")
    print(f"  - Version Check: {detector.strategy_version_check(cmd, version_flags)}")
    
    known_paths = detector.get_common_install_paths()
    print(f"  - Known Paths: {detector.strategy_known_paths(cmd, known_paths)}")
    
    if detector.is_windows:
        print(f"  - Windows Registry: {detector.strategy_windows_registry(tool_name)}")
    
    # OS Info
    print(f"\nSystem Info:")
    print(f"  - Windows: {detector.is_windows}")
    print(f"  - macOS: {detector.is_macos}")
    print(f"  - Linux: {detector.is_linux}")


def debug_all_tools():
    """Debug detection for all tools in all stacks."""
    all_tools = set()
    
    for stack, tools in STACKS.items():
        all_tools.update(tools)
    
    # Sort for consistent output
    all_tools = sorted(list(all_tools))
    
    print_header("FULL SYSTEM DETECTION REPORT")
    
    print(f"Found {len(all_tools)} unique tools across all stacks\n")
    
    found_count = 0
    not_found = []
    
    for tool in all_tools:
        result = check_software_advanced(tool)
        status = "✅" if result.binary_found else "❌"
        print(f"{status} {tool}")
        
        if result.binary_found:
            found_count += 1
        else:
            not_found.append(tool)
    
    # Summary
    print_header("SUMMARY")
    print(f"Total Tools: {len(all_tools)}")
    print(f"Found: {found_count} ({found_count*100//len(all_tools)}%)")
    print(f"Missing: {len(not_found)} ({len(not_found)*100//len(all_tools)}%)")
    
    if not_found:
        print(f"\nMissing Tools:")
        for tool in not_found:
            print(f"  - {tool}")
        print("\nRun 'python debug_detection.py <tool>' for specific debugging")


def debug_stacks():
    """Show status of each stack."""
    print_header("STACK READINESS REPORT")
    
    for stack_name, tools in STACKS.items():
        found = 0
        missing = 0
        
        for tool in tools:
            if check_software_advanced(tool).binary_found:
                found += 1
            else:
                missing += 1
        
        total = len(tools)
        percentage = found * 100 // total
        
        status = "✅" if missing == 0 else "⚠️ " if missing == 1 else "❌"
        
        print(f"{status} {stack_name.upper()}")
        print(f"   {found}/{total} tools ready ({percentage}%)")
        
        if missing > 0:
            missing_tools = [t for t in tools if not check_software_advanced(t).binary_found]
            print(f"   Missing: {', '.join(missing_tools)}")
        print()


def main():
    """Main entry point."""
    args = sys.argv[1:]
    
    if not args:
        # Show menu
        print_header("DETECTION DEBUGGING TOOL")
        print("Usage:")
        print("  python debug_detection.py              # Full report")
        print("  python debug_detection.py stacks       # Stack readiness")
        print("  python debug_detection.py <tool>       # Debug specific tool")
        print("  python debug_detection.py tool1 tool2  # Debug multiple tools\n")
        print("Examples:")
        print("  python debug_detection.py")
        print("  python debug_detection.py docker")
        print("  python debug_detection.py vscode docker node")
        print_header("")
        
        # Run full report
        debug_all_tools()
    
    elif args[0] == 'stacks':
        debug_stacks()
    
    else:
        # Debug specific tools
        print_header("TOOL DETECTION DEBUG")
        
        for tool in args:
            if tool in COMMAND_MAP or tool in TOOL_TYPE:
                debug_tool(tool)
            else:
                print(f"⚠️  Unknown tool: {tool}")
        
        print("\n" + "="*70 + "\n")


if __name__ == '__main__':
    main()
