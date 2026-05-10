import subprocess
import sys
import time

COMMAND_MAP = {
    "aws-cli": "aws",
    "kubernetes-cli": "kubectl",
    "node": "node",
    "docker": "docker",
    "terraform": "terraform",
    "java": "java",
    "git": "git",
    "vscode": "code",
    "python": "python",
    "pip": "pip",
    "anaconda": "conda",
    "jupyter": "jupyter",
    "postman": "postman",
    "openssl": "openssl",
    "android-studio": "studio64",
    "kotlin-compiler": "kotlinc",
    "npm": "npm",
    "yarn": "yarn",
    "rust": "rustc",
    "cargo": "cargo",
    "react": "npx",
    "typescript": "tsc",
    "unity": "unity",
    "blender": "blender",
    "numpy": "python",
}

VERSION_FLAG = {
    "kubernetes-cli": ["version", "--client"],
    "aws-cli": ["--version"],
    "terraform": ["--version"],
    "docker": ["--version"],
    "node": ["--version"],
    "java": ["--version"],
    "git": ["--version"],
    "vscode": ["--version"],
    "python": ["--version"],
    "pip": ["--version"],
    "anaconda": ["--version"],
    "jupyter": ["--version"],
    "postman": ["--version"],
    "openssl": ["version"],
    "android-studio": ["--version"],
    "kotlin-compiler": ["-version"],
    "npm": ["--version"],
    "yarn": ["--version"],
    "rust": ["--version"],
    "cargo": ["--version"],
    "typescript": ["--version"],
    "unity": ["--version"],
    "blender": ["--version"],
}

TOOL_TYPE = {
    "docker": "system",
    "node": "system",
    "git": "system",
    "vscode": "system",
    "python": "system",
    "pip": "system",
    "anaconda": "system",
    "jupyter": "python_lib",
    "fastapi": "python_lib",
    "pandas": "python_lib",
    "numpy": "python_lib",
    "aws-cli": "system",
    "kubernetes-cli": "system",
    "terraform": "system",
    "java": "system",
    "postman": "system",
    "openssl": "system",
    "android-studio": "system",
    "kotlin-compiler": "system",
    "ollama": "system",
    "npm": "system",
    "yarn": "system",
    "react": "npm_lib",
    "typescript": "npm_lib",
    "rust": "system",
    "cargo": "system",
    "unity": "system",
    "blender": "system"
}

def check_system_tool(cmd):
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
    tool_type = TOOL_TYPE.get(tool)

    if tool_type == "system":
        cmd = COMMAND_MAP.get(tool, tool)
        return check_system_tool(cmd)

    elif tool_type == "python_lib":
        return check_python_lib(tool)

    cmd = COMMAND_MAP.get(tool, tool)
    return check_system_tool(cmd)
    
# The "Recipe Book"
STACKS = {
    "webdev": ["node", "git", "vscode"],
    "frontend": ["node", "git", "vscode", "react", "typescript"],
    "backend_dev": ["python", "postman", "docker", "git", "vscode"],
    "ml_dev": ["python", "pip", "ollama", "docker"],
    "backend_security": ["python", "fastapi", "postman", "openssl"],
    "data_science": ["python", "anaconda", "jupyter", "pandas", "numpy"],
    "cloud_engineer": ["terraform", "aws-cli", "docker", "kubernetes-cli"],
    "devops": ["docker", "kubernetes-cli", "terraform", "git", "vscode"],
    "android_dev": ["java", "android-studio", "kotlin-compiler"],
    "python_dev": ["python", "git", "vscode", "pip"],
    "game_dev": ["unity", "blender", "git", "vscode"],
    "rust_dev": ["rust", "cargo", "git", "vscode"],
    "nodejs_dev": ["node", "git", "vscode", "npm", "yarn"],
}

def start_orchestrator():
    choice = input("\nWhat are you building today? (Options: webdev, ml_dev, java_dev,cloud_engineer, android_dev): ").lower()
    
    if choice in STACKS:
        tools_needed = STACKS[choice]
        print(f"\n🚀 Planning setup for {choice.upper()}...")
        
        # This is where we will loop through the tools and check them
        for tool in tools_needed:
            # We reuse your check_software function here!
            if check_software(tool):
                 print(f"{tool} is already there.")
            else:
                 print(f" {tool} is MISSING and needs to be installed.")
    else:
        print("I don't have a recipe for that stack yet.")
        
    print("\n--- ACTION PLAN ---")
    print("I will attempt to install the missing tools listed above.")
    confirm = input("Do you want to proceed with the installation? (y/proceed with the installation? (y/n): ")
        
    if confirm.lower() == 'y':
            print("🛠️ Starting installation process...")
            # We will build the installer next!
    else:
            print(" Setup cancelled by user.")    
        
# 1. Get a list of the stack names
stack_names = list(STACKS.keys())

print("\n---  SETUP ORCHESTRATOR ---")
print("What are you building today?\n")

# 2. Display the numbered menu
for index, name in enumerate(stack_names, start=1):
    # This turns "web_dev" into "1. Web Dev"
    clean_name = name.replace("_", " ").title()
    print(f"{index}. {clean_name}")

# 3. Get the user's number choice
try:
    
    user_input = input("\nSelect what you will build today: ")
    choice_index = int(user_input) - 1  # Subtract 1 because lists start at 0
    
    if 0 <= choice_index < len(stack_names):
        choice = stack_names[choice_index]
        required = STACKS[choice]
        print(f"\n✨ You selected: {choice.upper()}\n")
    else:
        print("❌ Invalid number. Please run the script again.")
        exit()
except ValueError:
    print("❌ Please enter a valid number (e.g., 1, 2, 3).")
    exit()


# Package installation mapping for all tools
INSTALL_MAP = {
    # --- Web Dev ---
    "node": "OpenJS.NodeJS",
    "git": "Git.Git",
    "vscode": "Microsoft.VisualStudioCode",

    # --- Frontend ---
    "react": None,  # npm install react
    "typescript": None,  # npm install -g typescript

    # --- Backend Dev ---
    "docker": "Docker.DockerDesktop",
    "postman": "Postman.Postman",

    # --- ML Dev ---
    "python": "Python.Python.3.11",
    "pip": None,  # Comes with Python
    "ollama": "Ollama.Ollama",

    # --- Backend Security ---
    "fastapi": None,   # pip install fastapi
    "openssl": "ShiningLight.OpenSSL",

    # --- Data Science ---
    "anaconda": "Anaconda.Anaconda3",
    "jupyter": None,   # pip install notebook
    "pandas": None,    # pip install pandas
    "numpy": None,     # pip install numpy

    # --- Cloud Engineer ---
    "terraform": "Hashicorp.Terraform",
    "aws-cli": "Amazon.AWSCLI",
    "kubernetes-cli": "Kubernetes.kubectl",

    # --- DevOps ---
    # (Same as cloud_engineer)

    # --- Android Dev ---
    "java": "Oracle.JDK.17",
    "android-studio": "Google.AndroidStudio",
    "kotlin-compiler": "JetBrains.Kotlin",

    # --- Node.js Dev ---
    "npm": None,  # Comes with Node.js
    "yarn": None,  # npm install -g yarn

    # --- Rust Dev ---
    "rust": "Rustlang.Rust.MSVC",
    "cargo": None,  # Comes with Rust

    # --- Game Dev ---
    "unity": "Unity.Hub",
    "blender": "BlenderFoundation.Blender"
}

def install_npm(package, global_flag=False):
    """Install npm packages globally or locally"""
    cmd = [
        "npm",
        "install",
        package
    ]
    
    if global_flag:
        cmd.insert(2, "-g")
    
    print(f"\n📦 Installing {package} via npm...")
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    print(result.stdout)

    if result.returncode == 0:
        print(f"✅ {package} installed via npm")
        return True

    print(f"❌ Failed installing {package} via npm")
    print(result.stderr)
    return False


def install_conda(package):
    """Install packages using conda (Anaconda)"""
    cmd = [
        "conda",
        "install",
        "-y",
        package
    ]
    
    print(f"\n📦 Installing {package} via conda...")
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    print(result.stdout)

    if result.returncode == 0:
        print(f"✅ {package} installed via conda")
        return True

    print(f"❌ Failed installing {package} via conda")
    print(result.stderr)
    return False


def install_chocolatey(package):
    """Install packages using Chocolatey"""
    # First check if chocolatey is installed
    try:
        subprocess.run(
            ["choco", "--version"],
            capture_output=True,
            check=True
        )
    except:
        print("⚠️  Chocolatey not installed. Installing Chocolatey first...")
        print("Please run PowerShell as Administrator and execute:")
        print('Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString("https://community.chocolatey.org/install.ps1"))')
        return False
    
    cmd = [
        "choco",
        "install",
        "-y",
        package
    ]
    
    print(f"\n📦 Installing {package} via Chocolatey...")
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    print(result.stdout)

    if result.returncode == 0:
        print(f"✅ {package} installed via Chocolatey")
        return True

    print(f"❌ Failed installing {package} via Chocolatey")
    print(result.stderr)
    return False


INSTALL_STRATEGY = {
    "docker": "winget",
    "pandas": "pip",
    "react": "npm",
    "typescript": "npm",
    "yarn": "npm",
    "numpy": "conda",  # Can use conda or pip
    "vscode_cpp_extension": "vscode_extension",
    "mingw": "manual_or_custom"
}
def install_winget(package, retries=2):
    """Install packages using Windows Package Manager (winget)"""
    cmd = [
        "winget",
        "install",
        "--id", package,
        "-e",
        "--accept-package-agreements",
        "--accept-source-agreements"
    ]

    for attempt in range(retries):

        print(f"\n📥 Installing {package} via winget (Attempt {attempt+1}/{retries})")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        print("\n--- STDOUT ---")
        print(result.stdout)

        if result.stderr:
            print("\n--- STDERR ---")
            print(result.stderr)

        if result.returncode == 0:
            print(f"\n✅ {package} installed successfully via winget")
            return True

        print(f"\n⚠️  Attempt failed for {package}")
        time.sleep(3)

    print(f"\n❌ Installation failed for {package} after {retries} attempts")
    return False


def install_pip(package):
    """Install Python packages using pip"""
    cmd = [
        sys.executable,
        "-m",
        "pip",
        "install",
        package
    ]

    print(f"\n🐍 Installing {package} via pip...")

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    print(result.stdout)

    if result.returncode == 0:
        print(f"✅ {package} installed via pip")
        return True

    print(f"❌ Failed installing {package} via pip")
    print(result.stderr)

    return False

def install_software(tool):
    """Smart installer that chooses the best installation method"""
    if tool not in INSTALL_MAP:
        print(f"⚠️  No installation method defined for {tool}. Please install it manually.")
        return False
    
    package = INSTALL_MAP[tool]
    strategy = INSTALL_STRATEGY.get(tool, "default")
    
    # Check if it's a Python library
    if package is None:
        if TOOL_TYPE.get(tool) == "python_lib":
            print(f"🐍 Installing {tool} via pip...")
            return install_pip(tool)
        
        # Check if it's an npm library
        if TOOL_TYPE.get(tool) == "npm_lib":
            print(f"📦 Installing {tool} via npm...")
            global_install = tool in ["typescript", "yarn"]
            return install_npm(tool, global_flag=global_install)
        
        print(f"⚠️  No installation method defined for {tool}. Please install it manually.")
        return False
    
    # Use strategy-based installation
    if strategy == "npm":
        return install_npm(tool)
    elif strategy == "conda":
        return install_conda(tool)
    elif strategy == "pip":
        return install_pip(tool)
    else:
        # Default to winget
        return install_winget(package)

# --- STEP 1: Identify what is missing ---
print(f"--- Blueprint for {choice.upper()} ---\n")
missing_tools = []
for item in required:
    if check_software(item):
        print(f"✅ {item}: INSTALLED")
    else:
        print(f"❌ {item}: MISSING")
        missing_tools.append(item)

# --- STEP 2: The "Decision Gate" ---
if not missing_tools:
    print("\n🎉 Your environment is already perfect!")
else:
    confirm = input(f"\n🔧 Found {len(missing_tools)} missing tools. Install them? (y/n): ")
    
    if confirm.lower() == 'y':
        # --- STEP 3: The Execution Loop ---
        print("\n🚀 Starting installation process...\n")
        for tool in missing_tools:
            install_software(tool) # This calls your smart INSTALL_MAP function
            print(f"\n✓ Process finished for {tool}\n")
    else:
        print("⏭️  Installation aborted.")
        
def install_and_verify(tool):
    install_software(tool)
    
    print(f"Verifying {tool}...")
    
    for _ in range(5):  # retry logic
        if check_software(tool):
            print(f" {tool} is now ready")
            return
        time.sleep(3)
    
    print(f" {tool} installed but not ready. Manual step may be required.")        
    

TOOL_CATEGORY = {
    "docker": "fully_automated",
    "pandas": "fully_automated",
    "mingw": "semi_automated",
    "android_studio": "gui_heavy",
    "vscode_extension": "tool_plugin"
}    
def check_vscode_cli():

    try:
        subprocess.run(
            ["code", "--version"],
            capture_output=True,
            check=True
        )

        return True

    except:
        return False

def install_vscode_extension(extension):

    if not check_vscode_cli():

        print(" VSCode CLI not enabled")

        print("""
Manual Step:
1. Open VSCode
2. Press CTRL + SHIFT + P
3. Type:
   Shell Command: Install 'code' command in PATH
        """)

        return False

    result = subprocess.run(
        ["code", "--install-extension", extension],
        capture_output=True,
        text=True
    )

    print(result.stdout)

    if result.returncode == 0:
        print(f"Extension installed: {extension}")
        return True

    print(result.stderr)
    return False