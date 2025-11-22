# CodeGuard AI - Sandbox-Native Architecture Setup Guide

## 🎯 Overview

This guide will help you set up CodeGuard AI's new sandbox-native architecture where the security agent runs **inside E2B sandboxes** and uses **MCP clients** to connect to real-world Docker MCP servers.

## 🏗️ Architecture

### New Architecture (Sandbox-Native)

```
┌─────────────────────────────────────────────────────────────┐
│                   Streamlit Dashboard                        │
│            (Observability & Orchestration)                   │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    E2B Sandbox (microVM)                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          Security Agent (runs inside)                │  │
│  │                                                       │  │
│  │  1. Vulnerability Scanner                            │  │
│  │  2. Exploit Executor                                 │  │
│  │  3. MCP Client ─────────────┐                        │  │
│  └─────────────────────────────┼────────────────────────┘  │
└────────────────────────────────┼───────────────────────────┘
                                 │
                                 │ MCP Protocol
                                 ▼
                    ┌────────────────────────┐
                    │   GitHub MCP Server    │
                    │   (Docker Container)   │
                    └────────────────────────┘
                                 │
                                 ▼
                          GitHub API
```

### Key Components

1. **Streamlit Dashboard** (`dashboard.py`)
   - Triggers analysis for GitHub PRs
   - Real-time monitoring of sandbox execution
   - Displays logs and results
   - Observability for demo purposes

2. **Orchestrator** (`orchestrator.py`)
   - Launches E2B sandboxes
   - Deploys agent code inside sandbox
   - Manages sandbox lifecycle
   - Streams logs back to dashboard

3. **Sandbox Agent** (`sandbox_agent/agent.py`)
   - **Runs entirely inside E2B sandbox**
   - Uses MCP client to connect to external GitHub MCP server
   - Scans code for vulnerabilities
   - Executes exploits (safely, already in sandbox)
   - Posts results back via MCP

4. **GitHub MCP Server** (Docker container)
   - External MCP server from Docker MCP Hub
   - Provides GitHub API access via MCP protocol
   - Agent inside sandbox connects to this

## 📋 Prerequisites

- Python 3.10 or higher
- Docker and Docker Compose
- E2B API key ([get one here](https://e2b.dev))
- GitHub Personal Access Token ([create one here](https://github.com/settings/tokens))

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd CodeGuardAI

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys

Create or update `config.json`:

```json
{
  "e2b_api_key": "your_e2b_api_key_here",
  "github_token": "your_github_token_here"
}
```

### 3. Start GitHub MCP Server

```bash
# Set GitHub token in environment
export GITHUB_TOKEN="your_github_token_here"

# Start GitHub MCP server via Docker Compose
docker-compose up -d

# Verify it's running
docker ps | grep github-mcp
```

### 4. Launch Dashboard

```bash
streamlit run dashboard.py
```

The dashboard will open at `http://localhost:8501`

## 🎮 Usage

### Running an Analysis

1. Open the dashboard at `http://localhost:8501`
2. Go to the **"New Analysis"** tab
3. Enter:
   - Repository Owner (e.g., `octocat`)
   - Repository Name (e.g., `hello-world`)
   - PR Number (e.g., `1`)
4. Click **"Launch Analysis"**
5. Switch to the **"Live Monitor"** tab to watch progress in real-time

### What Happens

1. **Sandbox Creation**: Orchestrator creates a new E2B sandbox
2. **Environment Setup**: Installs dependencies inside sandbox (httpx, etc.)
3. **Agent Deployment**: Deploys agent code into sandbox filesystem
4. **Agent Execution**: Agent runs inside sandbox and:
   - Connects to GitHub MCP server via MCP client
   - Fetches PR files from GitHub
   - Scans code for vulnerabilities
   - Executes exploits (safely inside sandbox)
   - Posts security report back to PR
5. **Results Display**: Dashboard shows logs and final results
6. **Cleanup**: Sandbox is terminated

## 📊 Observability Features

The dashboard provides:

- **Real-time logs** from sandbox execution
- **Progress timeline** showing each step
- **Vulnerability details** with severity levels
- **Exploit results** showing confirmed vulnerabilities
- **Security reports** posted to GitHub
- **Analysis history** for all past runs

## 🔧 Testing Locally

### Test the Orchestrator

Run the orchestrator directly to test sandbox execution:

```bash
python orchestrator.py <repo_owner> <repo_name> <pr_number> <github_token>

# Example:
python orchestrator.py octocat hello-world 1 ghp_xxxxxxxxxxxx
```

### Test the Agent Code

You can also test the agent code locally (simulated):

```bash
cd sandbox_agent
python agent.py '{"github_token": "ghp_xxx", "repo_owner": "octocat", "repo_name": "hello-world", "pr_number": 1}'
```

## 🐳 Docker MCP Server Details

The `docker-compose.yml` sets up:

- **GitHub MCP Server** on port `8080`
- Connects to GitHub API using your token
- Accessible from E2B sandboxes via `host.docker.internal:8080`

### Adding More MCP Servers

You can add more Docker MCP servers from the Docker MCP Hub:

```yaml
# In docker-compose.yml
perplexity-mcp:
  image: mcp/perplexity-server:latest
  ports:
    - "8081:8080"
  environment:
    - PERPLEXITY_API_KEY=${PERPLEXITY_API_KEY}
```

Then update the agent to connect to multiple MCP servers.

## 🎯 Hackathon Demo Points

This architecture demonstrates:

1. ✅ **Agents running inside E2B sandboxes**
   - Agent code executes entirely within E2B microVM
   - Safe exploit testing in isolated environment

2. ✅ **MCP clients inside sandboxes**
   - Agent uses MCP client to connect to external tools
   - Shows real-world tool integration

3. ✅ **Docker MCP Hub integration**
   - Uses GitHub MCP server from Docker MCP Hub
   - Can easily add more MCP servers

4. ✅ **Real-world use case**
   - Automated security testing
   - Actual GitHub PR integration
   - Practical value for developers

5. ✅ **Observability**
   - Real-time monitoring via dashboard
   - Shows what's happening inside sandbox
   - Great for demos and presentations

## 🏆 Key Differentiators

### Before (External MCP Architecture)
- MCP server runs externally
- MCP server calls E2B to execute code
- Orchestration happens outside sandbox

### After (Sandbox-Native Architecture)
- **Agent runs inside E2B sandbox**
- **Agent uses MCP client to call external tools**
- **All scanning/exploitation happens inside sandbox**
- **Clearer separation of concerns**
- **More aligned with hackathon criteria**

## 📁 Project Structure

```
CodeGuardAI/
├── sandbox_agent/           # Agent that runs INSIDE E2B
│   ├── __init__.py
│   └── agent.py            # Main agent with MCP client
├── orchestrator.py          # Launches agents in E2B sandboxes
├── dashboard.py             # Streamlit observability dashboard
├── docker-compose.yml       # GitHub MCP server setup
├── config.json              # API keys configuration
├── requirements.txt         # Python dependencies
├── SETUP_GUIDE.md          # This file
└── mcp_server/             # (Legacy - can be removed)
    └── ...
```

## 🔍 Troubleshooting

### E2B Sandbox Issues

If sandbox creation fails:
- Check your E2B API key is valid
- Verify you have credits in your E2B account
- Check E2B service status

### GitHub MCP Server Issues

If GitHub MCP connection fails:
- Verify Docker container is running: `docker ps`
- Check logs: `docker logs codeguard-github-mcp`
- Ensure GitHub token has proper permissions
- Test connectivity from sandbox to `host.docker.internal:8080`

### Agent Execution Issues

If agent fails inside sandbox:
- Check dashboard logs for error messages
- Verify dependencies installed correctly
- Test agent code locally first
- Check GitHub token permissions

## 🚀 Next Steps

### For the Hackathon

1. **Test with real PRs**: Create a test repository with vulnerable code
2. **Record demo**: Show the full workflow in action
3. **Highlight architecture**: Emphasize MCP inside E2B
4. **Show observability**: Dashboard is great for live demos

### Future Enhancements

- Add webhook listener for automatic PR monitoring
- Support more MCP servers (Perplexity, Slack, etc.)
- Add AI-powered fix generation via MCP
- Implement retry logic and error handling
- Add metrics and analytics

## 📚 Resources

- [E2B Documentation](https://e2b.dev/docs)
- [Docker MCP Hub](https://github.com/docker/mcp-hub)
- [MCP Protocol Specification](https://github.com/anthropics/mcp)
- [CodeGuard AI Repository](your-repo-url)

## 💡 Tips for Demo

1. **Start with the architecture diagram** - Show how MCP runs inside E2B
2. **Show the dashboard first** - Observability is impressive
3. **Run live analysis** - Real-time logs are engaging
4. **Highlight the sandbox isolation** - Emphasize safety of exploit testing
5. **Show GitHub integration** - Real-world practical value

---

🎉 **You're ready to demo CodeGuard AI at the hackathon!**

For questions or issues, please open a GitHub issue or contact the team.
