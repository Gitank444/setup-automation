"""Global constants for the setup automation system."""

from pathlib import Path
import yaml

REGISTRY_ROOT = Path(__file__).resolve().parent.parent / "registry"
TOOLS_REGISTRY = REGISTRY_ROOT / "tools"
STRATEGIES_REGISTRY = REGISTRY_ROOT / "strategies"


def _load_yaml(path):
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def _load_tool_configs():
    configs = {}
    for tool_file in sorted(TOOLS_REGISTRY.glob("*.yaml")):
        tool_data = _load_yaml(tool_file)
        tool_key = tool_data.get("name", tool_file.stem)
        configs[tool_key] = tool_data
    return configs


def _load_strategy_config(name):
    return _load_yaml(STRATEGIES_REGISTRY / f"{name}.yaml")


TOOL_CONFIGS = _load_tool_configs()
DETECTION_STRATEGY = _load_strategy_config("detection")
INSTALLATION_STRATEGY = _load_strategy_config("installation")

COMMAND_MAP = {
    tool: config.get("command", tool)
    for tool, config in TOOL_CONFIGS.items()
}

VERSION_FLAG = {
    tool: config.get("version_flags", ["--version"])
    for tool, config in TOOL_CONFIGS.items()
}

TOOL_TYPE = {
    tool: config.get("type", "system")
    for tool, config in TOOL_CONFIGS.items()
}

INSTALL_MAP = {
    tool: config["install_package"]
    for tool, config in TOOL_CONFIGS.items()
    if config.get("install_package") is not None
}

MINIMUM_VERSION = {
    tool: config["minimum_version"]
    for tool, config in TOOL_CONFIGS.items()
    if config.get("minimum_version") is not None
}

VERSIONED_INSTALL = {
    tool: config["versioned_install"]
    for tool, config in TOOL_CONFIGS.items()
    if config.get("versioned_install") is not None
}

# Add optional strategy-defined versioned install metadata after tool-specific configs.
VERSIONED_INSTALL = {
    **INSTALLATION_STRATEGY.get("versioned_install", {}),
    **VERSIONED_INSTALL,
}

INSTALL_STRATEGY = {
    tool: config.get(
        "install_strategy",
        INSTALLATION_STRATEGY.get("install_strategy", {}).get(tool, "default"),
    )
    for tool, config in TOOL_CONFIGS.items()
}

DETECTION_RULES = {
    tool: config.get("detection", {})
    for tool, config in TOOL_CONFIGS.items()
}
