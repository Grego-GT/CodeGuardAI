#!/usr/bin/env python3
"""
Quick test script for CodeGuard AI using sample vulnerable code.
This script helps you test the vulnerability scanner without needing GitHub.
"""

import sys
import os
import asyncio
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from sandbox_agent.agent import VulnerabilityScanner
except ImportError:
    print("Error: Could not import VulnerabilityScanner. Make sure sandbox_agent/agent.py exists.")
    sys.exit(1)


def test_vulnerability_detection():
    """Test vulnerability detection on sample files."""

    print("=" * 60)
    print("CodeGuard AI - Local Vulnerability Detection Test")
    print("=" * 60)
    print()

    sample_dir = Path(__file__).parent / "sample_vulnerable_code"

    if not sample_dir.exists():
        print(f"Error: Sample code directory not found at {sample_dir}")
        return

    # Get all Python files in the sample directory
    test_files = list(sample_dir.glob("*.py"))

    if not test_files:
        print("No Python test files found in sample_vulnerable_code/")
        return

    print(f"Found {len(test_files)} test files:")
    for f in test_files:
        print(f"  - {f.name}")
    print()

    # Initialize scanner
    scanner = VulnerabilityScanner()

    total_vulnerabilities = 0
    results_by_file = {}

    # Scan each file
    for test_file in test_files:
        print(f"\n📄 Scanning: {test_file.name}")
        print("-" * 60)

        try:
            with open(test_file, 'r') as f:
                code = f.read()

            # Scan for vulnerabilities
            vulnerabilities = scanner.scan_code(code, test_file.name)

            if vulnerabilities:
                print(f"✅ Found {len(vulnerabilities)} vulnerabilities:")
                results_by_file[test_file.name] = vulnerabilities

                for vuln in vulnerabilities:
                    print(f"\n  🔴 {vuln['type'].upper()}")
                    print(f"     Line {vuln['line']}: {vuln['code'][:80]}...")
                    print(f"     Pattern: {vuln['pattern'][:60]}...")

                total_vulnerabilities += len(vulnerabilities)
            else:
                print("  ℹ️  No vulnerabilities detected")
                results_by_file[test_file.name] = []

        except Exception as e:
            print(f"  ❌ Error scanning file: {e}")
            continue

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Files scanned: {len(test_files)}")
    print(f"Total vulnerabilities found: {total_vulnerabilities}")
    print()

    print("Breakdown by file:")
    for filename, vulns in results_by_file.items():
        vuln_types = {}
        for v in vulns:
            vuln_types[v['type']] = vuln_types.get(v['type'], 0) + 1

        print(f"\n  {filename}:")
        if vuln_types:
            for vtype, count in vuln_types.items():
                print(f"    - {vtype}: {count}")
        else:
            print(f"    - No vulnerabilities")

    print("\n" + "=" * 60)

    # Expected results
    expected_counts = {
        'sql_injection.py': 4,
        'xss_vulnerabilities.py': 6,
        'command_injection.py': 8,
        'path_traversal.py': 9
    }

    print("\nExpected vs Actual:")
    for filename, expected in expected_counts.items():
        actual = len(results_by_file.get(filename, []))
        status = "✅" if actual >= expected else "⚠️"
        print(f"  {status} {filename}: {actual}/{expected}")

    print()

    if total_vulnerabilities >= sum(expected_counts.values()):
        print("🎉 All expected vulnerabilities detected!")
        print("✅ CodeGuard AI is working correctly!")
    else:
        print("⚠️  Some vulnerabilities were not detected.")
        print("💡 This may indicate the detection patterns need adjustment.")

    print()


def print_usage():
    """Print usage instructions."""
    print("""
CodeGuard AI Test Script
========================

This script tests the vulnerability scanner against sample vulnerable code.

Usage:
    python test_sample_code.py

What it does:
1. Scans all .py files in sample_vulnerable_code/
2. Detects SQL injection, XSS, command injection, and path traversal
3. Prints detailed results for each file
4. Shows summary statistics
5. Compares against expected vulnerability counts

Note: This only tests the vulnerability detection component.
      For full end-to-end testing (including exploit generation and GitHub integration),
      use the Streamlit dashboard or orchestrator.py with a real GitHub PR.

To test the full pipeline:
    1. Push sample files to a GitHub repo
    2. Create a pull request
    3. Run: streamlit run dashboard.py
    4. Or: python orchestrator.py <owner> <repo> <pr_number> <token>
""")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', 'help']:
        print_usage()
    else:
        try:
            test_vulnerability_detection()
        except KeyboardInterrupt:
            print("\n\nTest interrupted by user.")
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
