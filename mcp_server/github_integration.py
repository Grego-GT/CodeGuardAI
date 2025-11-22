"""
GitHub MCP integration for fetching PR code changes.
"""

from typing import List, Dict, Optional
import httpx


class GitHubIntegration:
    """Handles GitHub API interactions via MCP server."""
    
    def __init__(self, github_token: Optional[str] = None):
        """
        Initialize GitHub integration.
        
        Args:
            github_token: Optional GitHub personal access token
        """
        self.github_token = github_token
        self.base_url = "https://api.github.com"
        self.headers = {}
        if github_token:
            self.headers["Authorization"] = f"token {github_token}"
    
    async def get_pr_files(self, repo_owner: str, repo_name: str, pr_number: int) -> List[Dict]:
        """
        Fetch changed files from a GitHub PR.
        
        Args:
            repo_owner: Repository owner/org
            repo_name: Repository name
            pr_number: Pull request number
            
        Returns:
            List of file change dicts with 'file', 'content', 'status' (added/modified/deleted)
        """
        # This would typically use MCP server, but for MVP we'll use direct API
        async with httpx.AsyncClient() as client:
            # Get PR files
            url = f"{self.base_url}/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/files"
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            
            files_data = response.json()
            file_changes = []
            
            for file_info in files_data:
                file_path = file_info['filename']
                status = file_info['status']  # added, modified, removed
                
                # Skip deleted files
                if status == 'removed':
                    continue
                
                # Get file content
                content = ""
                if 'patch' in file_info:
                    # Extract added lines from patch
                    patch = file_info['patch']
                    # For MVP, we'll use the patch content
                    # In production, fetch full file content
                    content = patch
                else:
                    # Fetch full file content
                    contents_url = file_info.get('contents_url', '').replace('{+path}', file_path)
                    try:
                        content_response = await client.get(contents_url, headers=self.headers)
                        if content_response.status_code == 200:
                            content_data = content_response.json()
                            import base64
                            content = base64.b64decode(content_data['content']).decode('utf-8')
                    except Exception:
                        pass
                
                file_changes.append({
                    'file': file_path,
                    'content': content,
                    'status': status,
                    'additions': file_info.get('additions', 0),
                    'deletions': file_info.get('deletions', 0),
                })
            
            return file_changes
    
    async def post_comment(self, repo_owner: str, repo_name: str, pr_number: int, comment: str) -> bool:
        """
        Post a comment to a GitHub PR.
        
        Args:
            repo_owner: Repository owner/org
            repo_name: Repository name
            pr_number: Pull request number
            comment: Comment body (supports Markdown)
            
        Returns:
            True if successful
        """
        async with httpx.AsyncClient() as client:
            url = f"{self.base_url}/repos/{repo_owner}/{repo_name}/issues/{pr_number}/comments"
            payload = {"body": comment}
            response = await client.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return True
    
    async def format_security_report(self, vulnerabilities: List[Dict], exploits: List[Dict]) -> str:
        """
        Format vulnerabilities and exploit results into a Markdown security report.
        
        Args:
            vulnerabilities: List of vulnerability findings
            exploits: List of exploit execution results
            
        Returns:
            Formatted Markdown report
        """
        report = "# 🔒 CodeGuard AI Security Report\n\n"
        
        if not vulnerabilities:
            report += "✅ No security vulnerabilities detected.\n"
            return report
        
        report += f"## Summary\n\n"
        report += f"Found **{len(vulnerabilities)}** potential security vulnerability/vulnerabilities.\n\n"
        
        # Group by severity
        by_severity = {}
        for vuln in vulnerabilities:
            severity = vuln.get('severity', 'medium')
            if severity not in by_severity:
                by_severity[severity] = []
            by_severity[severity].append(vuln)
        
        for severity in ['critical', 'high', 'medium', 'low']:
            if severity in by_severity:
                report += f"\n## {severity.upper()} Severity Issues\n\n"
                for i, vuln in enumerate(by_severity[severity], 1):
                    report += f"### {i}. {vuln.get('type', 'Unknown').replace('_', ' ').title()}\n\n"
                    report += f"**File:** `{vuln.get('file', 'unknown')}`\n"
                    report += f"**Line:** {vuln.get('line', 'unknown')}\n\n"
                    report += f"**Description:** {vuln.get('description', 'No description')}\n\n"
                    report += f"**Code Snippet:**\n```\n{vuln.get('code_snippet', '')}\n```\n\n"
                    
                    # Add exploit proof if available
                    exploit = next((e for e in exploits if e.get('vulnerability_id') == i), None)
                    if exploit:
                        report += f"**Exploit Proof:** {'✅ Exploit successful' if exploit.get('exploit_successful') else '❌ Exploit failed'}\n\n"
        
        report += "\n---\n\n"
        report += "*Report generated by CodeGuard AI*\n"
        
        return report

