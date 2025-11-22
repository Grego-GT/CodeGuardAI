# CodeGuard AI Demo Workflow

This guide shows how to use **this same repository** for both the CodeGuard AI application and the demo PR scanning.

## 🎯 What We've Set Up

✅ Created branch `demo-vulnerable-api` with vulnerable code
✅ Added 4 API endpoint files with 27+ vulnerabilities
✅ Pushed to GitHub
📝 Ready to create PR and scan!

## 📋 Step-by-Step Demo

### Step 1: Create the Pull Request

Visit this URL to create the PR:
```
https://github.com/Grego-GT/CodeGuardAI/pull/new/demo-vulnerable-api
```

Or create it manually:
1. Go to: https://github.com/Grego-GT/CodeGuardAI
2. Click "Pull requests" → "New pull request"
3. Base: `main` ← Compare: `demo-vulnerable-api`
4. Click "Create pull request"
5. Title: **"Add API Endpoints for User Management"**
6. Add description (optional)
7. Click "Create pull request"

**Note the PR number** (it will be shown as #X)

---

### Step 2: Start the GitHub MCP Server

```bash
# Make sure Docker is running
docker compose up -d

# Verify it's running
docker ps | grep github-mcp
```

Expected output:
```
codeguard-github-mcp   ghcr.io/github/github-mcp-server:latest   Up   0.0.0.0:8080->8080/tcp
```

---

### Step 3: Run CodeGuard AI Against Your PR

#### Option A: Using the Orchestrator (CLI)

```bash
# Get your config ready
cat config.json  # Should have e2b_api_key and github_token

# Run the analysis
python orchestrator.py Grego-GT CodeGuardAI <PR_NUMBER> <YOUR_GITHUB_TOKEN>

# Example (if PR is #2):
python orchestrator.py Grego-GT CodeGuardAI 2 ghp_xxxxxxxxxxxxxxxxxxxx
```

#### Option B: Using the Dashboard (GUI)

```bash
# Start the dashboard
streamlit run dashboard.py
```

Then in your browser (http://localhost:8501):

1. Go to **"New Analysis"** tab
2. Enter:
   - **Repository Owner**: `Grego-GT`
   - **Repository Name**: `CodeGuardAI`
   - **PR Number**: `<the PR number you created>`
3. Click **"Launch Analysis"**
4. Switch to **"Live Monitor"** tab to watch progress in real-time

---

### Step 4: Watch the Magic Happen ✨

CodeGuard AI will:

1. **Create E2B Sandbox** (~10 seconds)
   ```
   🚀 Creating E2B sandbox...
   ✓ Sandbox created
   ```

2. **Setup Environment** (~15 seconds)
   ```
   Setting up sandbox environment...
   ✓ pip install httpx completed
   ```

3. **Deploy Agent** (~5 seconds)
   ```
   Deploying agent code to sandbox...
   ✓ Agent code deployed
   ```

4. **Scan for Vulnerabilities** (~10 seconds)
   ```
   🔍 Starting security analysis inside sandbox...
   Scanning api/endpoints/database.py...
   Found SQL injection vulnerability at line 16
   Found SQL injection vulnerability at line 31
   ...
   ```

5. **Generate & Test Exploits** (~20 seconds)
   ```
   Generating exploit for SQL injection...
   Testing exploit...
   ✅ Exploit successful!
   ```

6. **Post Report to PR** (~5 seconds)
   ```
   Posting security report to GitHub PR...
   ✅ Analysis complete!
   ```

---

### Step 5: View the Results

**In the PR on GitHub:**
1. Go to your PR: https://github.com/Grego-GT/CodeGuardAI/pull/<PR_NUMBER>
2. Scroll down to the comments section
3. You should see a detailed security report from CodeGuard AI

**Expected Report Format:**
```markdown
## 🛡️ CodeGuard AI Security Report

**Analysis Date:** 2024-01-15 10:30:00 UTC

### Summary
- **Files Scanned:** 4
- **Vulnerabilities Found:** 27
- **Severity:** 🔴 Critical

### Vulnerabilities by File

#### 🔴 api/endpoints/database.py
- SQL Injection (4 instances) - HIGH severity
- Lines: 16, 31, 44, 57

#### 🔴 api/endpoints/search.py
- Cross-Site Scripting (6 instances) - MEDIUM/HIGH severity
- Lines: 14, 22, 40, 48, 57, 73, 87

#### 🔴 api/endpoints/system.py
- Command Injection (8 instances) - CRITICAL severity
- Lines: 15, 26, 36, 49, 60, 71, 81, 90

#### 🔴 api/endpoints/files.py
- Path Traversal (9 instances) - HIGH severity
- Lines: 14, 26, 38, 48, 62, 76, 88, 97, 112

---

[Detailed findings for each vulnerability...]
```

---

## 🧪 What Gets Scanned

The PR includes these files with intentional vulnerabilities:

| File | Original | Vulnerabilities | Description |
|------|----------|----------------|-------------|
| `api/endpoints/database.py` | `sql_injection.py` | 4 SQL injection | String concat, f-strings, format() |
| `api/endpoints/search.py` | `xss_vulnerabilities.py` | 6 XSS | Reflected, stored, DOM-based |
| `api/endpoints/system.py` | `command_injection.py` | 8 Command injection | os.system, eval, exec |
| `api/endpoints/files.py` | `path_traversal.py` | 9 Path traversal | File access, uploads |

**Total: 27+ vulnerabilities across 4 security categories**

---

## 🎬 Demo Talking Points

When demonstrating CodeGuard AI:

### 1. **Problem Statement**
"Traditional security tools either:
- Only do static analysis without proving vulnerabilities work
- Can't safely execute exploits
- Don't integrate into developer workflows

CodeGuard AI solves this by running security agents inside E2B sandboxes."

### 2. **Show the PR**
"Here's a typical PR adding new API endpoints. Looks normal, right?
Let's see what CodeGuard AI finds..."

### 3. **Launch Analysis**
"I'll launch the analysis. Notice how CodeGuard AI:
- Creates an isolated E2B sandbox
- Deploys the security agent inside
- Scans the code for vulnerabilities
- Actually executes exploits to prove they work
- All safely inside the sandbox!"

### 4. **Live Monitoring**
"You can watch in real-time as the agent:
- Detects each vulnerability
- Generates proof-of-concept exploits
- Tests them safely
- This takes about 60 seconds total"

### 5. **Show Results**
"Now look at the PR. CodeGuard AI has posted a detailed report:
- 27 vulnerabilities found across 4 categories
- Exact line numbers
- Proof that exploits work
- Remediation recommendations
- All automatically!"

### 6. **Key Innovation**
"The magic is that the agent runs INSIDE the E2B sandbox, not outside.
It uses MCP to connect to GitHub for fetching files and posting results.
This architecture enables safe exploit testing at scale."

---

## 🔄 Reset and Run Again

If you want to test again or show to different people:

### Keep the Same PR
```bash
# Just run CodeGuard AI again
python orchestrator.py Grego-GT CodeGuardAI <PR_NUMBER> <TOKEN>
```

### Create a New PR
```bash
# Make a small change to the branch
git checkout demo-vulnerable-api
echo "# Updated $(date)" >> api/README.md
git add api/README.md
git commit -m "Update API documentation"
git push

# This will update the existing PR, or create a new branch:
git checkout -b demo-vulnerable-api-v2
git push -u origin demo-vulnerable-api-v2
# Then create new PR via GitHub web UI
```

### Clean Up
```bash
# Delete the demo branch (locally and remotely)
git checkout main
git branch -D demo-vulnerable-api
git push origin --delete demo-vulnerable-api

# Close/delete the PR on GitHub
# Then you can start fresh
```

---

## 🐛 Troubleshooting

### "E2B API key not found"
```bash
# Check your config.json
cat config.json

# Should contain:
{
  "e2b_api_key": "e2b_...",
  "github_token": "ghp_..."
}
```

### "GitHub MCP server connection failed"
```bash
# Restart the MCP server
docker compose down
docker compose up -d

# Check logs
docker compose logs -f github-mcp
```

### "No vulnerabilities found"
```bash
# Verify the files are in the PR
git diff main...demo-vulnerable-api --name-only

# Should show:
# api/endpoints/database.py
# api/endpoints/files.py
# api/endpoints/search.py
# api/endpoints/system.py
```

### "Agent execution timeout"
```bash
# E2B might be slow or quota exceeded
# Check E2B dashboard: https://e2b.dev/dashboard
# Or increase timeout in orchestrator.py
```

---

## 📊 Expected Performance

| Metric | Expected Value |
|--------|---------------|
| Total execution time | 40-80 seconds |
| Sandbox creation | 5-10 seconds |
| Environment setup | 10-15 seconds |
| Vulnerability scanning | 5-10 seconds |
| Exploit testing | 10-20 seconds |
| Report generation | 2-5 seconds |
| GitHub posting | 2-5 seconds |

---

## 🎯 Success Criteria

✅ All 27+ vulnerabilities detected
✅ Exploits generated and tested
✅ Report posted to PR automatically
✅ Detailed findings with line numbers
✅ Remediation advice included
✅ Complete in under 2 minutes

---

## 📚 Additional Resources

- **Repository**: https://github.com/Grego-GT/CodeGuardAI
- **Sample Code Details**: `sample_vulnerable_code/README.md`
- **Architecture Docs**: `ARCHITECTURE.md`
- **Full Testing Guide**: `TESTING_GUIDE.md`

---

**You're all set! 🚀**

Create the PR and run CodeGuard AI to see it in action!
