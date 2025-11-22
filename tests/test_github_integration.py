"""
Tests for github_integration module.
"""

import pytest
from mcp_server.github_integration import GitHubIntegration


def test_github_integration_initialization():
    """Test GitHub integration can be initialized."""
    integration = GitHubIntegration()
    assert integration.base_url == "https://api.github.com"
    assert integration.headers == {}


def test_github_integration_with_token():
    """Test GitHub integration with token."""
    token = "test_token_123"
    integration = GitHubIntegration(github_token=token)
    assert "Authorization" in integration.headers
    assert f"token {token}" in integration.headers["Authorization"]


@pytest.mark.asyncio
async def test_format_security_report():
    """Test security report formatting."""
    from mcp_server.github_integration import format_security_report
    
    vulnerabilities = [
        {
            'type': 'sql_injection',
            'severity': 'high',
            'line': 10,
            'file': 'app.py',
            'code_snippet': "query = f\"SELECT * FROM users WHERE id = '{user_id}'\"",
            'description': 'SQL injection vulnerability',
        }
    ]
    exploits = [
        {
            'vulnerability_id': 1,
            'exploit_successful': True,
        }
    ]
    
    report = await format_security_report(vulnerabilities, exploits)
    assert isinstance(report, str)
    assert 'Security Report' in report
    assert 'sql_injection' in report.lower() or 'sql injection' in report.lower()
    assert 'Exploit successful' in report

