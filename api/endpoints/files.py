"""
Path Traversal Vulnerabilities - Example Code
This file contains INTENTIONALLY VULNERABLE code for testing purposes.
DO NOT use this code in production.
"""

import os
from flask import Flask, request, send_file

app = Flask(__name__)

# Vulnerability 1: Direct file access with user input
@app.route('/download')
def vulnerable_download():
    filename = request.args.get('file', 'document.txt')

    # VULNERABLE: Direct concatenation allows ../../../etc/passwd
    file_path = "/var/www/files/" + filename

    try:
        return send_file(file_path)
    except Exception as e:
        return f"Error: {e}"


# Vulnerability 2: open() with user-controlled path
@app.route('/read')
def vulnerable_read():
    filename = request.args.get('file', 'readme.txt')

    # VULNERABLE: User can read arbitrary files
    file_path = f"./docs/{filename}"

    try:
        with open(file_path, 'r') as f:
            content = f.read()
        return f"<pre>{content}</pre>"
    except Exception as e:
        return f"Error: {e}"


# Vulnerability 3: os.path.join with untrusted input
@app.route('/image')
def vulnerable_image():
    image_name = request.args.get('name', 'logo.png')

    # VULNERABLE: os.path.join doesn't prevent traversal if input starts with /
    file_path = os.path.join('/var/www/images', image_name)

    return send_file(file_path)


# Vulnerability 4: File upload path traversal
@app.route('/upload', methods=['POST'])
def vulnerable_upload():
    file = request.files.get('file')

    if file:
        # VULNERABLE: Trusting user-provided filename
        filename = file.filename
        save_path = f"./uploads/{filename}"

        file.save(save_path)
        return "File uploaded successfully"

    return "No file provided"


# Vulnerability 5: Template file access
@app.route('/template')
def vulnerable_template():
    template_name = request.args.get('name', 'default')

    # VULNERABLE: User can access any file by using ../
    template_path = f"templates/{template_name}.html"

    try:
        with open(template_path, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Template not found: {e}"


# Vulnerability 6: Log file access
@app.route('/logs')
def vulnerable_logs():
    log_file = request.args.get('file', 'app.log')

    # VULNERABLE: Directory traversal in log access
    log_path = "./logs/" + log_file

    try:
        with open(log_path, 'r') as f:
            logs = f.read()
        return f"<pre>{logs}</pre>"
    except Exception as e:
        return f"Error reading logs: {e}"


# Vulnerability 7: Config file access
def get_config(config_name):
    # VULNERABLE: Reading config files with user input
    config_path = f"/etc/app/config/{config_name}"

    with open(config_path, 'r') as f:
        return f.read()


# Vulnerability 8: Archive extraction
import zipfile

@app.route('/extract', methods=['POST'])
def vulnerable_extract():
    archive = request.files.get('archive')

    if archive:
        # VULNERABLE: Zip slip - extracting without path validation
        extract_path = "./extracted/"

        with zipfile.ZipFile(archive) as zf:
            zf.extractall(extract_path)

        return "Archive extracted successfully"

    return "No archive provided"


# Vulnerability 9: Include files
@app.route('/include')
def vulnerable_include():
    page = request.args.get('page', 'home')

    # VULNERABLE: File inclusion with user input
    include_path = f"./includes/{page}.php"

    try:
        with open(include_path, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error: {e}"


# SECURE EXAMPLES (for comparison)
import os.path

ALLOWED_FILES = ['readme.txt', 'terms.txt', 'privacy.txt']

@app.route('/secure_read')
def secure_read():
    filename = request.args.get('file', 'readme.txt')

    # SECURE: Whitelist approach
    if filename not in ALLOWED_FILES:
        return "File not allowed", 403

    file_path = os.path.join('./docs', filename)

    # Additional check: ensure resolved path is within allowed directory
    docs_dir = os.path.abspath('./docs')
    requested_path = os.path.abspath(file_path)

    if not requested_path.startswith(docs_dir):
        return "Invalid file path", 403

    try:
        with open(requested_path, 'r') as f:
            content = f.read()
        return f"<pre>{content}</pre>"
    except Exception as e:
        return f"Error: {e}"


@app.route('/secure_download')
def secure_download():
    filename = request.args.get('file', 'document.txt')

    # SECURE: Validate filename and use absolute path checking
    # Remove any directory traversal attempts
    safe_filename = os.path.basename(filename)

    base_dir = os.path.abspath('/var/www/files')
    file_path = os.path.join(base_dir, safe_filename)

    # Ensure the resolved path is within the base directory
    if not os.path.abspath(file_path).startswith(base_dir):
        return "Invalid file path", 403

    if not os.path.isfile(file_path):
        return "File not found", 404

    return send_file(file_path)


if __name__ == '__main__':
    app.run(debug=True)
