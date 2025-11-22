"""
Sample vulnerable code for testing CodeGuard AI.
Contains intentional security vulnerabilities for demonstration.
"""

import os
import sqlite3
from flask import Flask, request, render_template_string

app = Flask(__name__)

# SQL Injection vulnerability
def get_user(user_id):
    """Vulnerable: SQL injection via string formatting."""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # VULNERABLE: Direct string formatting in SQL
    query = f"SELECT * FROM users WHERE id = '{user_id}'"
    cursor.execute(query)
    return cursor.fetchone()

# Command Injection vulnerability
def process_file(filename):
    """Vulnerable: Command injection via os.system."""
    # VULNERABLE: User input directly in system command
    os.system(f"cat {filename}")
    return "File processed"

# XSS vulnerability (simulated in Python context)
def render_user_content(user_input):
    """Vulnerable: XSS via unsanitized user input."""
    # VULNERABLE: User input rendered without sanitization
    template = f"<div>{user_input}</div>"
    return render_template_string(template)

# Path Traversal vulnerability
def read_config(config_path):
    """Vulnerable: Path traversal in file operations."""
    # VULNERABLE: No validation of path traversal
    with open(config_path, 'r') as f:
        return f.read()

# Another SQL Injection example
def search_users(search_term):
    """Vulnerable: SQL injection via string concatenation."""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # VULNERABLE: String concatenation in SQL
    query = "SELECT * FROM users WHERE name LIKE '%" + search_term + "%'"
    cursor.execute(query)
    return cursor.fetchall()

