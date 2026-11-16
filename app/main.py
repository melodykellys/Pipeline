import sqlite3
import subprocess
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse

app = FastAPI(title="Vulnerable AppSec Target")

# 1. FLAW: Hardcoded API Secret (Target: Gitleaks)
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
STRIPE_LIVE_KEY = "sk_live_51N9x82K9LmPqR7vT4wXyZ1234567890abcdef"

# Setup dummy in-memory database
conn = sqlite3.connect(":memory:", check_same_thread=False)
conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, role TEXT)")
conn.execute("INSERT INTO users (username, role) VALUES ('admin', 'superuser'), ('guest', 'viewer')")
conn.commit()


@app.get("/")
def health_check():
    return {"status": "running", "environment": "production"}


# 2. FLAW: SQL Injection via f-string interpolation (Target: Semgrep & CodeQL)
@app.get("/users")
def get_user(username: str = Query(..., description="Username to look up")):
    cursor = conn.cursor()
    query = f"SELECT id, username, role FROM users WHERE username = '{username}'"
    cursor.execute(query)
    results = cursor.fetchall()
    return {"users": results}


# 3. FLAW: OS Command Injection (Target: Semgrep & CodeQL)
@app.get("/ping")
def ping_host(host: str = Query(..., description="Host IP or domain to ping")):
    # Passing user input directly to shell=True allows command chaining (e.g., 127.0.0.1; id)
    output = subprocess.check_output(f"ping -c 1 {host}", shell=True, text=True)
    return {"output": output}


# 4. FLAW: Reflected XSS & Missing Security Headers (Target: OWASP ZAP)
@app.get("/welcome", response_class=HTMLResponse)
def welcome_banner(name: str = "Guest"):
    # Directly rendering unescaped user input into HTML
    html_content = f"""
    <html>
        <head><title>Welcome</title></head>
        <body>
            <h1>Hello, {name}!</h1>
            <p>Welcome to the portal.</p>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)
