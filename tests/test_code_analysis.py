"""
Tests for code_analysis module.
"""

import pytest
from mcp_server.code_analysis import VulnerabilityScanner, scan_pr_changes


def test_scanner_initialization():
    """Test scanner can be initialized."""
    scanner = VulnerabilityScanner()
    assert scanner is not None
    assert 'sql_injection' in scanner.patterns


def test_scan_sql_injection():
    """Test detection of SQL injection vulnerabilities."""
    scanner = VulnerabilityScanner()
    vulnerable_code = """
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = '{user_id}'"
    cursor.execute(query)
"""
    vulnerabilities = scanner.scan_code(vulnerable_code, "test.py")
    assert len(vulnerabilities) > 0
    assert any(v['type'] == 'sql_injection' for v in vulnerabilities)


def test_scan_command_injection():
    """Test detection of command injection vulnerabilities."""
    scanner = VulnerabilityScanner()
    vulnerable_code = """
def process_file(filename):
    os.system(f"cat {filename}")
"""
    vulnerabilities = scanner.scan_code(vulnerable_code, "test.py")
    assert len(vulnerabilities) > 0
    assert any(v['type'] == 'command_injection' for v in vulnerabilities)


def test_scan_clean_code():
    """Test that clean code produces no vulnerabilities."""
    scanner = VulnerabilityScanner()
    clean_code = """
def safe_function(param):
    # Use parameterized queries
    cursor.execute("SELECT * FROM users WHERE id = ?", (param,))
    return cursor.fetchone()
"""
    vulnerabilities = scanner.scan_code(clean_code, "test.py")
    assert len(vulnerabilities) == 0


@pytest.mark.asyncio
async def test_scan_pr_changes():
    """Test scanning PR changes."""
    changes = [
        {
            'file': 'app.py',
            'content': 'query = f"SELECT * FROM users WHERE id = \'{user_id}\'"',
        }
    ]
    vulnerabilities = await scan_pr_changes(changes)
    assert len(vulnerabilities) > 0

