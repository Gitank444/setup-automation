"""Main orchestrator for setup automation."""
import time
import threading
from config import STACKS, INSTALL_MAP, INSTALL_STRATEGY, TOOL_TYPE
from checkers import check_software_advanced
from installers import (
    WingetInstaller, PipInstaller, NpmInstaller, 
    CondaInstaller, ChocolateyInstaller
)
from agents.resolver_agent import ResolverAgent
from agents.failure_agent import FailureAgent
from models.tool_status import ToolStatus
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

        print("\n🔍 Checking your current setup...\n")

        for tool in tools:
            # Detect the tool and classify its health status.
            signal = check_software_advanced(tool)
            result = self.resolver_agent.resolve(signal)

            # Installed tools are healthy and do not require action.
            if result.status == ToolStatus.INSTALLED:
                print(f"✅ {tool} - INSTALLED")
                installed_tools.append(tool)
                continue

            if result.status == ToolStatus.PARTIAL:
                print(f"⚠️  {tool} - PARTIAL")
                print(f"   {result.reason}")
                partial_tools.append(tool)
                actionable_tools.append(tool)

            elif result.status == ToolStatus.OUTDATED:
                print(f"⚠️  {tool} - OUTDATED")
                print(f"   {result.reason}")
                actionable_tools.append(tool)

            elif result.status == ToolStatus.BROKEN:
                print(f"❌ {tool} - BROKEN")
                print(f"   {result.reason}")
                actionable_tools.append(tool)

            elif result.status == ToolStatus.CONFLICT:
                print(f"⚠️  {tool} - CONFLICT")
                print(f"   {result.reason}")
                actionable_tools.append(tool)

            else:
                print(f"❌ {tool} - MISSING")
                print(f"   {result.reason}")
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
        return actionable_tools
  
        
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
            return False
        
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
            
            success = self.install_tool(tool)
            
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
        
        if failed_tools:
            print(f"\n⚠️  {len(failed_tools)} tools failed to install: {', '.join(failed_tools)}")
        
        return all_successful
        
    def install_tool(self, tool):
        """
        Intelligently install a tool using the best available method.
        
        Args:
            tool (str): Tool to install
            
        Returns:
            bool: True if installation was successful
        """
        
        package = INSTALL_MAP.get(tool)
        strategy = INSTALL_STRATEGY.get(tool, "default")

        # If tool has no package metadata defined, fail gracefully.
        # This prevents a KeyError for tools that are added to a stack but not to the install map.
        if tool not in INSTALL_MAP:
            print(f"⚠️  No installation metadata found for {tool}. Please add it to config/constants.py.")
            return False

        # Handle tools without a winget package ID: Python and npm libraries.
        if package is None:
            if TOOL_TYPE.get(tool) == "python_lib":
                print(f"🐍 Installing {tool} via pip...")
                installer = self.installers['pip']
                return installer.install(tool)

            if TOOL_TYPE.get(tool) == "npm_lib":
                print(f"📦 Installing {tool} via npm...")
                installer = self.installers['npm']
                global_install = tool in ["typescript", "yarn"]
                return installer.install(tool, global_flag=global_install)

            print(f"⚠️  No installation method defined for {tool}. Please install it manually.")
            return False
        
        # Use strategy-based installation
        if strategy == "npm":
            return self.installers['npm'].install(tool)
        elif strategy == "conda":
            return self.installers['conda'].install(tool)
        elif strategy == "pip":
            return self.installers['pip'].install(tool)
        elif strategy == "chocolatey":
            return self.installers['chocolatey'].install(tool)
        else:
            # Default to winget
            return self.installers['winget'].install(package)
    
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
        missing_tools = self.check_missing_tools(required)
        
        # Attempt installation for any actionable problems.
        success = self.install_missing_tools(missing_tools)
        
        if success and missing_tools:
            print("\n🎉 Setup completed successfully!")
        
        # Print session summary
        self._print_session_summary(choice, required, missing_tools)
        
        return success
