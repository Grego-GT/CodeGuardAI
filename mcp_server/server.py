"""
Main MCP server exposing CodeGuard AI tools.
"""

import asyncio
import json
from typing import Any, Dict, List
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .code_analysis import scan_pr_changes
from .e2b_executor import E2BExecutor
from .github_integration import GitHubIntegration, format_security_report
from .fix_generator import FixGenerator


# Load configuration
def load_config() -> Dict[str, Any]:
    """Load configuration from config.json."""
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Fallback to environment variables or defaults
        import os
        return {
            'e2b_api_key': os.getenv('E2B_API_KEY', ''),
            'openai_api_key': os.getenv('OPENAI_API_KEY', ''),
            'github_token': os.getenv('GITHUB_TOKEN', ''),
        }


# Initialize components
config = load_config()
github_integration = GitHubIntegration(config.get('github_token'))
e2b_executor = E2BExecutor(config.get('e2b_api_key'))
fix_generator = FixGenerator(config.get('openai_api_key'))

# Create MCP server
server = Server("codeguard-ai")


@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools."""
    return [
        Tool(
            name="scan_pr",
            description="Scan a GitHub pull request for security vulnerabilities",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo_owner": {"type": "string", "description": "Repository owner/org"},
                    "repo_name": {"type": "string", "description": "Repository name"},
                    "pr_number": {"type": "integer", "description": "Pull request number"},
                },
                "required": ["repo_owner", "repo_name", "pr_number"],
            },
        ),
        Tool(
            "scan_and_exploit_pr",
            description="Scan PR for vulnerabilities, prove them with exploits, and generate fixes",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo_owner": {"type": "string"},
                    "repo_name": {"type": "string"},
                    "pr_number": {"type": "integer"},
                    "post_comment": {"type": "boolean", "description": "Post report as PR comment"},
                },
                "required": ["repo_owner", "repo_name", "pr_number"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls."""
    if name == "scan_pr":
        return await handle_scan_pr(arguments)
    elif name == "scan_and_exploit_pr":
        return await handle_scan_and_exploit_pr(arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")


async def handle_scan_pr(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle scan_pr tool call."""
    repo_owner = arguments["repo_owner"]
    repo_name = arguments["repo_name"]
    pr_number = arguments["pr_number"]
    
    # Fetch PR changes
    file_changes = await github_integration.get_pr_files(repo_owner, repo_name, pr_number)
    
    # Scan for vulnerabilities
    vulnerabilities = await scan_pr_changes(file_changes)
    
    result = {
        "vulnerabilities_found": len(vulnerabilities),
        "vulnerabilities": vulnerabilities,
    }
    
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def handle_scan_and_exploit_pr(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle full scan, exploit, and fix generation workflow."""
    repo_owner = arguments["repo_owner"]
    repo_name = arguments["repo_name"]
    pr_number = arguments["pr_number"]
    post_comment = arguments.get("post_comment", False)
    
    # Step 1: Fetch PR changes
    file_changes = await github_integration.get_pr_files(repo_owner, repo_name, pr_number)
    
    # Step 2: Scan for vulnerabilities
    vulnerabilities = await scan_pr_changes(file_changes)
    
    if not vulnerabilities:
        message = "✅ No security vulnerabilities detected in this PR."
        if post_comment:
            await github_integration.post_comment(repo_owner, repo_name, pr_number, message)
        return [TextContent(type="text", text=message)]
    
    # Step 3: Generate and run exploits
    exploits = []
    code_context = {change['file']: change['content'] for change in file_changes}
    
    for i, vuln in enumerate(vulnerabilities):
        try:
            # Generate exploit
            exploit_code = await e2b_executor.generate_exploit(vuln)
            
            # Get vulnerable code context
            file_path = vuln.get('file', '')
            vulnerable_context = code_context.get(file_path, '')
            
            # Run exploit
            exploit_result = await e2b_executor.run_exploit(exploit_code, vulnerable_context)
            exploit_result['vulnerability_id'] = i + 1
            exploits.append(exploit_result)
        except Exception as e:
            exploits.append({
                'vulnerability_id': i + 1,
                'exploit_successful': False,
                'error': str(e),
            })
    
    # Step 4: Generate fixes
    fixes = await fix_generator.generate_fixes_batch(vulnerabilities, code_context)
    
    # Step 5: Format and post report
    report = await github_integration.format_security_report(vulnerabilities, exploits)
    
    # Add fixes to report
    if fixes:
        report += "\n## Suggested Fixes\n\n"
        for fix_data in fixes:
            vuln = fix_data['vulnerability']
            fix = fix_data['fix']
            report += f"### Fix for {vuln.get('type', 'unknown').replace('_', ' ').title()}\n\n"
            report += f"**Fixed Code:**\n```python\n{fix.get('fixed_code', '')}\n```\n\n"
            report += f"**Explanation:**\n{fix.get('explanation', '')}\n\n"
            report += f"**Recommendations:**\n{fix.get('recommendations', '')}\n\n"
    
    if post_comment:
        await github_integration.post_comment(repo_owner, repo_name, pr_number, report)
    
    # Cleanup
    await e2b_executor.cleanup()
    
    return [TextContent(type="text", text=report)]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())

