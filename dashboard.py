"""
Streamlit Observability Dashboard for CodeGuard AI.
Shows real-time progress of security agents running inside E2B sandboxes.
"""

import streamlit as st
import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from orchestrator import SandboxOrchestrator


def load_config():
    """Load configuration from config.json."""
    config_path = Path(__file__).parent / "config.json"
    if config_path.exists():
        with open(config_path, 'r') as f:
            return json.load(f)
    return {}


# Initialize session state
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []
if 'current_analysis' not in st.session_state:
    st.session_state.current_analysis = None
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'orchestrator' not in st.session_state:
    config = load_config()
    st.session_state.orchestrator = SandboxOrchestrator(config.get('e2b_api_key', ''))


# Page config
st.set_page_config(
    page_title="CodeGuard AI - Observability Dashboard",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ CodeGuard AI - Sandbox Agent Observability")
st.markdown("**Real-time monitoring of security agents running inside E2B sandboxes**")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")

    config = load_config()

    st.markdown("### API Keys")
    if config.get('e2b_api_key'):
        st.success("✓ E2B API Key configured")
    else:
        st.error("✗ E2B API Key missing")

    if config.get('github_token'):
        st.success("✓ GitHub Token configured")
    else:
        st.error("✗ GitHub Token missing")

    st.markdown("---")

    st.markdown("### Architecture")
    st.info("""
    **Flow:**
    1. GitHub PR trigger
    2. Launch E2B Sandbox
    3. Agent runs inside sandbox
    4. MCP client connects to GitHub MCP
    5. Results posted to PR
    """)

    st.markdown("---")

    st.markdown("### Analysis History")
    st.write(f"Total analyses: {len(st.session_state.analysis_history)}")


# Main tabs
tab1, tab2, tab3 = st.tabs(["🚀 New Analysis", "📊 Live Monitor", "📜 History"])

with tab1:
    st.header("Launch New Security Analysis")
    st.markdown("Trigger a security analysis for a GitHub Pull Request")

    col1, col2, col3 = st.columns(3)

    with col1:
        repo_owner = st.text_input("Repository Owner", value="", placeholder="e.g., octocat")

    with col2:
        repo_name = st.text_input("Repository Name", value="", placeholder="e.g., hello-world")

    with col3:
        pr_number = st.number_input("PR Number", min_value=1, value=1)

    if st.button("🔍 Launch Analysis", type="primary"):
        if not repo_owner or not repo_name:
            st.error("Please provide repository owner and name")
        elif not config.get('e2b_api_key'):
            st.error("E2B API key not configured. Please add it to config.json")
        elif not config.get('github_token'):
            st.error("GitHub token not configured. Please add it to config.json")
        else:
            # Initialize analysis
            st.session_state.current_analysis = {
                'repo_owner': repo_owner,
                'repo_name': repo_name,
                'pr_number': pr_number,
                'status': 'running',
                'started_at': datetime.now().isoformat(),
                'logs': [],
                'result': None
            }
            st.session_state.logs = []

            st.info(f"🚀 Launching analysis for {repo_owner}/{repo_name} PR #{pr_number}")
            st.info("⏩ Switch to the 'Live Monitor' tab to watch progress")

            # Trigger async analysis
            async def run_analysis():
                """Run the analysis asynchronously."""
                await st.session_state.orchestrator.initialize()

                def log_callback(message: str):
                    """Callback to capture logs."""
                    st.session_state.logs.append({
                        'timestamp': datetime.now().isoformat(),
                        'message': message
                    })

                result = await st.session_state.orchestrator.run_agent(
                    repo_owner,
                    repo_name,
                    pr_number,
                    config.get('github_token', ''),
                    log_callback
                )

                # Update analysis
                st.session_state.current_analysis['status'] = 'completed'
                st.session_state.current_analysis['completed_at'] = datetime.now().isoformat()
                st.session_state.current_analysis['result'] = result
                st.session_state.current_analysis['logs'] = st.session_state.logs

                # Add to history
                st.session_state.analysis_history.insert(0, st.session_state.current_analysis)

                return result

            # Run in background
            with st.spinner("Initializing sandbox..."):
                try:
                    result = asyncio.run(run_analysis())
                    st.success("✅ Analysis complete! Check the Live Monitor tab for results.")
                except Exception as e:
                    st.error(f"❌ Analysis failed: {str(e)}")
                    st.session_state.current_analysis['status'] = 'failed'
                    st.session_state.current_analysis['error'] = str(e)


with tab2:
    st.header("📊 Live Analysis Monitor")

    if st.session_state.current_analysis:
        analysis = st.session_state.current_analysis

        # Status header
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Repository", f"{analysis['repo_owner']}/{analysis['repo_name']}")
        with col2:
            st.metric("PR Number", analysis['pr_number'])
        with col3:
            status = analysis['status']
            status_color = {
                'running': '🟡',
                'completed': '🟢',
                'failed': '🔴'
            }.get(status, '⚪')
            st.metric("Status", f"{status_color} {status.upper()}")

        st.markdown("---")

        # Progress timeline
        st.subheader("🔄 Progress Timeline")

        if st.session_state.logs:
            # Show logs in real-time
            log_container = st.container()
            with log_container:
                for log_entry in st.session_state.logs:
                    timestamp = log_entry['timestamp'].split('T')[1][:8] if 'T' in log_entry['timestamp'] else ''
                    message = log_entry['message']
                    st.text(f"[{timestamp}] {message}")
        else:
            st.info("No logs yet. Waiting for sandbox to start...")

        st.markdown("---")

        # Results (if completed)
        if analysis['status'] == 'completed' and analysis.get('result'):
            st.subheader("📋 Analysis Results")

            result = analysis['result']

            if result.get('status') == 'success':
                vulns = result.get('vulnerabilities', [])

                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Vulnerabilities Found", len(vulns))
                with col2:
                    exploits = result.get('exploits', [])
                    successful_exploits = sum(1 for e in exploits if e.get('exploit_successful'))
                    st.metric("Exploits Confirmed", successful_exploits)

                # Show vulnerabilities
                if vulns:
                    st.subheader("🔍 Detected Vulnerabilities")
                    for i, vuln in enumerate(vulns, 1):
                        with st.expander(f"{i}. {vuln['type'].replace('_', ' ').title()} - {vuln['severity'].upper()}"):
                            st.write(f"**File:** `{vuln['file']}:{vuln['line']}`")
                            st.code(vuln['code_snippet'], language='python')
                            st.write(f"**Description:** {vuln['description']}")

                # Show report
                if result.get('report'):
                    st.subheader("📄 Security Report")
                    st.markdown(result['report'])
            else:
                st.error(f"Analysis failed: {result.get('error', 'Unknown error')}")

        elif analysis['status'] == 'failed':
            st.error(f"❌ Analysis failed: {analysis.get('error', 'Unknown error')}")

        # Auto-refresh while running
        if analysis['status'] == 'running':
            time.sleep(2)
            st.rerun()

    else:
        st.info("👈 No active analysis. Launch one from the 'New Analysis' tab.")


with tab3:
    st.header("📜 Analysis History")

    if st.session_state.analysis_history:
        for i, analysis in enumerate(st.session_state.analysis_history):
            with st.expander(
                f"#{i+1} - {analysis['repo_owner']}/{analysis['repo_name']} PR #{analysis['pr_number']} - {analysis['status'].upper()}"
            ):
                st.write(f"**Started:** {analysis['started_at']}")
                if analysis.get('completed_at'):
                    st.write(f"**Completed:** {analysis['completed_at']}")

                if analysis.get('result'):
                    result = analysis['result']
                    vulns = result.get('vulnerabilities', [])
                    st.write(f"**Vulnerabilities Found:** {len(vulns)}")

                    if result.get('report'):
                        st.markdown("**Report:**")
                        st.markdown(result['report'])
    else:
        st.info("No analysis history yet. Run your first analysis!")


# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.9em;'>
🤖 CodeGuard AI - Powered by E2B Sandboxes + Docker MCP Hub<br/>
Agents run inside sandboxes, connecting to real tools via MCP
</div>
""", unsafe_allow_html=True)
