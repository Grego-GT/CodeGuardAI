# CodeGuardAI
CodeGuard AI is an MCP-powered security agent that scans GitHub pull requests for vulnerabilities, uses E2B sandboxes to safely execute live exploits proving these vulnerabilities, and automatically generates secure code fixes with explanations, delivering real-time, actionable security insights to developers and enterprises.

![CodeGuardAI Diagram](/assets/CodeGuardAI_Diagram.png)

## Features

- 🔍 **Automated Vulnerability Scanning**: Detects common security vulnerabilities (SQL injection, XSS, command injection, path traversal)
- 🧪 **Live Exploit Testing**: Uses E2B sandboxes to safely prove vulnerabilities with real exploits
- 🤖 **AI-Powered Fix Generation**: Leverages OpenAI API to generate secure code fixes with explanations
- 📊 **Comprehensive Security Reports**: Automatically posts detailed reports to GitHub pull requests
- 🎯 **MCP Integration**: Exposes tools via MCP server for integration with other systems

## Project Structure

```
codeguard-ai/
├── mcp_server/                    # Core MCP server components
│   ├── code_analysis.py           # Vulnerability detection logic
│   ├── e2b_executor.py            # E2B sandbox integration
│   ├── github_integration.py      # GitHub API integration
│   ├── fix_generator.py           # OpenAI API integration
│   └── server.py                  # Main MCP server
├── demo/                          # Demo application
│   ├── streamlit_app.py           # Streamlit UI for testing
│   └── sample_vulnerable_code.py  # Sample code for testing
├── tests/                         # Test suite
└── config.example.json            # Configuration template
```

## Setup

### Prerequisites

- Python 3.10 or higher
- E2B API key ([get one here](https://e2b.dev))
- OpenAI API key ([get one here](https://platform.openai.com/api-keys))
- GitHub Personal Access Token (optional, for PR integration)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd CodeGuardAI
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure the application:
```bash
cp config.example.json config.json
```

Edit `config.json` and add your API keys:
```json
{
  "e2b_api_key": "your_e2b_api_key",
  "openai_api_key": "your_openai_api_key",
  "github_token": "your_github_token"
}
```

## Usage

### Running the Demo (Streamlit)

The easiest way to test CodeGuard AI is using the Streamlit demo:

```bash
streamlit run demo/streamlit_app.py
```

This will open a web interface where you can:
- Paste code or load the sample vulnerable code
- Scan for vulnerabilities
- Test exploits (requires E2B API key)
- Generate fixes (requires OpenAI API key)

### Running the MCP Server

To run the MCP server:

```bash
python -m mcp_server.server
```

The server exposes two main tools:
- `scan_pr`: Scan a GitHub PR for vulnerabilities
- `scan_and_exploit_pr`: Full workflow (scan, exploit, generate fixes, post report)

### Using via MCP Client

Once the MCP server is running, you can call it from an MCP client:

```python
# Example: Scan a PR
result = await client.call_tool("scan_pr", {
    "repo_owner": "owner",
    "repo_name": "repo",
    "pr_number": 123
})
```

### Running Tests

```bash
pytest tests/
```

## Development

### Adding New Vulnerability Patterns

Edit `mcp_server/code_analysis.py` and add patterns to the `VulnerabilityScanner.patterns` dictionary:

```python
self.patterns = {
    'new_vuln_type': [
        r'pattern_to_match',
    ],
}
```

### Extending Exploit Generation

Modify `mcp_server/e2b_executor.py` to add exploit templates for new vulnerability types.

### Customizing Fix Generation

Update the prompt in `mcp_server/fix_generator.py` to adjust how OpenAI generates fixes. You can also change the model (e.g., `gpt-4-turbo-preview`, `gpt-3.5-turbo`) based on your needs.

## Architecture

1. **Code Analysis**: Regex-based pattern matching for common vulnerabilities
2. **E2B Execution**: Isolated sandbox environment for safe exploit testing
3. **Fix Generation**: LLM-powered code fix generation with explanations
4. **GitHub Integration**: Automated PR monitoring and reporting

## Security Considerations

- E2B sandboxes provide isolation for exploit testing
- All API keys should be kept secure (use environment variables in production)
- The vulnerability scanner uses pattern matching - may produce false positives/negatives
- Always review AI-generated fixes before applying to production code

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]
