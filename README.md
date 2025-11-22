# CodeGuard AI 🛡️

> **Security agents running inside E2B sandboxes, connecting to real-world tools via Docker MCP servers**

**CodeGuard AI: The CodeRabbit Killer for Security**

> While tools like CodeRabbit provide general code review suggestions, CodeGuard AI specializes in security by actually proving vulnerabilities are exploitable—no false positives, just confirmed threats.

## What It Is

CodeGuard AI is an autonomous security agent that scans GitHub pull requests for vulnerabilities and proves they're exploitable by safely executing exploits inside isolated E2B sandboxes.

## Why It Exists

Traditional security scanners flood developers with hundreds of potential vulnerabilities but can't tell you which ones are actually exploitable. This wastes time investigating false positives or risks missing real threats.

## How It Solves It

CodeGuard AI runs security agents entirely inside E2B microVMs, where exploits can be safely tested without risk. The agent uses MCP clients to seamlessly connect to GitHub, automatically fetching PR files, analyzing code, executing exploit tests, and posting detailed security reports with fix suggestions directly to pull requests.

### Architecture

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

**Key Innovation**: The agent runs **inside** an E2B sandbox to find and prove real exploits.

## Quick Start

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Configure API keys**: Create `config.json` with your E2B API key and GitHub token
3. **Start GitHub MCP Server**: `docker-compose up -d`
4. **Launch Dashboard**: `streamlit run dashboard.py`

See **[SETUP_GUIDE.md](SETUP_GUIDE.md)** for detailed setup instructions.

## Documentation

- **[SETUP_GUIDE.md](SETUP_GUIDE.md)**: Complete setup instructions with troubleshooting
- **[ARCHITECTURE.md](ARCHITECTURE.md)**: Detailed architecture documentation
- **[DEMO_WORKFLOW.md](DEMO_WORKFLOW.md)**: Demo workflow and usage examples
- **[TESTING_GUIDE.md](TESTING_GUIDE.md)**: Testing and development guide

## Features

- 🏃 **Agents Inside Sandboxes**: Security agent runs entirely within E2B microVMs
- 🔌 **MCP Client Integration**: Agent uses MCP clients to connect to GitHub MCP server
- 🔍 **Automated Vulnerability Scanning**: Detects SQL injection, XSS, command injection, path traversal
- 🧪 **Safe Exploit Testing**: Proves vulnerabilities with real exploits in isolated environment
- 📝 **GitHub Integration**: Posts security reports directly to pull requests with fix suggestions

## Development

See **[TESTING_GUIDE.md](TESTING_GUIDE.md)** for information on:
- Adding new vulnerability patterns
- Extending exploit generation
- Adding more MCP servers
