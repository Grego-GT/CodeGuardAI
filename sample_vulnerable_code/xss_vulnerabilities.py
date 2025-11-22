"""
Cross-Site Scripting (XSS) Vulnerabilities - Example Code
This file contains INTENTIONALLY VULNERABLE code for testing purposes.
DO NOT use this code in production.
"""

from flask import Flask, request, render_template_string, make_response

app = Flask(__name__)

# Vulnerability 1: Reflected XSS - Direct output
@app.route('/greet')
def vulnerable_greet():
    name = request.args.get('name', 'Guest')

    # VULNERABLE: Directly embedding user input in HTML
    html = "<html><body><h1>Hello, " + name + "!</h1></body></html>"
    return html


# Vulnerability 2: Reflected XSS - Template string
@app.route('/search')
def vulnerable_search():
    query = request.args.get('q', '')

    # VULNERABLE: Using f-string with user input
    html = f"""
    <html>
    <body>
        <h1>Search Results</h1>
        <p>You searched for: {query}</p>
        <p>No results found.</p>
    </body>
    </html>
    """
    return html


# Vulnerability 3: Stored XSS - Comment system
comments_db = []

@app.route('/comment', methods=['POST'])
def add_comment():
    comment = request.form.get('comment', '')
    username = request.form.get('username', 'Anonymous')

    # VULNERABLE: Storing unsanitized user input
    comments_db.append({'username': username, 'comment': comment})

    return "Comment added!"


@app.route('/comments')
def show_comments():
    # VULNERABLE: Displaying unsanitized stored data
    html = "<html><body><h1>Comments</h1>"
    for c in comments_db:
        html += f"<div><strong>{c['username']}</strong>: {c['comment']}</div>"
    html += "</body></html>"
    return html


# Vulnerability 4: DOM-based XSS
@app.route('/profile')
def user_profile():
    user_id = request.args.get('id', '1')

    # VULNERABLE: User input directly in JavaScript
    html = f"""
    <html>
    <head>
        <script>
            var userId = '{user_id}';
            document.write('<h1>User Profile: ' + userId + '</h1>');
        </script>
    </head>
    <body></body>
    </html>
    """
    return html


# Vulnerability 5: XSS via innerHTML
@app.route('/dashboard')
def dashboard():
    message = request.args.get('message', 'Welcome!')

    # VULNERABLE: Setting innerHTML with user input
    html = f"""
    <html>
    <body>
        <div id="notification"></div>
        <script>
            document.getElementById('notification').innerHTML = '{message}';
        </script>
    </body>
    </html>
    """
    return html


# Vulnerability 6: XSS in URL redirect
@app.route('/redirect')
def vulnerable_redirect():
    url = request.args.get('url', '/')

    # VULNERABLE: javascript: protocol can be injected
    html = f"""
    <html>
    <body>
        <p>Redirecting to: {url}</p>
        <script>
            window.location = '{url}';
        </script>
    </body>
    </html>
    """
    return html


# SECURE EXAMPLE (for comparison)
from markupsafe import escape

@app.route('/secure_greet')
def secure_greet():
    name = request.args.get('name', 'Guest')

    # SECURE: Escaping user input
    html = f"<html><body><h1>Hello, {escape(name)}!</h1></body></html>"
    return html


if __name__ == '__main__':
    app.run(debug=True)
