"""
E2B sandbox integration for safely executing vulnerable code and exploits.
"""

import asyncio
import os
from typing import Dict, List, Optional
from e2b_code_interpreter import Sandbox


class E2BExecutor:
    """Manages E2B sandbox sessions for code execution and exploit testing."""
    
    def __init__(self, api_key: str):
        """
        Initialize E2B executor.
        
        Args:
            api_key: E2B API key
        """
        self.api_key = api_key
        self.sandbox: Optional[Sandbox] = None
        # Set API key as environment variable for E2B SDK
        os.environ['E2B_API_KEY'] = api_key
    
    async def create_sandbox(self) -> None:
        """Create a new E2B sandbox session."""
        # E2B Sandbox.create() is synchronous, so we run it in executor
        loop = asyncio.get_event_loop()
        self.sandbox = await loop.run_in_executor(None, Sandbox.create)
    
    async def execute_code(self, code: str) -> Dict[str, any]:
        """
        Execute code in the sandbox.
        
        Args:
            code: Python code to execute
            
        Returns:
            Dict with execution results, stdout, stderr, and any errors
        """
        if not self.sandbox:
            await self.create_sandbox()
        
        try:
            # Execute code in sandbox (run_code is synchronous)
            loop = asyncio.get_event_loop()
            execution = await loop.run_in_executor(None, self.sandbox.run_code, code)
            
            return {
                'success': True,
                'stdout': execution.text if hasattr(execution, 'text') else str(execution),
                'stderr': '',
                'output': str(execution),
            }
        except Exception as e:
            return {
                'success': False,
                'stdout': '',
                'stderr': str(e),
                'error': str(e),
            }
    
    async def deploy_vulnerable_code(self, code: str) -> Dict[str, any]:
        """
        Deploy vulnerable code to sandbox for testing.
        
        Args:
            code: The vulnerable code to deploy
            
        Returns:
            Execution result dict
        """
        return await self.execute_code(code)
    
    async def run_exploit(self, exploit_code: str, vulnerable_code_context: str = "") -> Dict[str, any]:
        """
        Run an exploit against the deployed vulnerable code.
        
        Args:
            exploit_code: The exploit code to execute
            vulnerable_code_context: Context from previously deployed vulnerable code
            
        Returns:
            Dict with exploit results, including whether it succeeded
        """
        # Combine context and exploit
        full_code = vulnerable_code_context + "\n\n" + exploit_code if vulnerable_code_context else exploit_code
        
        result = await self.execute_code(full_code)
        
        # Determine if exploit was successful
        # This is a simplified check - in reality, you'd analyze the output more carefully
        exploit_success = result['success'] and (
            'error' not in result.get('stderr', '').lower() or
            'exploit' in result.get('stdout', '').lower()
        )
        
        result['exploit_successful'] = exploit_success
        return result
    
    async def generate_exploit(self, vulnerability: Dict[str, any]) -> str:
        """
        Generate exploit code for a given vulnerability.
        
        Args:
            vulnerability: Vulnerability dict with type, code_snippet, etc.
            
        Returns:
            Exploit code as string
        """
        vuln_type = vulnerability.get('type', '')
        code_snippet = vulnerability.get('code_snippet', '')
        
        # Basic exploit templates
        # Note: Double braces {{}} escape f-string interpolation
        exploits = {
            'sql_injection': f"""
# SQL Injection Exploit
# Testing: {code_snippet}
test_input = "'; DROP TABLE users; --"
result = execute_query(f"SELECT * FROM users WHERE id = '{{{{test_input}}}}'")
print(f"Exploit result: {{result}}")
""",
            'xss': f"""
# XSS Exploit
# Testing: {code_snippet}
test_input = "<script>alert('XSS')</script>"
result = render_user_content(test_input)
print(f"Exploit result: {{result}}")
""",
            'command_injection': f"""
# Command Injection Exploit
# Testing: {code_snippet}
test_input = "; cat /etc/passwd"
result = os.system(f"echo {{{{test_input}}}}")
print(f"Exploit result: {{result}}")
""",
        }
        
        return exploits.get(vuln_type, f"# Exploit for {vuln_type}\n# Code: {code_snippet}")
    
    async def cleanup(self) -> None:
        """Clean up sandbox resources."""
        if self.sandbox:
            # E2B Sandbox cleanup - use kill() to terminate the sandbox
            try:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, self.sandbox.kill)
            except Exception:
                pass  # Ignore cleanup errors
            finally:
                self.sandbox = None

