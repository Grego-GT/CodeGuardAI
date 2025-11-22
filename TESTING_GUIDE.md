# CodeGuard AI Testing Guide

This guide will help you test all the functionality of CodeGuard AI using the sample vulnerable code provided.

## 📋 What's Been Created

### Sample Vulnerable Code (`sample_vulnerable_code/`)

Four Python files with intentionally vulnerable code:

| File | Vulnerabilities | Description |
|------|----------------|-------------|
| `sql_injection.py` | 4 patterns | String concat, f-strings, .format(), % operator |
| `xss_vulnerabilities.py` | 6 patterns | Reflected, stored, DOM-based XSS |
| `command_injection.py` | 8 patterns | os.system(), subprocess, eval(), exec() |
| `path_traversal.py` | 9 patterns | File access, uploads, archives |

**Total: 27+ vulnerabilities to detect**

### Testing Tools

1. **`test_sample_code.py`** - Quick local vulnerability scanner test
2. **`create_test_repo.sh`** - Automated GitHub test repository setup
3. **`sample_vulnerable_code/README.md`** - Detailed documentation

## 🧪 Testing Methods

### Method 1: Quick Local Test (Fastest - 30 seconds)

Test just the vulnerability detection without E2B or GitHub:

```bash
# Run the local test script
python test_sample_code.py
```

**What it does:**
- Scans all sample files
- Detects vulnerabilities using regex patterns
- Shows detailed results for each file
- Compares against expected counts
- ✅ No API keys required
- ✅ No GitHub needed
- ❌ Doesn't test exploit generation or MCP integration

**Expected output:**
```
📄 Scanning: sql_injection.py
✅ Found 4 vulnerabilities:
  🔴 SQL_INJECTION
     Line 16: query = "SELECT * FROM users WHERE username='" + username...
  ...

SUMMARY
Files scanned: 4
Total vulnerabilities found: 27+
🎉 All expected vulnerabilities detected!
```

---

### Method 2: Manual GitHub PR Test (Moderate - 5 minutes)

Test the full pipeline with a real GitHub PR:

#### Step 1: Create a test repository

```bash
# Using GitHub CLI
gh repo create codeguard-test --public
cd /tmp
git clone https://github.com/<your-username>/codeguard-test
cd codeguard-test
```

#### Step 2: Add vulnerable code

```bash
# Copy sample files to your repo
mkdir api
cp ~/path/to/CodeGuardAI/sample_vulnerable_code/sql_injection.py ./api/database.py
cp ~/path/to/CodeGuardAI/sample_vulnerable_code/xss_vulnerabilities.py ./api/search.py

# Create a PR
git checkout -b add-api-endpoints
git add api/
git commit -m "Add API endpoints"
git push origin add-api-endpoints
gh pr create --title "Add API endpoints" --body "Testing CodeGuard AI"
```

#### Step 3: Run CodeGuard AI

```bash
# Get your PR number (usually #1)
gh pr list

# Run via CLI
cd ~/path/to/CodeGuardAI
python orchestrator.py <your-username> codeguard-test 1 <github-token>

# OR use the dashboard
streamlit run dashboard.py
# Navigate to "New Analysis" tab
# Enter: your-username / codeguard-test / 1
# Click "Launch Analysis"
```

**What it tests:**
- ✅ E2B sandbox creation
- ✅ Vulnerability detection
- ✅ Exploit generation
- ✅ Exploit execution (safe in sandbox)
- ✅ GitHub MCP integration
- ✅ PR comment posting
- ✅ Full end-to-end pipeline

---

### Method 3: Automated GitHub Setup (Easiest - 2 minutes)

Use the automated script to set everything up:

```bash
# Run the setup script
./create_test_repo.sh

# Follow the prompts:
# - Enter repository name (or use default: codeguard-test)
# - Confirm creation
# - Script creates repo, commits files, and creates PR automatically

# Then run CodeGuard AI against the created PR
# (Script will give you the exact command to run)
```

**What it does:**
- ✅ Creates GitHub repository
- ✅ Adds all 4 vulnerable files
- ✅ Creates a pull request
- ✅ Gives you ready-to-run commands
- ✅ Fastest way to get a full test environment

---

## 📊 Expected Results

### Local Test Results

When running `test_sample_code.py`, you should see:

```
Expected vs Actual:
  ✅ sql_injection.py: 4/4
  ✅ xss_vulnerabilities.py: 6/6
  ✅ command_injection.py: 8/8
  ✅ path_traversal.py: 9/9
```

### Full Pipeline Results

When running the orchestrator or dashboard, you should see:

1. **Console Output:**
```
[ORCHESTRATOR] 🚀 Creating E2B sandbox...
[ORCHESTRATOR] ✓ Sandbox created
[ORCHESTRATOR] Setting up sandbox environment...
[ORCHESTRATOR] ✓ pip install httpx completed
[ORCHESTRATOR] 🔍 Starting security analysis inside sandbox...
[ORCHESTRATOR] Scanning api/database.py...
[ORCHESTRATOR] Found SQL injection vulnerability at line 16
[ORCHESTRATOR] Generating exploit...
[ORCHESTRATOR] Testing exploit...
[ORCHESTRATOR] ✅ Exploit successful!
...
[ORCHESTRATOR] ✅ Analysis complete!
```

2. **GitHub PR Comment:**

The PR should receive a comment like:

```markdown
## 🛡️ CodeGuard AI Security Report

**Analysis Date:** 2024-01-15 10:30:00 UTC

### Summary
- **Files Scanned:** 4
- **Vulnerabilities Found:** 27
- **Severity:** 🔴 Critical

---

### 🔴 SQL Injection (4 instances)
**File:** `api/database.py`
**Severity:** High

**Line 16:**
```python
query = "SELECT * FROM users WHERE username='" + username + "' AND password='" + password + "'"
```

**Exploit Proof:**
Payload: `' OR '1'='1' --`
Result: Authentication bypass confirmed

**Fix Suggestion:**
```python
# Use parameterized queries
cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
```

---
...
```

### Dashboard View

The Streamlit dashboard should show:

- **New Analysis Tab:**
  - Input form (filled)
  - "Launch Analysis" button
  - Success message with session ID

- **Live Monitor Tab:**
  - Real-time log streaming
  - Progress indicator
  - Vulnerability count
  - Timeline of events

- **History Tab:**
  - Analysis entry with results
  - Clickable to view detailed report
  - Statistics and charts

---

## 🐛 Troubleshooting

### Local Test Issues

**Error: "Could not import VulnerabilityScanner"**
```bash
# Make sure sandbox_agent/agent.py exists
ls sandbox_agent/agent.py

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"
```

**No vulnerabilities detected:**
```bash
# Check if files exist
ls sample_vulnerable_code/*.py

# Verify file permissions
chmod 644 sample_vulnerable_code/*.py

# Check scanner patterns in sandbox_agent/agent.py
```

### GitHub PR Test Issues

**"E2B API key not found"**
```bash
# Create config.json
cat > config.json << EOF
{
  "e2b_api_key": "your_e2b_api_key",
  "github_token": "your_github_token"
}
EOF
```

**"GitHub MCP server not accessible"**
```bash
# Start the MCP server
docker compose up -d

# Check if running
docker ps | grep github-mcp

# Check logs
docker compose logs github-mcp
```

**"Sandbox creation failed"**
```bash
# Verify E2B API key
python -c "import os; from e2b_code_interpreter import Sandbox; print('OK')"

# Check E2B dashboard for quota
# https://e2b.dev/dashboard
```

---

## 📝 Test Checklist

Use this checklist to ensure complete testing:

### Basic Functionality
- [ ] Local test script runs without errors
- [ ] All 27+ vulnerabilities detected in local test
- [ ] Sample files are readable and valid Python

### Detection Capabilities
- [ ] SQL injection detected (4 patterns)
- [ ] XSS detected (6 patterns)
- [ ] Command injection detected (8 patterns)
- [ ] Path traversal detected (9 patterns)
- [ ] Secure code examples NOT flagged

### E2B Sandbox
- [ ] Sandbox creates successfully
- [ ] Dependencies install correctly
- [ ] Agent code deploys to sandbox
- [ ] Agent executes inside sandbox
- [ ] Sandbox cleans up after analysis

### MCP Integration
- [ ] GitHub MCP server starts
- [ ] Agent connects to MCP server
- [ ] PR files fetched via MCP
- [ ] Comments posted via MCP

### Exploit Testing
- [ ] Exploits generated for vulnerabilities
- [ ] Exploits execute safely in sandbox
- [ ] Exploit results captured
- [ ] No false positives on secure code

### Reporting
- [ ] Security report generated
- [ ] Report posted to GitHub PR
- [ ] Report includes line numbers
- [ ] Report includes fix suggestions with code snippets
- [ ] Report includes remediation advice
- [ ] Report properly formatted (markdown)

### Dashboard
- [ ] Dashboard loads successfully
- [ ] New Analysis form works
- [ ] Live monitoring shows real-time logs
- [ ] History tab shows past analyses
- [ ] All tabs render correctly

---

## 🎯 Performance Benchmarks

Expected timing for full pipeline test:

| Phase | Expected Time |
|-------|--------------|
| Sandbox creation | 5-10 seconds |
| Environment setup | 10-15 seconds |
| Agent deployment | 2-5 seconds |
| Vulnerability scanning | 5-10 seconds |
| Exploit generation | 5-10 seconds |
| Exploit execution | 10-20 seconds |
| Report generation | 2-5 seconds |
| GitHub posting | 2-5 seconds |
| **Total** | **40-80 seconds** |

For 4 files with 27 vulnerabilities:
- Expected: ~60 seconds
- If slower: Check network, E2B quota, or MCP server

---

## 🚀 Next Steps

After successful testing:

1. **Extend Detection:**
   - Add new vulnerability patterns to `sandbox_agent/agent.py`
   - Test with different programming languages
   - Add more complex exploit generation

2. **Improve Accuracy:**
   - Reduce false positives with context analysis
   - Add semantic analysis beyond regex
   - Implement machine learning detection

3. **Scale Up:**
   - Test with larger repositories
   - Analyze multiple PRs concurrently
   - Implement caching for faster re-scans

4. **Production Use:**
   - Set up webhook for automatic PR monitoring
   - Deploy dashboard to Streamlit Cloud
   - Configure GitHub Action for CI/CD integration

---

## 📚 Additional Resources

- **README.md** - Project overview and quick start
- **ARCHITECTURE.md** - Detailed architecture documentation
- **SETUP_GUIDE.md** - Complete setup instructions
- **sample_vulnerable_code/README.md** - Vulnerability details and exploit examples

---

**Happy Testing! 🛡️**

If you find any issues or have questions, please check the troubleshooting section or refer to the documentation files.
