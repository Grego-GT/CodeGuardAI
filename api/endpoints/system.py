"""
Command Injection Vulnerabilities - Example Code
This file contains INTENTIONALLY VULNERABLE code for testing purposes.
DO NOT use this code in production.
"""

import os
import subprocess
from flask import Flask, request

app = Flask(__name__)

# Vulnerability 1: os.system() with user input
@app.route('/ping')
def vulnerable_ping():
    host = request.args.get('host', 'localhost')

    # VULNERABLE: Direct user input to os.system()
    command = "ping -c 4 " + host
    result = os.system(command)

    return f"Ping result: {result}"


# Vulnerability 2: subprocess.call() with shell=True
@app.route('/dns_lookup')
def vulnerable_dns():
    domain = request.args.get('domain', 'example.com')

    # VULNERABLE: shell=True with user input
    command = f"nslookup {domain}"
    result = subprocess.call(command, shell=True)

    return f"DNS lookup completed with status: {result}"


# Vulnerability 3: subprocess.run() with shell=True
@app.route('/whois')
def vulnerable_whois():
    domain = request.args.get('domain', 'example.com')

    # VULNERABLE: f-string concatenation with shell=True
    result = subprocess.run(
        f"whois {domain}",
        shell=True,
        capture_output=True,
        text=True
    )

    return result.stdout


# Vulnerability 4: os.popen() with user input
@app.route('/traceroute')
def vulnerable_traceroute():
    host = request.args.get('host', 'google.com')

    # VULNERABLE: os.popen() with user input
    command = "traceroute " + host
    output = os.popen(command).read()

    return f"<pre>{output}</pre>"


# Vulnerability 5: eval() with user input
@app.route('/calculate')
def vulnerable_calculate():
    expression = request.args.get('expr', '1+1')

    # VULNERABLE: eval() allows arbitrary code execution
    try:
        result = eval(expression)
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {e}"


# Vulnerability 6: exec() with user input
@app.route('/execute')
def vulnerable_execute():
    code = request.args.get('code', 'print("Hello")')

    # VULNERABLE: exec() allows arbitrary code execution
    try:
        exec(code)
        return "Code executed"
    except Exception as e:
        return f"Error: {e}"


# Vulnerability 7: String formatting in commands
def backup_file(filename):
    # VULNERABLE: User input in command string
    command = "tar -czf backup.tar.gz {}".format(filename)
    os.system(command)


# Vulnerability 8: subprocess.Popen with shell=True
@app.route('/convert')
def vulnerable_convert():
    input_file = request.args.get('input', 'document.txt')
    output_file = request.args.get('output', 'document.pdf')

    # VULNERABLE: Multiple user inputs with shell=True
    command = f"convert {input_file} {output_file}"
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate()

    return f"Conversion complete: {stdout.decode()}"


# SECURE EXAMPLES (for comparison)
@app.route('/secure_ping')
def secure_ping():
    host = request.args.get('host', 'localhost')

    # SECURE: Using list arguments without shell=True
    try:
        result = subprocess.run(
            ['ping', '-c', '4', host],
            capture_output=True,
            text=True,
            timeout=10
        )
        return f"<pre>{result.stdout}</pre>"
    except subprocess.TimeoutExpired:
        return "Ping timeout"
    except Exception as e:
        return f"Error: {e}"


@app.route('/secure_dns')
def secure_dns():
    domain = request.args.get('domain', 'example.com')

    # SECURE: Whitelist validation + list arguments
    import re
    if not re.match(r'^[a-zA-Z0-9.-]+$', domain):
        return "Invalid domain name"

    result = subprocess.run(
        ['nslookup', domain],
        capture_output=True,
        text=True,
        timeout=5
    )

    return f"<pre>{result.stdout}</pre>"


if __name__ == '__main__':
    app.run(debug=True)
