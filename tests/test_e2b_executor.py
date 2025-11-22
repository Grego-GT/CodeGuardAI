"""
Tests for e2b_executor module.
"""

import pytest
from mcp_server.e2b_executor import E2BExecutor


@pytest.mark.asyncio
async def test_executor_initialization():
    """Test executor can be initialized."""
    executor = E2BExecutor(api_key="test_key")
    assert executor.api_key == "test_key"
    assert executor.sandbox is None


@pytest.mark.asyncio
async def test_generate_exploit():
    """Test exploit generation."""
    executor = E2BExecutor(api_key="test_key")
    vulnerability = {
        'type': 'sql_injection',
        'code_snippet': "query = f\"SELECT * FROM users WHERE id = '{user_id}'\"",
    }
    exploit = await executor.generate_exploit(vulnerability)
    assert isinstance(exploit, str)
    assert 'exploit' in exploit.lower() or 'test' in exploit.lower()


@pytest.mark.asyncio
async def test_generate_exploit_unknown_type():
    """Test exploit generation for unknown vulnerability type."""
    executor = E2BExecutor(api_key="test_key")
    vulnerability = {
        'type': 'unknown_vuln',
        'code_snippet': "some code",
    }
    exploit = await executor.generate_exploit(vulnerability)
    assert isinstance(exploit, str)
    assert 'unknown_vuln' in exploit

