"""Global constants for the setup automation system."""

# Maps tool names to their CLI commands
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

# Version check flags for each tool
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

# Minimum supported versions used for status classification
MINIMUM_VERSION = {
    "python": "3.11.0",
    "git": "2.40.0",
    "vscode": "1.80.0",
    "node": "18.0.0",
    "docker": "24.0.0",
    "blender": "4.0.0",
    "unity": "2023.1.0",
    "pip": "23.0.0",
    "npm": "9.0.0",
    "yarn": "1.22.0",
    "rust": "1.70.0",
}

# Categorizes tools by type
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

# Winget package IDs for installation
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
    "fastapi": None,  # pip install fastapi
    "openssl": "ShiningLight.OpenSSL",

    # --- Data Science ---
    "anaconda": "Anaconda.Anaconda3",
    "jupyter": None,  # pip install notebook
    "pandas": None,  # pip install pandas
    "numpy": None,  # pip install numpy

    # --- Cloud Engineer ---
    "terraform": "Hashicorp.Terraform",
    "aws-cli": "Amazon.AWSCLI",
    "kubernetes-cli": "Kubernetes.kubectl",

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

# Installation strategy for each tool
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

# Tool categories by automation level
TOOL_CATEGORY = {
    "docker": "fully_automated",
    "pandas": "fully_automated",
    "mingw": "semi_automated",
    "android_studio": "gui_heavy",
    "vscode_extension": "tool_plugin"
}
