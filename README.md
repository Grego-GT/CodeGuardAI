# CodeGuard AI 🛡️

> **Security agents running inside E2B sandboxes, connecting to real-world tools via Docker MCP servers**

CodeGuard AI is a sandbox-native security agent that scans GitHub pull requests for vulnerabilities, safely executes exploits **inside E2B sandboxes**, and posts detailed security reports—all while using **MCP clients** to connect to real GitHub tools via Docker MCP Hub.

![CodeGuardAI Diagram](/assets/CodeGuardAI_Diagram.png)

## 🌟 Hackathon Features

- 🏃 **Agents Inside Sandboxes**: Security agent runs entirely within E2B microVMs
- 🔌 **MCP Client Integration**: Agent uses MCP clients to connect to GitHub MCP server
- 🐳 **Docker MCP Hub**: Uses pre-built GitHub MCP server from Docker MCP Hub
- 🔍 **Automated Vulnerability Scanning**: Detects SQL injection, XSS, command injection, path traversal
- 🧪 **Safe Exploit Testing**: Proves vulnerabilities with real exploits in isolated environment
- 📊 **Real-time Observability**: Streamlit dashboard shows live progress and logs
- 📝 **GitHub Integration**: Posts security reports directly to pull requests

## 🏗️ Architecture

### Sandbox-Native Design

```
Streamlit Dashboard (Observability)
         ↓
    Orchestrator
         ↓
   E2B Sandbox ←─── Agent runs INSIDE
         │
         │ MCP Client
         ↓
   GitHub MCP Server (Docker)
         ↓
    GitHub API
```

**Key Innovation**: The agent runs **inside** the E2B sandbox and uses an **MCP client** to connect to external tools (GitHub MCP), rather than having an external MCP server orchestrate sandboxes.

## 📁 Project Structure

```
CodeGuardAI/
├── sandbox_agent/              # Agent that runs INSIDE E2B sandbox
│   ├── agent.py               # Main agent with MCP client
│   └── __init__.py
├── orchestrator.py             # Launches agents in E2B sandboxes
├── dashboard.py                # Streamlit observability dashboard
├── docker-compose.yml          # GitHub MCP server setup
├── config.json                 # API keys configuration
├── SETUP_GUIDE.md             # Complete setup instructions
├── ARCHITECTURE.md            # Detailed architecture docs
└── mcp_server/                # (Legacy - external MCP architecture)
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- Docker and Docker Compose
- E2B API key ([get one here](https://e2b.dev))
- GitHub Personal Access Token ([create one here](https://github.com/settings/tokens))

### Installation (5 minutes)

1. **Clone and setup**
```bash
git clone <repository-url>
cd CodeGuardAI

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

2. **Configure API keys**

Create `config.json`:
```json
{
  "e2b_api_key": "your_e2b_api_key_here",
  "github_token": "your_github_token_here"
}
```

3. **Start GitHub MCP Server**
```bash
export GITHUB_TOKEN="your_github_token_here"
docker-compose up -d
```

4. **Launch Dashboard**
```bash
streamlit run dashboard.py
```

Open http://localhost:8501 and you're ready! 🎉

## 📖 Usage

### Running Security Analysis

1. Open the dashboard at http://localhost:8501
2. Go to **"New Analysis"** tab
3. Enter repository details:
   - Owner: `octocat`
   - Name: `hello-world`
   - PR Number: `1`
4. Click **"Launch Analysis"**
5. Switch to **"Live Monitor"** to watch real-time progress

### What Happens Behind the Scenes

1. **Sandbox Creation**: New E2B microVM is created
2. **Agent Deployment**: Security agent code deployed inside sandbox
3. **MCP Connection**: Agent connects to GitHub MCP server
4. **Analysis**:
   - Fetches PR files via MCP
   - Scans for vulnerabilities
   - Executes exploits (safely inside sandbox)
5. **Reporting**: Posts security report to PR via MCP
6. **Cleanup**: Sandbox is terminated

### Testing Locally

Test the orchestrator directly:
```bash
python orchestrator.py <repo_owner> <repo_name> <pr_number> <github_token>
```

Example:
```bash
python orchestrator.py octocat hello-world 1 ghp_xxxxxxxxxxxx
```

## 📚 Documentation

- **[SETUP_GUIDE.md](SETUP_GUIDE.md)**: Complete setup instructions with troubleshooting
- **[ARCHITECTURE.md](ARCHITECTURE.md)**: Detailed architecture documentation
- **[Demo Video](#)**: Watch CodeGuard AI in action (coming soon)

## 🎯 Hackathon Highlights

### Why This Architecture is Special

1. **Agents Inside Sandboxes**: The security agent runs entirely within E2B microVMs, not just using them for code execution
2. **MCP Clients in Sandboxes**: Agent uses MCP clients to connect to external tools from inside the sandbox
3. **Real-World Tools**: Uses GitHub MCP server from Docker MCP Hub for authentic GitHub integration
4. **Practical Use Case**: Solves real security problems for development teams
5. **Observability**: Dashboard shows exactly what's happening inside the sandbox in real-time

### Key Differentiators

**Traditional Approach:**
```
External Orchestrator → Calls E2B → Executes Code → Returns Results
```

**CodeGuard AI:**
```
E2B Sandbox [Agent + MCP Client] → Connects to MCP Servers → Does Everything Inside
```

## 🔧 Development

### Adding New Vulnerability Patterns

Edit `sandbox_agent/agent.py` and add patterns to `VulnerabilityScanner.patterns`:

```python
self.patterns = {
    'new_vuln_type': [
        r'pattern_to_match',
    ],
}
```

### Adding More MCP Servers

Edit `docker-compose.yml`:

```yaml
perplexity-mcp:
  image: mcp/perplexity-server:latest
  ports:
    - "8081:8080"
  environment:
    - PERPLEXITY_API_KEY=${PERPLEXITY_API_KEY}
```

Then update agent to connect to the new server.

### Extending Exploit Generation

Modify `ExploitExecutor.generate_exploit()` in `sandbox_agent/agent.py`.

## 🛡️ Security Considerations

- **Sandbox Isolation**: E2B provides microVM-level isolation for exploit testing
- **Temporary Execution**: Sandboxes are destroyed after each analysis
- **API Key Security**: Keys in `config.json` (gitignored), never committed
- **Network Isolation**: Sandboxes only connect to specified MCP servers
- **Pattern Matching**: May produce false positives; exploit confirmation reduces this