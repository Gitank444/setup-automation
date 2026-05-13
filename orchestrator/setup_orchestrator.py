"""Main orchestrator for setup automation."""
import time
import threading
import os
import subprocess
from config import STACKS, INSTALL_MAP, INSTALL_STRATEGY, TOOL_TYPE, VERSIONED_INSTALL
from checkers import check_software_advanced
from installers import (
    WingetInstaller, PipInstaller, NpmInstaller, 
    CondaInstaller, ChocolateyInstaller
)
from agents.resolver_agent import ResolverAgent
from agents.failure_agent import FailureAgent
from models import ToolStatus
import signal

class SetupOrchestrator:
    """Orchestrates the entire setup process.

    This class is the central coordinator, responsible for:
    - presenting available stacks to the user
    - detecting tool health and availability
    - selecting installation strategies
    - verifying the result after install attempts
    """
    
    def __init__(self):
        """Initialize the orchestrator with available installers."""
        self.installers = {
            'winget': WingetInstaller(),
            'pip': PipInstaller(),
            'npm': NpmInstaller(), 
            'conda': CondaInstaller(),
            'chocolatey': ChocolateyInstaller()
        }
        self.resolver_agent = ResolverAgent()
        self.failure_agent = FailureAgent()

    def _reload_environment_path(self):
        """
        Reload the PATH environment variable from the system.
        
        After system-level installations (winget, chocolatey), Windows updates
        the registry PATH but Python's os.environ['PATH'] is stale.
        This method refreshes it so subprocess calls can find newly installed tools.
        """
        import sys
        if sys.platform == "win32":
            try:
                import winreg
                # Read from registry (where Windows stores PATH)
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                    r'Environment') as key:
                    user_path, _ = winreg.QueryValueEx(key, 'PATH')
                    os.environ['PATH'] = user_path + os.pathsep + os.environ.get('PATH', '')
                
                # Also get system PATH
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                    r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment') as key:
                    system_path, _ = winreg.QueryValueEx(key, 'PATH')
                    if system_path not in os.environ['PATH']:
                        os.environ['PATH'] = os.environ['PATH'] + os.pathsep + system_path
            except Exception as e:
                print(f"⚠️  Could not reload PATH from registry: {e}")
        else:
            # On Unix-like systems, try to reload from shell
            try:
                result = subprocess.run(
                    ['bash', '-i', '-c', 'echo $PATH'],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if result.returncode == 0:
                    os.environ['PATH'] = result.stdout.strip() + os.pathsep + os.environ.get('PATH', '')
            except:
                pass

    def _get_version_metadata(self, tool):
        return VERSIONED_INSTALL.get(tool)

    def _resolve_package_target(self, tool, version=None):
        package = INSTALL_MAP.get(tool)
        version_metadata = self._get_version_metadata(tool) or {}

        if version and version_metadata:
            version_specific = version_metadata.get("versions", {}).get(version)
            if version_specific:
                return version_specific

        if version and TOOL_TYPE.get(tool) == "python_lib":
            return f"{tool}=={version}"

        if version and TOOL_TYPE.get(tool) == "npm_lib":
            return f"{tool}@{version}"

        return package

    def _get_installer_for_tool(self, tool):
        strategy = INSTALL_STRATEGY.get(tool, "default")
        if strategy == "npm":
            return self.installers['npm']
        if strategy == "conda":
            return self.installers['conda']
        if strategy == "pip":
            return self.installers['pip']
        if strategy == "chocolatey":
            return self.installers['chocolatey']
        return self.installers['winget']

    def _repair_tool(self, tool, version=None):
        print(f"\n🔧 Repairing {tool}...")
        target = self._resolve_package_target(tool, version)
        installer = self._get_installer_for_tool(tool)
        global_install = tool in ["typescript", "yarn"]

        if hasattr(installer, 'uninstall') and target:
            installer.uninstall(target, version=version, global_flag=global_install)

        return self.install_tool(tool, version)

    def _handle_repairs(self, repair_tools):
        if not repair_tools:
            return

        print("\n🛠️ Repair candidates detected:")
        for tool, status in repair_tools:
            print(f"   - {tool}: {status.name}")

        print("\n🔄 Attempting automatic repair for PARTIAL and BROKEN tools...\n")
        
        auto_repaired = []
        for tool, status in repair_tools:
            # Automatically repair PARTIAL and BROKEN tools
            if status.name in ["PARTIAL", "BROKEN", "OUTDATED"]:
                print(f"🔧 Auto-repairing {tool}...")
                version_choice = self._select_install_version(tool)
                if version_choice:
                    print(f"   → Using version: {version_choice}")
                else:
                    print(f"   → Using default version")
                
                success = self._repair_tool(tool, version_choice)
                if success:
                    print(f"✅ {tool} repair completed\n")
                    auto_repaired.append(tool)
                else:
                    print(f"⚠️  {tool} repair encountered issues\n")
            else:
                # For CONFLICT, still ask user
                answer = input(f"\n⚠️  Conflict detected for {tool}. Fix by reinstalling? (y/n): ")
                if answer.strip().lower() == 'y':
                    version_choice = self._select_install_version(tool)
                    self._repair_tool(tool, version_choice)
        
        if auto_repaired:
            print(f"\n✅ Auto-repaired: {', '.join(auto_repaired)}")

    def _offer_installed_version_changes(self, required_tools):
        versioned_installed = []
        for tool in required_tools:
            metadata = self._get_version_metadata(tool)
            if not metadata:
                continue

            signal = check_software_advanced(tool)
            result = self.resolver_agent.resolve(signal)
            if result.status == ToolStatus.INSTALLED and signal.version:
                versioned_installed.append((tool, signal.version))

        if not versioned_installed:
            return

        print("\n✅ Your stack is already installed with these versions:")
        for idx, (tool, version) in enumerate(versioned_installed, start=1):
            print(f"   {idx}. {tool}: {version}")

        choice = input("\nDo you want to install a different version for any of these tools? (y/n): ")
        if choice.strip().lower() != 'y':
            return

        selection = input("Select a tool number to change version, or press Enter to skip: ").strip()
        if not selection:
            return

        if not selection.isdigit() or not (1 <= int(selection) <= len(versioned_installed)):
            print("Invalid selection. Skipping version changes.")
            return

        selected_tool = versioned_installed[int(selection) - 1][0]
        current_version = versioned_installed[int(selection) - 1][1]
        new_version = self._select_install_version(selected_tool)
        if not new_version or new_version == current_version:
            print(f"No change made for {selected_tool}.")
            return

        print(f"\n🔁 Reinstalling {selected_tool} as version {new_version}...")
        self._repair_tool(selected_tool, new_version)

    def _select_install_version(self, tool):
        metadata = self._get_version_metadata(tool)
        if not metadata:
            return None

        versions = list(metadata.get("versions", {}).keys())
        default = metadata.get("default") or (versions[0] if versions else None)
        if not versions:
            return None

        print(f"\n🔢 {tool} version selection")
        print(f"   Default: {default}")

        if len(versions) == 1:
            return default

        for index, version in enumerate(versions, start=1):
            marker = " (default)" if version == default else ""
            print(f"   {index}. {version}{marker}")

        choice = input(f"   Choose version or press Enter to use default [{default}]: ").strip()
        if choice == "":
            return default

        if choice.isdigit():
            selected_index = int(choice) - 1
            if 0 <= selected_index < len(versions):
                return versions[selected_index]

        if choice in versions:
            return choice

        print(f"   Invalid selection, using default {default}.")
        return default

    def _spinner(self, stop_event):
        """Display a spinning animation while installation runs."""
        spinner_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        i = 0
        start_time = time.time()
        while not stop_event.is_set():
            elapsed = time.time() - start_time
            print(f"\r      {spinner_chars[i % len(spinner_chars)]} Installing... ({elapsed:.0f}s elapsed)", end='', flush=True)
            time.sleep(0.1)
            i += 1
        print("\r      ✅ Done" + " " * 30)  # Clear the spinner line
    
    def _print_installation_summary(self, results, total_time):
        """Print a formatted installation summary."""
        print("──────────────────────────────────")
        print("📊 Installation Summary")
        print("──────────────────────────────────")
        
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        for result in results:
            status_icon = "✅" if result['success'] else "❌"
            time_str = f"{result['elapsed']:.1f}s"
            print(f"{status_icon} {result['tool']:<15} {time_str}")
            
            if not result['success']:
                # Add error details for failed installs
                status = result['status']
                print(f"   └─ {status.reason}")
                if status.details and 'path' in status.details:
                    print(f"   └─ 💡 Found at: {status.details['path']}")
        
        print("──────────────────────────────────")
        print(f"Total: {len(successful)} success, {len(failed)} failed | {total_time:.1f}s")
        print("──────────────────────────────────")
    
    def _print_session_summary(self, stack_choice, required_tools, missing_tools):
        """Print a clean session summary at the end."""
        print("\n──────────────────────────────────")
        print("🏁 Session Complete")
        print("──────────────────────────────────")
        
        # Get current status of all tools
        ready_tools = []
        action_tools = []
        
        for tool in required_tools:
            signal = check_software_advanced(tool)
            result = self.resolver_agent.resolve(signal)
            
            if result.status == ToolStatus.INSTALLED:
                ready_tools.append(tool)
            else:
                action_tools.append((tool, result.status.name.lower()))
        
        stack_name = stack_choice.replace("_", " ").upper()
        print(f"Stack    : {stack_name}")
        print(f"Checked  : {len(required_tools)} tools")
        
        if ready_tools:
            ready_str = ", ".join(ready_tools)
            print(f"✅ Ready : {ready_str}")
        
        if action_tools:
            action_str = ", ".join([f"{tool} ({status})" for tool, status in action_tools])
            print(f"⚠️ Action: {action_str}")
        
        print("──────────────────────────────────")
    
    def display_stacks(self):
        """Display available development stacks."""
        stack_names = list(STACKS.keys())
        
        print("\n---  SETUP ORCHESTRATOR ---")
        print("What are you building today?\n")
        
        for index, name in enumerate(stack_names, start=1):
            clean_name = name.replace("_", " ").title()
            print(f"{index}. {clean_name}")
        
        return stack_names
    
    def get_user_choice(self, stack_names):
        """
        Get user's stack choice.
        
        Args:
            stack_names (list): List of available stack names
            
        Returns:
            tuple: (choice, required_tools) or (None, None) if invalid
        """
        try:
            user_input = input("\nSelect what you will build today: ")
            choice_index = int(user_input) - 1
            
            if 0 <= choice_index < len(stack_names):
                choice = stack_names[choice_index]
                required = STACKS[choice]
                print(f"\n✨ You selected: {choice.upper()}\n")
                return choice, required
            else:
                print("❌ Invalid number. Please run the script again.")
                return None, None
        except ValueError:
            print("❌ Please enter a valid number (e.g., 1, 2, 3).")
            return None, None
        
    def check_missing_tools(self, tools):
        actionable_tools = []
        installed_tools = []
        partial_tools = []
        missing_tools = []
        repair_tools = []
        installed_versioned = []

        print("\n🔍 Checking your current setup...\n")

        for tool in tools:
            # Detect the tool and classify its health status.
            signal = check_software_advanced(tool)
            result = self.resolver_agent.resolve(signal)

            # Installed tools are healthy and do not require action.
            if result.status == ToolStatus.INSTALLED:
                print(f"✅ {tool} - INSTALLED")
                installed_tools.append(tool)
                if self._get_version_metadata(tool) and signal.version:
                    installed_versioned.append((tool, signal.version))
                continue

            if result.status == ToolStatus.PARTIAL:
                installer = INSTALL_STRATEGY.get(tool, 'winget')
                recommended = INSTALL_MAP.get(tool, 'Unknown')

                print(f"⚠️  {tool} - PARTIAL")
                print(f"   Status      : PARTIAL")
                print(f"   Binary      : Found")
                print(f"   PATH        : Not Available")
                print(f"   Registry    : Not Checked")
                print(f"   Installer   : {installer}")
                print(f"   Recommended : {recommended}")

                partial_tools.append(tool)
                actionable_tools.append(tool)
                repair_tools.append((tool, result.status))

            elif result.status == ToolStatus.OUTDATED:
                installer = INSTALL_STRATEGY.get(tool, 'winget')
                recommended = INSTALL_MAP.get(tool, 'Unknown')

                print(f"⚠️  {tool} - OUTDATED")
                print(f"   Status      : OUTDATED")
                print(f"   Binary      : Found")
                print(f"   PATH        : Available")
                print(f"   Registry    : Not Checked")
                print(f"   Installer   : {installer}")
                print(f"   Recommended : {recommended}")

                actionable_tools.append(tool)

            elif result.status == ToolStatus.BROKEN:
                installer = INSTALL_STRATEGY.get(tool, 'winget')
                recommended = INSTALL_MAP.get(tool, 'Unknown')

                print(f"❌ {tool} - BROKEN")
                print(f"   Status      : BROKEN")
                print(f"   Binary      : Found")
                print(f"   PATH        : Available")
                print(f"   Registry    : Not Checked")
                print(f"   Installer   : {installer}")
                print(f"   Recommended : {recommended}\n")

                actionable_tools.append(tool)
                repair_tools.append((tool, result.status))

            elif result.status == ToolStatus.CONFLICT:
                installer = INSTALL_STRATEGY.get(tool, 'winget')
                recommended = INSTALL_MAP.get(tool, 'Unknown')

                print(f"⚠️  {tool} - CONFLICT")
                print(f"   Status      : CONFLICT")
                print(f"   Binary      : Found")
                print(f"   PATH        : Available")
                print(f"   Registry    : Not Checked")
                print(f"   Installer   : {installer}")
                print(f"   Recommended : {recommended}\n")

                actionable_tools.append(tool)
                repair_tools.append((tool, result.status))

            else:
                # Structured format for MISSING tools
                installer = INSTALL_STRATEGY.get(tool, 'winget')
                recommended = INSTALL_MAP.get(tool, 'Unknown')

                print(f"❌ {tool} - MISSING")
                print(f"   Status      : MISSING")
                print(f"   Binary      : Not Found")
                print(f"   PATH        : Not Available")
                print(f"   Registry    : Not Checked")
                print(f"   Installer   : {installer}")
                print(f"   Recommended : {recommended}\n")

                missing_tools.append(tool)
                actionable_tools.append(tool)

            for line in self.failure_agent.get_advice(tool, result.status, result.details):
                print(f"   {line}")

        # Summary output helps users understand what the system found.
        print(
            f"\n📊 Summary: {len(installed_tools)} installed, "
            f"{len(partial_tools)} partial, {len(missing_tools)} missing, "
            f"{len(actionable_tools)} actionable"
        )
        return missing_tools, repair_tools, installed_versioned
  
        
    def install_missing_tools(self, missing_tools):
        """
        Install all missing tools.
        
        Args:
            missing_tools (list): List of tools to install
            
        Returns:
            bool: True if all installations successful
        """
        if not missing_tools:
            print("\n🎉 Your environment is already perfect!")
            return True
        
        confirm = input(f"\n🔧 Found {len(missing_tools)} missing tools. Install them? (y/n): ")
        
        if confirm.lower() != 'y':
            print("\n⏭️ Installation skipped.")
            
            print("\n💡 Manual install commands:")
            for tool in missing_tools:
                package = INSTALL_MAP.get(tool)
                if package:
                    print(f"   → {tool}: winget install {package}")
                else:
                    # Fallback to failure agent advice
                    advice = self.failure_agent.get_advice(tool, ToolStatus.MISSING)
                    if advice:
                        print(f"   → {tool}: {advice[0].replace('💡 Run: ', '')}")
            
            print("\n▶️  Run this tool again anytime to install automatically.")
            return True
        
        print("\n🚀 Starting installation process...\n")
        all_successful = True
        failed_tools = []  # Track tools that failed installation
        
        print(f"🚀 Installing {len(missing_tools)} tools...\n")
        
        install_results = []  # Track results for summary
        total_start_time = time.time()
        
        for i, tool in enumerate(missing_tools, 1):
            print(f"[{i}/{len(missing_tools)}] 📥 {tool}")
            start_time = time.time()
            
            # Start spinner in background thread
            stop_spinner = threading.Event()
            spinner_thread = threading.Thread(target=self._spinner, args=(stop_spinner,))
            spinner_thread.daemon = True
            spinner_thread.start()

            version_choice = self._select_install_version(tool)
            if version_choice:
                print(f"   → Installing version: {version_choice}")

            success = self.install_tool(tool, version_choice)
            
            # Stop spinner
            stop_spinner.set()
            spinner_thread.join()
            
            end_time = time.time()
            elapsed = end_time - start_time
            print(f"      ✅ Completed in {elapsed:.1f}s")
            verified = self.verify_installation(tool)
            print(f"\n✓ Process finished for {tool}\n")

            # Re-check status after installation attempt.
            # If the tool remains missing, broken, or otherwise unhealthy, mark it failed.
            signal = check_software_advanced(tool)
            status = self.resolver_agent.resolve(signal)

            final_success = success and verified and status.status == ToolStatus.INSTALLED
            install_results.append({
                'tool': tool,
                'success': final_success,
                'elapsed': elapsed,
                'status': status
            })

            if not final_success:
                all_successful = False
                failed_tools.append(tool)
        
        total_end_time = time.time()
        total_elapsed = total_end_time - total_start_time
        
        # Print installation summary
        self._print_installation_summary(install_results, total_elapsed)
        
        if failed_tools:
            print(f"\n⚠️  {len(failed_tools)} tools failed to install: {', '.join(failed_tools)}")
        
        return all_successful

    def install_tool(self, tool, version=None, max_retries=3):
        """
        Intelligently install a tool using the best available method.
         
        Args:
            tool (str): Tool to install
            version (str|None): Optional version selection
            max_retries (int): Maximum retry attempts
            
        Returns:
            bool: True if installation was successful
        """
        
        package = INSTALL_MAP.get(tool)
        strategy = INSTALL_STRATEGY.get(tool, "default")
        version_metadata = VERSIONED_INSTALL.get(tool, {})

        package_to_install = None
        if version and version_metadata:
            package_to_install = version_metadata.get("versions", {}).get(version)

        if package_to_install is None and version:
            if TOOL_TYPE.get(tool) == "python_lib":
                package_to_install = f"{tool}=={version}"
            elif TOOL_TYPE.get(tool) == "npm_lib":
                package_to_install = f"{tool}@{version}"

        if package_to_install is None:
            package_to_install = package

        # If tool has no package metadata defined, fail gracefully.
        if tool not in INSTALL_MAP:
            print(f"⚠️  No installation metadata found for {tool}. Please add it to config/constants.py.")
            return False

        # Handle tools without a winget package ID: Python and npm libraries.
        if package_to_install is None:
            if TOOL_TYPE.get(tool) == "python_lib":
                install_target = tool
                if version:
                    install_target = f"{tool}=={version}"
                print(f"🐍 Installing {install_target} via pip...")
                installer = self.installers['pip']
                for attempt in range(max_retries):
                    result = installer.install(install_target)
                    if result:
                        return True
                    if attempt < max_retries - 1:
                        print(f"   Retry attempt {attempt + 1}...")
                        time.sleep(2)
                return False

            if TOOL_TYPE.get(tool) == "npm_lib":
                install_target = tool
                if version:
                    install_target = f"{tool}@{version}"
                print(f"📦 Installing {install_target} via npm...")
                installer = self.installers['npm']
                global_install = tool in ["typescript", "yarn"]
                for attempt in range(max_retries):
                    result = installer.install(install_target, global_flag=global_install)
                    if result:
                        return True
                    if attempt < max_retries - 1:
                        print(f"   Retry attempt {attempt + 1}...")
                        time.sleep(2)
                return False

            print(f"⚠️  No installation method defined for {tool}. Please install it manually.")
            return False

        # Use strategy-based installation with retries
        strategies = [strategy] if strategy != "default" else ["winget", "chocolatey"]
        
        for attempt in range(max_retries):
            if strategy == "npm":
                global_install = tool in ["typescript", "yarn"]
                result = self.installers['npm'].install(package_to_install, global_flag=global_install, version=None)
            elif strategy == "conda":
                result = self.installers['conda'].install(package_to_install)
            elif strategy == "pip":
                result = self.installers['pip'].install(package_to_install, version=None)
            elif strategy == "chocolatey":
                result = self.installers['chocolatey'].install(package_to_install)
            else:
                # Default to winget
                result = self.installers['winget'].install(package_to_install, version=version)
            
            if result:
                # Reload environment after successful system install
                if strategy in ["default", "winget", "chocolatey"]:
                    self._reload_environment_path()
                return True
            
            if attempt < max_retries - 1:
                print(f"   ⏳ Retrying installation (attempt {attempt + 2}/{max_retries})...")
                time.sleep(3)
        
        return False
    
    def verify_installation(self, tool, retries=5):
        """
        Verify that a tool was installed successfully.
        
        Args:
            tool (str): Tool to verify
            retries (int): Number of verification attempts
            
        Returns:
            bool: True if tool is ready
        """
        print(f"Verifying {tool}...")
        
        # Reload environment after installation to pick up newly installed tools
        self._reload_environment_path()
        time.sleep(1)  # Give system time to update
        
        for attempt in range(retries):
            signal = check_software_advanced(tool)
            result = self.resolver_agent.resolve(signal)
            if result.status == ToolStatus.INSTALLED:
                print(f"✅ {tool} is now ready")
                return True
            if result.status in (ToolStatus.PARTIAL, ToolStatus.OUTDATED, ToolStatus.BROKEN, ToolStatus.CONFLICT):
                print(f"⚠️  {tool} is detected but not healthy: {result.reason}")
                return False
            time.sleep(1)
        
        print(f"⚠️  {tool} installed but not ready. Manual step may be required.")
        return False
    
    def run(self):
        """Run the complete setup orchestration."""
        # Display available stacks and prompt the user to choose one.
        stack_names = self.display_stacks()
        choice, required = self.get_user_choice(stack_names)
        
        if choice is None:
            return False
        
        # Analyze tool status for the selected stack.
        missing_tools, repair_tools, installed_versioned = self.check_missing_tools(required)
        self._handle_repairs(repair_tools)

        if not missing_tools and not repair_tools:
            self._offer_installed_version_changes(required)
        
        # Attempt installation for any actionable problems.
        success = self.install_missing_tools(missing_tools)
        
        if success and missing_tools:
            print("\n🎉 Setup completed successfully!")
        
        # Print session summary
        self._print_session_summary(choice, required, missing_tools)
        
        return success
