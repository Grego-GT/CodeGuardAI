"""
Vulnerability detection logic for scanning code changes.
Detects common security vulnerabilities like SQL injection, XSS, etc.
"""

import re
from typing import List, Dict, Optional


class VulnerabilityScanner:
    """Scans code for common security vulnerabilities."""
    
    def __init__(self):
        # Patterns for common vulnerabilities
        self.patterns = {
            'sql_injection': [
                r'execute\s*\(\s*["\'].*%s.*["\']',  # String formatting in SQL
                r'execute\s*\(\s*f["\']',  # f-strings in SQL
                r'query\s*\(\s*["\'].*\+.*["\']',  # String concatenation
                r'execute\s*\(\s*["\'].*\{.*\}.*["\']',  # Format strings
            ],
            'xss': [
                r'innerHTML\s*=',  # Direct innerHTML assignment
                r'document\.write\s*\(',  # document.write
                r'eval\s*\(',  # eval() usage
                r'\.html\s*\([^)]*\+',  # jQuery .html() with concatenation
            ],
            'command_injection': [
                r'os\.system\s*\(',
                r'subprocess\.call\s*\(',
                r'subprocess\.Popen\s*\(',
                r'eval\s*\(',
            ],
            'path_traversal': [
                r'open\s*\(\s*["\'].*\.\./',  # Path traversal in file operations
                r'os\.path\.join\s*\([^)]*\.\.',  # Path traversal in join
            ],
        }
    
    def scan_code(self, code: str, file_path: str = "") -> List[Dict[str, any]]:
        """
        Scan code for vulnerabilities.
        
        Args:
            code: The code content to scan
            file_path: Optional file path for context
            
        Returns:
            List of vulnerability findings with line numbers and descriptions
        """
        vulnerabilities = []
        lines = code.split('\n')
        
        for vuln_type, patterns in self.patterns.items():
            for pattern in patterns:
                for line_num, line in enumerate(lines, start=1):
                    if re.search(pattern, line, re.IGNORECASE):
                        vulnerabilities.append({
                            'type': vuln_type,
                            'severity': self._get_severity(vuln_type),
                            'line': line_num,
                            'file': file_path,
                            'code_snippet': line.strip(),
                            'description': self._get_description(vuln_type),
                        })
        
        return vulnerabilities
    
    def _get_severity(self, vuln_type: str) -> str:
        """Get severity level for vulnerability type."""
        severity_map = {
            'sql_injection': 'high',
            'xss': 'high',
            'command_injection': 'critical',
            'path_traversal': 'high',
        }
        return severity_map.get(vuln_type, 'medium')
    
    def _get_description(self, vuln_type: str) -> str:
        """Get human-readable description for vulnerability type."""
        descriptions = {
            'sql_injection': 'Potential SQL injection vulnerability detected. User input may be directly concatenated into SQL queries.',
            'xss': 'Potential Cross-Site Scripting (XSS) vulnerability. User input may be rendered without sanitization.',
            'command_injection': 'Potential command injection vulnerability. User input may be executed as system commands.',
            'path_traversal': 'Potential path traversal vulnerability. User input may allow access to files outside intended directory.',
        }
        return descriptions.get(vuln_type, 'Security vulnerability detected.')


async def scan_pr_changes(changes: List[Dict]) -> List[Dict]:
    """
    Scan a list of code changes from a PR.
    
    Args:
        changes: List of dicts with 'file', 'content', and optionally 'old_content'
        
    Returns:
        List of all vulnerabilities found across all files
    """
    scanner = VulnerabilityScanner()
    all_vulnerabilities = []
    
    for change in changes:
        file_path = change.get('file', 'unknown')
        content = change.get('content', '')
        
        if content:
            vulns = scanner.scan_code(content, file_path)
            all_vulnerabilities.extend(vulns)
    
    return all_vulnerabilities

