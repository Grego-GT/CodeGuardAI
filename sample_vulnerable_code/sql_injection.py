"""
SQL Injection Vulnerabilities - Example Code
This file contains INTENTIONALLY VULNERABLE code for testing purposes.
DO NOT use this code in production.
"""

import sqlite3
from flask import Flask, request

app = Flask(__name__)

# Vulnerability 1: Direct SQL concatenation
@app.route('/login')
def vulnerable_login():
    username = request.args.get('username')
    password = request.args.get('password')

    # VULNERABLE: Direct string concatenation
    query = "SELECT * FROM users WHERE username='" + username + "' AND password='" + password + "'"

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(query)
    result = cursor.fetchone()

    if result:
        return "Login successful"
    return "Login failed"


# Vulnerability 2: f-string SQL injection
@app.route('/search')
def vulnerable_search():
    search_term = request.args.get('q')

    # VULNERABLE: Using f-string for SQL query
    query = f"SELECT * FROM products WHERE name LIKE '%{search_term}%'"

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()

    return str(results)


# Vulnerability 3: .format() SQL injection
@app.route('/user/<user_id>')
def get_user(user_id):
    # VULNERABLE: Using .format() for SQL query
    query = "SELECT * FROM users WHERE id = {}".format(user_id)

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(query)
    user = cursor.fetchone()

    return str(user)


# Vulnerability 4: % formatting SQL injection
def get_orders_by_status(status):
    # VULNERABLE: Using % formatting
    query = "SELECT * FROM orders WHERE status = '%s'" % status

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(query)
    orders = cursor.fetchall()

    return orders


# SECURE EXAMPLE (for comparison)
@app.route('/secure_login')
def secure_login():
    username = request.args.get('username')
    password = request.args.get('password')

    # SECURE: Using parameterized query
    query = "SELECT * FROM users WHERE username=? AND password=?"

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(query, (username, password))
    result = cursor.fetchone()

    if result:
        return "Login successful"
    return "Login failed"


if __name__ == '__main__':
    app.run(debug=True)
