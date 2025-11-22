#!/bin/bash
# Start GitHub MCP Server with token from config.json

set -e

echo "🚀 Starting GitHub MCP Server..."

# Check if config.json exists
if [ ! -f "config.json" ]; then
    echo "❌ Error: config.json not found"
    echo "Please create config.json with your github_token"
    exit 1
fi

# Extract GitHub token from config.json
GITHUB_TOKEN=$(jq -r '.github_token' config.json)

if [ -z "$GITHUB_TOKEN" ] || [ "$GITHUB_TOKEN" = "null" ]; then
    echo "❌ Error: github_token not found in config.json"
    exit 1
fi

echo "✓ GitHub token found in config.json"

# Export token and start docker-compose
export GITHUB_TOKEN

# Stop any existing containers
docker compose down 2>/dev/null || true

# Start the MCP server
docker compose up -d

echo ""
echo "✅ GitHub MCP Server started!"
echo ""
echo "Check status:"
echo "  docker ps | grep github-mcp"
echo ""
echo "Check logs:"
echo "  docker logs -f codeguard-github-mcp"
echo ""
