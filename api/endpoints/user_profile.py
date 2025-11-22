"""
User Profile API Endpoint
⚠️ WARNING: This code contains intentional security vulnerabilities for demonstration purposes.
DO NOT use in production!
"""

from flask import Flask, request, jsonify, render_template_string
import sqlite3
import os
import subprocess
from pathlib import Path

app = Flask(__name__)

# Database connection (insecure)
DB_PATH = "users.db"

def init_db():
    """Initialize database with vulnerable schema."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            email TEXT,
            password TEXT,
            profile_data TEXT
        )
    """)
    conn.commit()
    conn.close()


@app.route('/api/user/login', methods=['POST'])
def login():
    """
    VULNERABILITY 1: SQL Injection
    User input directly concatenated into SQL query without sanitization.
    """
    username = request.form.get('username')
    password = request.form.get('password')
    
    # VULNERABLE: Direct string interpolation in SQL
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query)  # SQL Injection risk!
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return jsonify({"status": "success", "user_id": user[0]})
    return jsonify({"status": "failed"}), 401


@app.route('/api/user/search', methods=['GET'])
def search_users():
    """
    VULNERABILITY 2: SQL Injection with .format()
    Another SQL injection vulnerability using string formatting.
    """
    search_term = request.args.get('q', '')
    
    # VULNERABLE: Using .format() with user input
    query = "SELECT * FROM users WHERE username LIKE '%{}%' OR email LIKE '%{}%'".format(
        search_term, search_term
    )
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query)  # SQL Injection risk!
    results = cursor.fetchall()
    conn.close()
    
    return jsonify({"users": results})


@app.route('/api/user/<user_id>/profile', methods=['GET'])
def get_profile(user_id):
    """
    VULNERABILITY 3: Path Traversal
    Allows reading arbitrary files from the filesystem.
    """
    # VULNERABLE: No validation of user_id, allows directory traversal
    profile_file = f"profiles/{user_id}.json"
    
    # Even more vulnerable: direct file access
    file_path = os.path.join("data", profile_file)
    
    # VULNERABLE: Can access ../../../etc/passwd
    with open(file_path, 'r') as f:
        profile_data = f.read()
    
    return jsonify({"profile": profile_data})


@app.route('/api/user/upload', methods=['POST'])
def upload_file():
    """
    VULNERABILITY 4: Path Traversal in File Upload
    Allows writing files outside intended directory.
    """
    filename = request.form.get('filename')
    file_content = request.form.get('content')
    
    # VULNERABLE: No sanitization of filename
    upload_path = os.path.join("uploads", filename)
    
    # VULNERABLE: Can write to ../../../etc/passwd or any location
    with open(upload_path, 'w') as f:
        f.write(file_content)
    
    return jsonify({"status": "uploaded", "path": upload_path})


@app.route('/api/system/execute', methods=['POST'])
def execute_command():
    """
    VULNERABILITY 5: Command Injection
    Executes arbitrary system commands from user input.
    """
    command = request.form.get('command')
    
    # VULNERABLE: Direct execution of user input
    result = os.system(command)  # Command injection!
    
    return jsonify({"result": result})


@app.route('/api/system/process', methods=['POST'])
def process_data():
    """
    VULNERABILITY 6: Command Injection with subprocess
    Uses subprocess with shell=True, allowing command injection.
    """
    data = request.form.get('data')
    command = f"python process.py {data}"
    
    # VULNERABLE: shell=True allows command injection
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    return jsonify({"output": result.stdout})


@app.route('/api/system/popen', methods=['POST'])
def popen_command():
    """
    VULNERABILITY 7: Command Injection with os.popen
    Another command injection vector.
    """
    command = request.form.get('cmd')
    
    # VULNERABLE: os.popen with user input
    output = os.popen(command).read()  # Command injection!
    
    return jsonify({"output": output})


@app.route('/api/user/display', methods=['GET'])
def display_user():
    """
    VULNERABILITY 8: Cross-Site Scripting (XSS)
    Renders user input directly in HTML without sanitization.
    """
    user_input = request.args.get('name', 'Guest')
    
    # VULNERABLE: Direct injection of user input into HTML
    template = f"""
    <html>
        <body>
            <h1>Welcome, {user_input}!</h1>
            <div id="content">
                <script>
                    document.write('<p>User: ' + '{user_input}' + '</p>');
                </script>
            </div>
        </body>
    </html>
    """
    
    return render_template_string(template)


@app.route('/api/user/notify', methods=['POST'])
def send_notification():
    """
    VULNERABILITY 9: XSS with innerHTML
    Sets innerHTML with unsanitized user input.
    """
    message = request.form.get('message')
    
    # VULNERABLE: innerHTML with user input
    html_response = f"""
    <html>
        <body>
            <div id="notification"></div>
            <script>
                document.getElementById('notification').innerHTML = '{message}';
            </script>
        </body>
    </html>
    """
    
    return html_response


@app.route('/api/user/eval', methods=['POST'])
def evaluate_expression():
    """
    VULNERABILITY 10: Code Injection with eval()
    Executes arbitrary Python code from user input.
    """
    expression = request.form.get('expression')
    
    # VULNERABLE: eval() with user input allows arbitrary code execution
    result = eval(expression)  # Code injection!
    
    return jsonify({"result": result})


@app.route('/api/user/exec', methods=['POST'])
def execute_code():
    """
    VULNERABILITY 11: Code Injection with exec()
    Executes arbitrary Python code from user input.
    """
    code = request.form.get('code')
    
    # VULNERABLE: exec() with user input allows arbitrary code execution
    exec(code)  # Code injection!
    
    return jsonify({"status": "executed"})


@app.route('/api/user/query', methods=['GET'])
def query_database():
    """
    VULNERABILITY 12: SQL Injection with % formatting
    Another SQL injection pattern using % formatting.
    """
    user_id = request.args.get('id')
    
    # VULNERABLE: % formatting with user input
    query = "SELECT * FROM users WHERE id = %s" % user_id
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query)  # SQL Injection risk!
    user = cursor.fetchone()
    conn.close()
    
    return jsonify({"user": user})


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)

