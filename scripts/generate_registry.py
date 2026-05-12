import yaml
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location('old_constants', 'config/constants.py')
old = importlib.util.module_from_spec(spec)
spec.loader.exec_module(old)

stack_tools = [
    'node', 'git', 'vscode', 'react', 'typescript', 'python', 'postman', 'docker',
    'pip', 'ollama', 'fastapi', 'openssl', 'anaconda', 'jupyter', 'pandas', 'numpy',
    'terraform', 'aws-cli', 'kubernetes-cli', 'java', 'android-studio',
    'kotlin-compiler', 'unity', 'blender', 'rust', 'cargo', 'npm', 'yarn'
]

base = Path('registry/tools')
base.mkdir(parents=True, exist_ok=True)

for tool in stack_tools:
    config = {
        'name': tool,
        'command': old.COMMAND_MAP.get(tool, tool),
        'version_flags': old.VERSION_FLAG.get(tool, ['--version']),
        'type': old.TOOL_TYPE.get(tool, 'system'),
    }
    if tool in old.INSTALL_MAP:
        config['install_package'] = old.INSTALL_MAP[tool]
    if tool in old.INSTALL_STRATEGY:
        config['install_strategy'] = old.INSTALL_STRATEGY[tool]
    if tool in old.MINIMUM_VERSION:
        config['minimum_version'] = old.MINIMUM_VERSION[tool]
    if tool in old.VERSIONED_INSTALL:
        config['versioned_install'] = old.VERSIONED_INSTALL[tool]
    if tool in old.DETECTION_RULES:
        config['detection'] = old.DETECTION_RULES[tool]
    else:
        config['detection'] = {
            'executable_names': [tool, f'{tool}.exe'],
            'search_paths': [],
            'registry_names': [tool.capitalize().replace('-', ' ')]
        }
    config = {k: v for k, v in config.items() if v is not None}
    path = base / f'{tool}.yaml'
    print(f'Writing {path}')
    path.write_text(yaml.safe_dump(config, sort_keys=False), encoding='utf-8')
