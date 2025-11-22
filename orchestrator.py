"""
Orchestrator that launches the security agent inside E2B sandboxes.
Bridges between Streamlit dashboard and sandbox-native agent.
"""

import asyncio
import json
import os
from typing import Dict, Any, Optional, Callable
from e2b_code_interpreter import Sandbox


class SandboxOrchestrator:
    """Manages E2B sandbox lifecycle and agent execution."""

    def __init__(self, e2b_api_key: str):
        self.e2b_api_key = e2b_api_key
        os.environ['E2B_API_KEY'] = e2b_api_key
        self.sandbox: Optional[Sandbox] = None
        self.agent_code: Optional[str] = None

    async def initialize(self):
        """Initialize the orchestrator by loading agent code."""
        # Load the agent code that will run inside sandbox
        with open('sandbox_agent/agent.py', 'r') as f:
            self.agent_code = f.read()

    async def create_sandbox(self) -> Sandbox:
        """Create a new E2B sandbox."""
        loop = asyncio.get_event_loop()
        sandbox = await loop.run_in_executor(None, Sandbox.create)
        return sandbox

    async def setup_sandbox_environment(self, sandbox: Sandbox, log_callback: Optional[Callable] = None):
        """Install required dependencies inside the sandbox."""
        if log_callback:
            log_callback("Setting up sandbox environment...")

        # Install required packages inside sandbox
        # sandbox.run_code() expects Python code, so we need to use subprocess
        # asyncio is built-in, so we don't need to install it
        install_code = """
import subprocess
import sys

# Install httpx using pip
result = subprocess.run(
    [sys.executable, '-m', 'pip', 'install', 'httpx'],
    capture_output=True,
    text=True
)

if result.returncode != 0:
    print(f"Error installing httpx: {result.stderr}")
    sys.exit(1)
else:
    print("✓ httpx installed successfully")
"""

        loop = asyncio.get_event_loop()
        if log_callback:
            log_callback("Running: pip install httpx")
        try:
            result = await loop.run_in_executor(None, sandbox.run_code, install_code)
            # Check if installation was successful
            if result.error:
                error_msg = f"Failed to install package: {result.error}"
                if log_callback:
                    log_callback(f"❌ {error_msg}")
                raise Exception(error_msg)
            if log_callback:
                log_callback("✓ pip install httpx completed")
        except Exception as e:
            if log_callback:
                log_callback(f"❌ Error: pip install httpx failed: {str(e)}")
            raise

        # Verify httpx is installed
        if log_callback:
            log_callback("Verifying httpx installation...")
        verify_code = """
import sys
try:
    import httpx
    print(f"✓ httpx version {httpx.__version__} is installed")
except ImportError as e:
    print(f"❌ httpx is not available: {e}")
    sys.exit(1)
"""
        try:
            result = await loop.run_in_executor(None, sandbox.run_code, verify_code)
            # Check for errors first
            if result.error:
                raise Exception(f"httpx verification failed: {result.error}")
            # Check output text if available
            result_text = getattr(result, 'text', None) or getattr(result, 'output', None) or ''
            if result_text and '❌' in result_text:
                raise Exception("httpx verification failed - httpx not available")
            if log_callback:
                log_callback("✓ httpx verified")
        except Exception as e:
            if log_callback:
                log_callback(f"❌ Verification failed: {str(e)}")
            raise

    async def deploy_agent_to_sandbox(self, sandbox: Sandbox, log_callback: Optional[Callable] = None):
        """Deploy the agent code to the sandbox."""
        if log_callback:
            log_callback("Deploying agent code to sandbox...")

        # Write agent code to sandbox filesystem using repr() to properly escape the string
        # This ensures all quotes, newlines, and special characters are handled correctly
        agent_code_escaped = repr(self.agent_code)
        write_code = f"""
with open('agent.py', 'w', encoding='utf-8') as f:
    f.write({agent_code_escaped})
print('Agent code deployed successfully')
"""

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, sandbox.run_code, write_code)

        if log_callback:
            log_callback("✓ Agent code deployed")

    async def run_agent(
        self,
        repo_owner: str,
        repo_name: str,
        pr_number: int,
        github_token: str,
        log_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Run the security agent inside E2B sandbox.

        Args:
            repo_owner: GitHub repository owner
            repo_name: GitHub repository name
            pr_number: Pull request number
            github_token: GitHub personal access token
            log_callback: Optional callback for streaming logs

        Returns:
            Analysis results from the agent
        """
        sandbox = None
        try:
            # Create sandbox
            if log_callback:
                log_callback("🚀 Creating E2B sandbox...")
            sandbox = await self.create_sandbox()
            if log_callback:
                log_callback("✓ Sandbox created")

            # Setup environment
            await self.setup_sandbox_environment(sandbox, log_callback)

            # Deploy agent code
            await self.deploy_agent_to_sandbox(sandbox, log_callback)

            # Load MCP server URL from config file
            import json as json_lib
            try:
                with open('config.json', 'r') as f:
                    app_config = json_lib.load(f)
                    mcp_url = app_config.get('mcp', {}).get('server_url', 'http://localhost:8080')
            except Exception:
                mcp_url = 'http://localhost:8080'

            # Prepare configuration for agent
            config = {
                'github_token': github_token,
                'mcp_server_url': mcp_url,
                'repo_owner': repo_owner,
                'repo_name': repo_name,
                'pr_number': pr_number
            }

            config_json = json.dumps(config).replace("'", "\\'")

            # Run the agent
            if log_callback:
                log_callback("🔍 Starting security analysis inside sandbox...")

            # Write config to a file in the sandbox for easier handling
            config_write = f"""
import json
config = {json.dumps(config)}
with open('agent_config.json', 'w') as f:
    json.dump(config, f)
print('Config written')
"""
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, sandbox.run_code, config_write)

            # Prepare callback for streaming logs
            log_buffer = []

            def on_stdout_callback(msg):
                line = msg.line if hasattr(msg, 'line') else str(msg)
                log_buffer.append(line)
                if log_callback:
                    log_callback(line)

            def on_stderr_callback(msg):
                line = msg.line if hasattr(msg, 'line') else str(msg)
                log_buffer.append(f"[STDERR] {line}")
                if log_callback:
                    log_callback(f"⚠️ {line}")

            # Run the agent using the config file
            # First verify environment, then run agent
            run_command = """
import subprocess
import sys
import json
import os

# Verify Python environment
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Python path: {sys.path[:3]}")

# Verify httpx is available
try:
    import httpx
    print(f"✓ httpx is available: {httpx.__version__}")
except ImportError as e:
    print(f"❌ httpx import failed: {e}")
    # Try to install it again
    print("Attempting to install httpx...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'httpx'], check=True)
    import httpx
    print(f"✓ httpx installed: {httpx.__version__}")

# Read config from file
with open('agent_config.json', 'r') as f:
    config_str = f.read()

# Run agent with config
result = subprocess.run(
    [sys.executable, 'agent.py', config_str],
    capture_output=True,
    text=True
)

print('=== STDOUT ===')
print(result.stdout if result.stdout else 'No stdout')
print('=== STDERR ===')
print(result.stderr if result.stderr else 'No stderr')
print('=== RETURN CODE ===')
print(result.returncode)
"""

            # Run with callbacks for streaming output
            execution = await loop.run_in_executor(
                None,
                lambda: sandbox.run_code(
                    run_command,
                    on_stdout=on_stdout_callback,
                    on_stderr=on_stderr_callback
                )
            )

            # Parse output from E2B execution object
            # Check for errors first
            if execution.error:
                error_msg = f"Sandbox execution error: {execution.error}"
                if log_callback:
                    log_callback(f"❌ {error_msg}")
                raise Exception(error_msg)

            # Get text output from execution or use buffered logs
            output = execution.text if hasattr(execution, 'text') and execution.text else None

            if not output and log_buffer:
                # Use the buffered logs from callbacks
                output = '\n'.join(log_buffer)

            if not output:
                raise Exception("No output received from sandbox execution. The agent may have failed to run.")

            # Extract result JSON from output
            result = self._extract_result(output)

            if log_callback:
                log_callback("✅ Analysis complete!")

            return result

        except Exception as e:
            if log_callback:
                log_callback(f"❌ Error: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'logs': []
            }

        finally:
            # Cleanup sandbox
            if sandbox:
                try:
                    if log_callback:
                        log_callback("🧹 Cleaning up sandbox...")
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(None, sandbox.kill)
                except Exception:
                    pass

    def _extract_result(self, output: str) -> Dict[str, Any]:
        """Extract JSON result from agent output."""
        try:
            # Look for result between markers
            start_marker = "=== AGENT_RESULT ==="
            end_marker = "=== END_RESULT ==="

            if start_marker in output and end_marker in output:
                start_idx = output.index(start_marker) + len(start_marker)
                end_idx = output.index(end_marker)
                result_json = output[start_idx:end_idx].strip()
                return json.loads(result_json)
            else:
                # Fallback: return output as-is
                return {
                    'status': 'success',
                    'output': output,
                    'logs': output.split('\n')
                }
        except Exception as e:
            return {
                'status': 'error',
                'error': f'Failed to parse result: {str(e)}',
                'output': output
            }


async def main():
    """Test the orchestrator locally."""
    import sys

    if len(sys.argv) < 5:
        print("Usage: python orchestrator.py <repo_owner> <repo_name> <pr_number> <github_token>")
        sys.exit(1)

    repo_owner = sys.argv[1]
    repo_name = sys.argv[2]
    pr_number = int(sys.argv[3])
    github_token = sys.argv[4]

    # Load E2B API key from config
    with open('config.json', 'r') as f:
        config = json.load(f)

    orchestrator = SandboxOrchestrator(config['e2b_api_key'])
    await orchestrator.initialize()

    def log_callback(message: str):
        print(f"[ORCHESTRATOR] {message}")

    result = await orchestrator.run_agent(
        repo_owner,
        repo_name,
        pr_number,
        github_token,
        log_callback
    )

    print("\n" + "="*50)
    print("FINAL RESULT:")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
