"""
Simple Streamlit UI to demo vulnerability scan and exploit.
"""

import streamlit as st
import asyncio
import sys
import json
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_server.code_analysis import VulnerabilityScanner
from mcp_server.e2b_executor import E2BExecutor
from mcp_server.fix_generator import FixGenerator


def load_config():
    """Load configuration from config.json or environment variables."""
    config_path = Path(__file__).parent.parent / "config.json"
    config = {}
    
    # Try to load from config.json
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
        except Exception:
            pass
    
    # Fallback to environment variables
    if not config.get('e2b_api_key'):
        config['e2b_api_key'] = os.getenv('E2B_API_KEY', '')
    if not config.get('openai_api_key'):
        config['openai_api_key'] = os.getenv('OPENAI_API_KEY', '')
    if not config.get('github_token'):
        config['github_token'] = os.getenv('GITHUB_TOKEN', '')
    
    return config


# Load config
config = load_config()

# Page config
st.set_page_config(
    page_title="CodeGuard AI Demo",
    page_icon="🔒",
    layout="wide"
)

st.title("🔒 CodeGuard AI - Security Vulnerability Scanner")
st.markdown("Upload code or paste it below to scan for security vulnerabilities.")

# Initialize session state
if 'scanner' not in st.session_state:
    st.session_state.scanner = VulnerabilityScanner()

# Sidebar for API keys
with st.sidebar:
    st.header("Configuration")
    # Pre-populate from config.json, but allow manual override
    default_e2b = config.get('e2b_api_key', '')
    default_openai = config.get('openai_api_key', '')
    
    e2b_key = st.text_input(
        "E2B API Key", 
        value=default_e2b,
        type="password", 
        help="Required for exploit testing. Loaded from config.json if available."
    )
    openai_key = st.text_input(
        "OpenAI API Key", 
        value=default_openai,
        type="password", 
        help="Required for fix generation. Loaded from config.json if available."
    )
    
    if default_e2b or default_openai:
        st.info("ℹ️ API keys loaded from config.json")
    
    st.markdown("---")
    st.markdown("### Sample Vulnerable Code")
    if st.button("Load Sample"):
        sample_path = Path(__file__).parent / "sample_vulnerable_code.py"
        if sample_path.exists():
            with open(sample_path, 'r') as f:
                st.session_state.sample_code = f.read()

# Main content
tab1, tab2 = st.tabs(["Code Scanner", "Exploit & Fix"])

with tab1:
    st.header("Code Vulnerability Scanner")
    
    code_input = st.text_area(
        "Enter code to scan:",
        height=300,
        value=st.session_state.get('sample_code', ''),
        placeholder="Paste your code here or load the sample..."
    )
    
    if st.button("Scan for Vulnerabilities", type="primary"):
        if not code_input.strip():
            st.warning("Please enter some code to scan.")
        else:
            with st.spinner("Scanning code for vulnerabilities..."):
                vulnerabilities = st.session_state.scanner.scan_code(code_input)
            
            if vulnerabilities:
                st.error(f"Found {len(vulnerabilities)} potential vulnerability/vulnerabilities!")
                
                for i, vuln in enumerate(vulnerabilities, 1):
                    with st.expander(f"🔴 {vuln['type'].replace('_', ' ').title()} - {vuln['severity'].upper()} Severity"):
                        st.write(f"**Line {vuln['line']}:**")
                        st.code(vuln['code_snippet'], language='python')
                        st.write(f"**Description:** {vuln['description']}")
                
                st.session_state.vulnerabilities = vulnerabilities
                st.session_state.scanned_code = code_input
            else:
                st.success("✅ No vulnerabilities detected!")
                st.session_state.vulnerabilities = []

with tab2:
    st.header("Exploit Testing & Fix Generation")
    
    if 'vulnerabilities' not in st.session_state or not st.session_state.vulnerabilities:
        st.info("👆 First scan some code in the 'Code Scanner' tab to find vulnerabilities.")
    else:
        st.write(f"Found {len(st.session_state.vulnerabilities)} vulnerability/vulnerabilities to test.")
        
        if not e2b_key:
            st.warning("⚠️ E2B API key required for exploit testing.")
        if not openai_key:
            st.warning("⚠️ OpenAI API key required for fix generation.")
        
        if st.button("Test Exploits & Generate Fixes", type="primary"):
            if not e2b_key or not openai_key:
                st.error("Please provide both API keys in the sidebar.")
            else:
                # Define async function to process vulnerabilities
                async def process_vulnerabilities():
                    """Process all vulnerabilities asynchronously."""
                    e2b_executor = E2BExecutor(e2b_key)
                    fix_generator = FixGenerator(openai_key)
                    
                    results = []
                    
                    for i, vuln in enumerate(st.session_state.vulnerabilities):
                        # Generate and run exploit
                        try:
                            exploit_code = await e2b_executor.generate_exploit(vuln)
                            exploit_result = await e2b_executor.run_exploit(
                                exploit_code,
                                st.session_state.scanned_code
                            )
                            
                            # Generate fix
                            fix = await fix_generator.generate_fix(
                                vuln,
                                st.session_state.scanned_code
                            )
                            
                            results.append({
                                'vulnerability': vuln,
                                'exploit': exploit_result,
                                'fix': fix,
                            })
                        except Exception as e:
                            results.append({
                                'vulnerability': vuln,
                                'exploit': {'error': str(e)},
                                'fix': None,
                            })
                    
                    # Cleanup
                    await e2b_executor.cleanup()
                    return results
                
                # Run async function
                progress_bar = st.progress(0)
                status_text = st.empty()
                status_text.text("Processing vulnerabilities...")
                
                try:
                    results = asyncio.run(process_vulnerabilities())
                    
                    # Display results
                    status_text.text("Complete!")
                    st.success("✅ Exploit testing and fix generation complete!")
                    
                    for i, result in enumerate(results, 1):
                        vuln = result['vulnerability']
                        exploit = result['exploit']
                        fix = result['fix']
                        
                        with st.expander(f"Vulnerability {i}: {vuln['type'].replace('_', ' ').title()}"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.subheader("Exploit Result")
                                if exploit.get('exploit_successful'):
                                    st.error("🔴 Exploit Successful - Vulnerability Confirmed")
                                elif 'error' in exploit:
                                    st.warning(f"⚠️ Error: {exploit['error']}")
                                else:
                                    st.info("ℹ️ Exploit did not succeed (may be false positive)")
                                
                                if exploit.get('stdout'):
                                    st.code(exploit['stdout'], language='text')
                            
                            with col2:
                                st.subheader("Suggested Fix")
                                if fix:
                                    st.code(fix.get('fixed_code', ''), language='python')
                                    st.markdown(f"**Explanation:**\n{fix.get('explanation', '')}")
                                    st.markdown(f"**Recommendations:**\n{fix.get('recommendations', '')}")
                                else:
                                    st.warning("Fix generation failed.")
                except Exception as e:
                    st.error(f"Error processing vulnerabilities: {e}")

