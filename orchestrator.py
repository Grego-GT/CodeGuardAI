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
        setup_commands = [
            "pip install httpx",  # For GitHub API calls
            "pip install asyncio",  # Async support
        ]

        loop = asyncio.get_event_loop()
        for cmd in setup_commands:
            if log_callback:
                log_callback(f"Running: {cmd}")
            try:
                result = await loop.run_in_executor(None, sandbox.run_code, cmd)
                if log_callback:
                    log_callback(f"✓ {cmd} completed")
            except Exception as e:
                if log_callback:
                    log_callback(f"⚠ Warning: {cmd} failed: {str(e)}")

    async def deploy_agent_to_sandbox(self, sandbox: Sandbox, log_callback: Optional[Callable] = None):
        """Deploy the agent code to the sandbox."""
        if log_callback:
            log_callback("Deploying agent code to sandbox...")

        # Write agent code to sandbox filesystem
        write_code = f"""
with open('agent.py', 'w') as f:
    f.write('''{self.agent_code}''')
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

            # Prepare configuration for agent
            config = {
                'github_token': github_token,
                'mcp_server_url': 'http://host.docker.internal:8080',  # GitHub MCP server
                'repo_owner': repo_owner,
                'repo_name': repo_name,
                'pr_number': pr_number
            }

            config_json = json.dumps(config).replace("'", "\\'")

            # Run the agent
            if log_callback:
                log_callback("🔍 Starting security analysis inside sandbox...")

            run_command = f"""
import subprocess
import sys

# Run agent with config
result = subprocess.run(
    [sys.executable, 'agent.py', '{config_json}'],
    capture_output=True,
    text=True
)

print(result.stdout)
if result.stderr:
    print(result.stderr, file=sys.stderr)
"""

            loop = asyncio.get_event_loop()
            execution = await loop.run_in_executor(None, sandbox.run_code, run_command)

            # Parse output
            output = execution.text if hasattr(execution, 'text') else str(execution)

            if log_callback:
                # Stream logs from agent
                for line in output.split('\n'):
                    if line.strip():
                        log_callback(line)

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
