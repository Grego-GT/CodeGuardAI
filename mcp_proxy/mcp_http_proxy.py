"""
GitHub MCP HTTP Server
MCP-compatible HTTP server that provides GitHub API access.
Allows E2B sandboxes to connect to GitHub via MCP protocol over HTTP.
"""

from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Get GitHub token from environment
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "GitHub MCP HTTP Server",
        "protocol": "MCP over HTTP"
    })


@app.route('/mcp/tools/list', methods=['GET'])
def list_tools():
    """List available MCP tools."""
    return jsonify({
        "tools": [
            {
                "name": "get_pull_request_files",
                "description": "Get files changed in a pull request",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "owner": {"type": "string"},
                        "repo": {"type": "string"},
                        "pr_number": {"type": "integer"}
                    }
                }
            },
            {
                "name": "create_issue_comment",
                "description": "Create a comment on an issue or pull request",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "owner": {"type": "string"},
                        "repo": {"type": "string"},
                        "issue_number": {"type": "integer"},
                        "body": {"type": "string"}
                    }
                }
            }
        ]
    })


@app.route('/mcp/tools/call', methods=['POST'])
def call_tool():
    """Call an MCP tool."""
    data = request.json
    tool_name = data.get('tool')
    arguments = data.get('arguments', {})

    if tool_name == 'get_pull_request_files':
        return get_pr_files(arguments)
    elif tool_name == 'create_issue_comment':
        return create_pr_comment(arguments)
    else:
        return jsonify({"error": f"Unknown tool: {tool_name}"}), 400


def get_pr_files(args):
    """Fetch PR files via GitHub API."""
    owner = args.get('owner')
    repo = args.get('repo')
    pr_number = args.get('pr_number')

    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        files = response.json()

        # Fetch content for each Python file
        file_changes = []
        for file in files:
            if file['filename'].endswith('.py'):
                raw_url = file.get('raw_url')
                if raw_url:
                    content_response = requests.get(raw_url)
                    file_changes.append({
                        'file': file['filename'],
                        'content': content_response.text,
                        'status': file['status']
                    })

        return jsonify({
            "success": True,
            "files": file_changes
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


def create_pr_comment(args):
    """Create PR comment via GitHub API."""
    owner = args.get('owner')
    repo = args.get('repo')
    issue_number = args.get('issue_number')
    body = args.get('body')

    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/comments"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    try:
        response = requests.post(url, headers=headers, json={"body": body})
        response.raise_for_status()
        comment = response.json()

        return jsonify({
            "success": True,
            "comment_url": comment.get('html_url')
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == '__main__':
    if not GITHUB_TOKEN:
        print("WARNING: GITHUB_TOKEN environment variable not set!")
        print("Set it with: export GITHUB_TOKEN=your_token")
    else:
        print("✓ GitHub token configured")

    print("Starting GitHub MCP HTTP Server on port 8080")
    print("This server provides MCP-compatible HTTP endpoints for GitHub access")
    app.run(host='0.0.0.0', port=8080, debug=False)
