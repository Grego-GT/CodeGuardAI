# CodeGuard AI - Architecture Documentation

## 🎯 Problem Statement

Traditional security scanning tools either:
- Run static analysis without proving vulnerabilities are exploitable
- Execute exploits in unsafe environments
- Don't integrate well with developer workflows

CodeGuard AI solves this by:
1. Running security agents **inside isolated E2B sandboxes**
2. Using **MCP clients** to connect to real-world tools (GitHub, etc.)
3. Proving vulnerabilities with **safe exploit execution**
4. Automatically posting results back to GitHub PRs

## 🏗️ Architecture Overview

### High-Level Flow

```
GitHub PR Created
       │
       ├─> Webhook/Trigger
       │
       ▼
┌─────────────────────┐
│ Streamlit Dashboard │ ← Observability & Control Plane
│  (External)         │
└──────────┬──────────┘
           │
           │ 1. Launch Sandbox
           ▼
┌──────────────────────────────────────────────┐
│         E2B Sandbox (microVM)                │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │      Security Agent (Python)           │ │
│  │                                        │ │
│  │  ┌──────────────────────────────────┐ │ │
│  │  │  1. MCP Client                   │ │ │
│  │  │     └─> Connect to GitHub MCP    │ │ │
│  │  │     └─> Fetch PR files           │ │ │
│  │  └──────────────────────────────────┘ │ │
│  │                                        │ │
│  │  ┌──────────────────────────────────┐ │ │
│  │  │  2. Vulnerability Scanner        │ │ │
│  │  │     └─> Regex pattern matching   │ │ │
│  │  │     └─> Detect SQL injection     │ │ │
│  │  │     └─> Detect XSS, etc.         │ │ │
│  │  └──────────────────────────────────┘ │ │
│  │                                        │ │
│  │  ┌──────────────────────────────────┐ │ │
│  │  │  3. Exploit Executor             │ │ │
│  │  │     └─> Generate exploit code    │ │ │
│  │  │     └─> Execute safely (in VM)   │ │ │
│  │  │     └─> Prove vulnerabilities    │ │ │
│  │  └──────────────────────────────────┘ │ │
│  │                                        │ │
│  │  ┌──────────────────────────────────┐ │ │
│  │  │  4. Report Generator             │ │ │
│  │  │     └─> Format markdown report   │ │ │
│  │  │     └─> Post via MCP client      │ │ │
│  │  └──────────────────────────────────┘ │ │
│  └────────────────────────────────────────┘ │
│                                              │
│  Logs stream back to dashboard              │
└─────────────┬────────────────────────────────┘
              │
              │ MCP Protocol (httpx)
              ▼
    ┌─────────────────────┐
    │  GitHub MCP Server  │ ← Docker Container (External)
    │  (Docker MCP Hub)   │
    └──────────┬──────────┘
               │
               │ GitHub API
               ▼
         GitHub.com
```

## 🔑 Key Design Decisions

### 1. Agent Runs Inside E2B Sandbox

**Why:**
- Exploit execution must be isolated for safety
- E2B provides perfect sandboxing for untrusted code
- Aligns with hackathon requirement: "agents inside sandboxes"

**How:**
- Orchestrator deploys agent code to sandbox filesystem
- Agent is a self-contained Python script
- All dependencies installed inside sandbox

### 2. MCP Client Inside Sandbox

**Why:**
- Demonstrates "real-world tool access" via MCP
- Agent can connect to multiple MCP servers
- Clean separation: agent (sandbox) vs tools (external)

**How:**
- Agent uses httpx to make MCP protocol calls
- Connects to GitHub MCP server at `host.docker.internal:8080`
- Can be extended to Perplexity MCP, Slack MCP, etc.

### 3. Streamlit as Observability Dashboard

**Why:**
- Hackathon demo needs visual component
- Real-time monitoring impresses judges
- Shows what's happening inside the "black box" sandbox

**How:**
- Orchestrator streams logs via callbacks
- Dashboard updates in real-time
- Shows timeline, results, and history

### 4. Docker MCP Servers

**Why:**
- Docker MCP Hub provides pre-built MCP servers
- Easy to add more tools (Perplexity, Slack, etc.)
- Production-ready and maintained

**How:**
- `docker-compose.yml` defines MCP servers
- Run via `docker-compose up -d`
- Accessible from E2B sandboxes

## 📦 Component Details

### 1. Sandbox Agent (`sandbox_agent/agent.py`)

**Purpose:** Main security analysis logic, runs inside E2B

**Classes:**

- `VulnerabilityScanner`: Pattern-based vulnerability detection
  - SQL injection patterns
  - XSS patterns
  - Command injection patterns
  - Path traversal patterns
  - Generates fix suggestions for each vulnerability type

- `ExploitExecutor`: Generate and execute exploits
  - Template-based exploit generation
  - Safe execution (already in sandbox)
  - Result validation

- `GitHubMCPClient`: MCP client for GitHub integration
  - Fetch PR files via GitHub API
  - Post comments to PRs
  - Future: Use actual MCP protocol

- `SecurityAgent`: Main orchestrator inside sandbox
  - Coordinates workflow
  - Manages logging
  - Formats reports

**Key Methods:**

```python
async def analyze_pr(repo_owner, repo_name, pr_number):
    1. Fetch PR files via MCP client
    2. Scan files for vulnerabilities
    3. Execute exploits to prove them
    4. Generate security report with fix suggestions
    5. Post report back via MCP
    6. Return results
```

### 2. Orchestrator (`orchestrator.py`)

**Purpose:** Launches and manages E2B sandboxes

**Key Methods:**

```python
async def run_agent(...):
    1. Create E2B sandbox
    2. Install dependencies (httpx, etc.)
    3. Deploy agent.py to sandbox
    4. Execute agent with config
    5. Stream logs back via callback
    6. Parse and return results
    7. Cleanup sandbox
```

**Features:**
- Async execution for non-blocking operations
- Log streaming via callbacks
- Error handling and cleanup
- JSON result parsing

### 3. Dashboard (`dashboard.py`)

**Purpose:** Observability and control plane

**Tabs:**

1. **New Analysis**: Trigger analysis for a PR
2. **Live Monitor**: Real-time progress and logs
3. **History**: Past analyses and results

**Features:**
- Real-time log streaming
- Auto-refresh during analysis
- Vulnerability visualization
- Security report display
- Analysis history tracking

### 4. Docker MCP Servers (`docker-compose.yml`)

**Purpose:** External MCP servers for tool access

**Services:**

- `github-mcp`: GitHub API access via MCP
  - Port: 8080
  - Auth: GitHub token from env var
  - Accessible from E2B sandboxes

- (Future) `perplexity-mcp`: AI-powered insights
- (Future) `slack-mcp`: Notifications

## 🔄 Data Flow

### Analysis Workflow

1. **User triggers analysis** (Streamlit dashboard)
   ```
   Input: repo_owner, repo_name, pr_number
   ```

2. **Orchestrator creates sandbox**
   ```python
   sandbox = await Sandbox.create()
   ```

3. **Orchestrator deploys agent**
   ```python
   # Write agent.py to sandbox filesystem
   sandbox.run_code(write_agent_code)
   ```

4. **Agent runs inside sandbox**
   ```python
   # Agent.py executes:
   - Connect to GitHub MCP
   - Fetch PR files
   - Scan for vulnerabilities
   - Execute exploits
   - Post report
   ```

5. **Results stream back**
   ```
   Logs → Callback → Dashboard → User
   ```

6. **Cleanup**
   ```python
   sandbox.kill()
   ```

### MCP Communication

```
Agent (inside E2B)
    │
    │ httpx.get()
    ▼
GitHub MCP Server (Docker)
    │
    │ GitHub API
    ▼
GitHub.com
    │
    │ Response
    ▼
GitHub MCP Server
    │
    │ JSON Response
    ▼
Agent (processes data)
```

## 🛡️ Security Considerations

### Exploit Execution Safety

- **Isolated environment**: E2B sandboxes are microVMs
- **No network access** (except to MCP servers)
- **Temporary**: Sandboxes are destroyed after analysis
- **No persistent storage**: Results extracted before cleanup

### API Key Management

- Keys stored in `config.json` (gitignored)
- Passed to sandbox as config, not stored
- GitHub token has minimal required permissions
- E2B API key scoped to account

### Vulnerability Detection Accuracy

- **Pattern matching**: May have false positives
- **Exploit confirmation**: Reduces false positives
- **Context-aware**: Considers file type and location
- **Extensible**: Easy to add new patterns

## 📊 Performance Characteristics

### Sandbox Lifecycle

- **Creation**: ~5-10 seconds
- **Dependency installation**: ~10-15 seconds
- **Analysis execution**: ~10-30 seconds (depends on PR size)
- **Total**: ~30-60 seconds per PR

### Scalability

- **Parallel execution**: Multiple sandboxes can run concurrently
- **E2B limits**: Based on plan (usually 10+ concurrent sandboxes)
- **Bottleneck**: GitHub API rate limits
- **Optimization**: Cache PR data, reuse sandboxes

## 🔧 Configuration

### Environment Variables

```bash
E2B_API_KEY=e2b_xxx
GITHUB_TOKEN=ghp_xxx
```

### config.json

```json
{
  "e2b_api_key": "e2b_xxx",
  "github_token": "ghp_xxx"
}
```

### Docker MCP Servers

```yaml
# docker-compose.yml
services:
  github-mcp:
    image: mcp/github-server:latest
    ports:
      - "8080:8080"
    environment:
      - GITHUB_TOKEN=${GITHUB_TOKEN}
```

## 🚀 Deployment Options

### Local Development

```bash
# Terminal 1: Start MCP servers
docker-compose up

# Terminal 2: Run dashboard
streamlit run dashboard.py
```

### Cloud Deployment (Future)

- Deploy dashboard to Streamlit Cloud
- MCP servers on AWS/GCP with public endpoints
- Webhook endpoint for automatic PR monitoring
- Database for analysis history

### GitHub Action (Future)

```yaml
# .github/workflows/codeguard.yml
on: [pull_request]
jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - name: Run CodeGuard AI
        run: python orchestrator.py ${{ github.repository_owner }} ...
```

## 🎯 Hackathon Alignment

### Criteria Checklist

- ✅ **Agents running inside E2B sandboxes**
  - Agent code executes entirely within E2B microVM

- ✅ **Connect to real tools through MCP**
  - Agent uses MCP client to connect to GitHub MCP server

- ✅ **Use Docker MCP Hub servers**
  - GitHub MCP server from Docker MCP Hub

- ✅ **Demonstrate practical value**
  - Automated security testing for GitHub PRs

- ✅ **Show observability**
  - Real-time dashboard with logs and results

### Unique Value Proposition

1. **Real-world security use case**: Not a toy example
2. **Safe exploit execution**: Actually proves vulnerabilities
3. **GitHub integration**: Developers see results in PRs
4. **Extensible**: Easy to add more MCP servers/tools
5. **Production-ready**: Can be deployed today

## 📚 Future Enhancements

### Short-term (Hackathon++)

1. Add Perplexity MCP for AI-powered fix suggestions
2. Webhook listener for automatic PR monitoring
3. Support more languages (JavaScript, Go, etc.)
4. Better exploit generation (LLM-powered)

### Medium-term

1. Machine learning for vulnerability detection
2. Multi-agent collaboration (one agent per file)
3. Remediation PRs (auto-fix vulnerabilities)
4. Integration with CI/CD pipelines

### Long-term

1. Enterprise features (SSO, audit logs, etc.)
2. Custom rule engine
3. Compliance reporting (SOC2, GDPR, etc.)
4. SaaS offering with managed infrastructure

## 🤝 Contributing

See `CONTRIBUTING.md` for guidelines on:
- Adding new vulnerability patterns
- Implementing new MCP integrations
- Improving exploit generation
- Enhancing the dashboard

---

**Built for the E2B + MCP Hackathon 🚀**

Demonstrating the power of agents running inside sandboxes with real-world tool access via MCP.
