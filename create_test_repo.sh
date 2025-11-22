#!/bin/bash

# Create Test Repository Script for CodeGuard AI
# This script helps you quickly set up a test GitHub repository with vulnerable code

set -e

echo "=================================================="
echo "CodeGuard AI - Test Repository Setup"
echo "=================================================="
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed."
    echo "Install it from: https://cli.github.com/"
    echo "Or run: brew install gh"
    exit 1
fi

# Check if user is authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ Not authenticated with GitHub CLI."
    echo "Run: gh auth login"
    exit 1
fi

echo "✅ GitHub CLI is installed and authenticated"
echo ""

# Get repository name
read -p "Enter test repository name (default: codeguard-test): " REPO_NAME
REPO_NAME=${REPO_NAME:-codeguard-test}

# Get GitHub username
GH_USER=$(gh api user -q .login)
echo "GitHub username: $GH_USER"
echo ""

# Ask for confirmation
read -p "Create repository '$REPO_NAME' and push test files? (y/n): " CONFIRM
if [ "$CONFIRM" != "y" ]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "🚀 Creating test repository..."

# Create temporary directory
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

# Initialize git repo
git init
git config user.name "$GH_USER"
git config user.email "$(git config user.email || echo 'test@example.com')"

# Create directory structure
mkdir -p api

# Copy vulnerable files
echo "📁 Copying vulnerable code samples..."
cp "$OLDPWD/sample_vulnerable_code/sql_injection.py" ./api/database.py
cp "$OLDPWD/sample_vulnerable_code/xss_vulnerabilities.py" ./api/search.py
cp "$OLDPWD/sample_vulnerable_code/command_injection.py" ./api/system.py
cp "$OLDPWD/sample_vulnerable_code/path_traversal.py" ./api/files.py

# Create a simple README
cat > README.md << 'EOF'
# CodeGuard AI Test Repository

This is a test repository for demonstrating CodeGuard AI's security scanning capabilities.

⚠️ **WARNING**: This repository contains intentionally vulnerable code for testing purposes.

## Files

- `api/database.py` - SQL injection vulnerabilities
- `api/search.py` - XSS vulnerabilities
- `api/system.py` - Command injection vulnerabilities
- `api/files.py` - Path traversal vulnerabilities

## Testing with CodeGuard AI

1. Create a pull request adding one or more of these files
2. Run CodeGuard AI against the PR
3. Review the security findings

**DO NOT use this code in production!**
EOF

# Create initial commit
git add .
git commit -m "Initial commit: Add test API files

This commit adds API endpoints with various security issues
for testing CodeGuard AI's vulnerability detection."

# Create GitHub repository
echo "🌐 Creating GitHub repository..."
gh repo create "$REPO_NAME" --public --source=. --remote=origin --push

echo ""
echo "✅ Repository created successfully!"
echo ""
echo "Repository URL: https://github.com/$GH_USER/$REPO_NAME"
echo ""

# Create a test branch and PR
echo "🌿 Creating test branch with vulnerable code..."
git checkout -b add-api-endpoints

# Make a small change to create a diff
echo "# API Implementation" >> README.md
git add README.md
git commit -m "Add API implementation notes"

git push origin add-api-endpoints

echo "📝 Creating pull request..."
PR_URL=$(gh pr create \
    --title "Add API endpoints" \
    --body "This PR adds new API endpoints for the application.

**Files changed:**
- \`api/database.py\` - Database query endpoints
- \`api/search.py\` - Search functionality
- \`api/system.py\` - System administration endpoints
- \`api/files.py\` - File management endpoints

Please review for security issues." \
    --base main \
    --head add-api-endpoints)

echo ""
echo "=================================================="
echo "✅ Setup Complete!"
echo "=================================================="
echo ""
echo "Repository: https://github.com/$GH_USER/$REPO_NAME"
echo "Pull Request: $PR_URL"
echo ""
echo "Next steps:"
echo "1. Run CodeGuard AI against this PR:"
echo "   python orchestrator.py $GH_USER $REPO_NAME 1 <your-github-token>"
echo ""
echo "2. Or use the Streamlit dashboard:"
echo "   streamlit run dashboard.py"
echo "   Then analyze: $GH_USER / $REPO_NAME / PR #1"
echo ""
echo "3. Check the PR for CodeGuard AI's security report!"
echo ""
echo "Temporary directory: $TEMP_DIR"
echo "(You can delete this after testing)"
echo ""
