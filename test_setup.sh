#!/bin/bash
# Quick setup test script for CodeGuard AI

echo "🛡️  CodeGuard AI - Setup Test Script"
echo "======================================"
echo ""

# Check Python version
echo "1. Checking Python version..."
python_version=$(python --version 2>&1)
echo "   ✓ $python_version"
echo ""

# Check Docker
echo "2. Checking Docker..."
if command -v docker &> /dev/null; then
    docker_version=$(docker --version)
    echo "   ✓ $docker_version"
else
    echo "   ✗ Docker not found. Please install Docker."
    exit 1
fi
echo ""

# Check Docker Compose
echo "3. Checking Docker Compose..."
if command -v docker-compose &> /dev/null; then
    compose_version=$(docker-compose --version)
    echo "   ✓ $compose_version"
else
    echo "   ✗ Docker Compose not found. Please install Docker Compose."
    exit 1
fi
echo ""

# Check config.json
echo "4. Checking configuration..."
if [ -f "config.json" ]; then
    echo "   ✓ config.json found"

    # Check for E2B API key
    if grep -q "e2b_api_key" config.json; then
        echo "   ✓ E2B API key configured"
    else
        echo "   ⚠ E2B API key not found in config.json"
    fi

    # Check for GitHub token
    if grep -q "github_token" config.json; then
        echo "   ✓ GitHub token configured"
    else
        echo "   ⚠ GitHub token not found in config.json"
    fi
else
    echo "   ✗ config.json not found"
    echo "   → Please create config.json with your API keys"
    echo ""
    echo "   Example config.json:"
    echo "   {"
    echo "     \"e2b_api_key\": \"your_e2b_key\","
    echo "     \"github_token\": \"your_github_token\""
    echo "   }"
    exit 1
fi
echo ""

# Check Python dependencies
echo "5. Checking Python dependencies..."
if python -c "import streamlit" 2>/dev/null; then
    echo "   ✓ streamlit installed"
else
    echo "   ✗ streamlit not installed"
    echo "   → Run: pip install -r requirements.txt"
    exit 1
fi

if python -c "import e2b_code_interpreter" 2>/dev/null; then
    echo "   ✓ e2b-code-interpreter installed"
else
    echo "   ✗ e2b-code-interpreter not installed"
    echo "   → Run: pip install -r requirements.txt"
    exit 1
fi

if python -c "import httpx" 2>/dev/null; then
    echo "   ✓ httpx installed"
else
    echo "   ✗ httpx not installed"
    echo "   → Run: pip install -r requirements.txt"
    exit 1
fi
echo ""

# Check GitHub MCP server
echo "6. Checking GitHub MCP Server..."
if docker ps | grep -q "codeguard-github-mcp"; then
    echo "   ✓ GitHub MCP server is running"
else
    echo "   ⚠ GitHub MCP server not running"
    echo "   → Run: docker-compose up -d"
fi
echo ""

echo "======================================"
echo "✅ Setup check complete!"
echo ""
echo "Next steps:"
echo "  1. If any items are marked with ✗, fix them first"
echo "  2. Start GitHub MCP server: docker-compose up -d"
echo "  3. Launch dashboard: streamlit run dashboard.py"
echo "  4. Open http://localhost:8501"
echo ""
echo "Happy hacking! 🚀"
