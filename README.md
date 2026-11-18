# Shift-Left DevSecOps Security Pipeline

An automated CI/CD security pipeline built with **GitHub Actions** that enforces shift-left security gates across the Software Development Life Cycle (SDLC). 

The pipeline runs parallel static, dependency, secret, and dynamic security scans against an intentionally vulnerable containerized **FastAPI** application (`vuln-app`), automatically failing builds when security flaws are detected.

> **Note:** Failing status checks in this repository are intentional. They demonstrate the pipeline actively catching and blocking hardcoded secrets, vulnerable dependencies, insecure code patterns, and runtime misconfigurations.

---

## Pipeline Architecture

All security stages execute in parallel on every `push` and `pull_request` to `main` so developers receive complete feedback in a single run:

| Stage | Tool | Security Focus | Target Flaw in `vuln-app` |
| :--- | :--- | :--- | :--- |
| **Secret Detection** | **Gitleaks** | Scans Git commit history for exposed credentials | Hardcoded AWS & Stripe API keys in `app/main.py` |
| **Dependency Scanning** | **OSV-Scanner** | Audits third-party dependencies against known CVEs | Outdated packages pinned in `requirements.txt` |
| **Static Analysis (SAST)** | **Semgrep & CodeQL** | Analyzes Python AST and dataflow for insecure patterns | SQL Injection (`/users`) & OS Command Injection (`/ping`) |
| **Dynamic Analysis (DAST)** | **OWASP ZAP** | Builds Docker container and probes live HTTP endpoints | Reflected XSS (`/welcome`) & missing security headers |

---

## Project Structure

```text
Pipeline/
├── .github/
│   └── workflows/
│       └── security-pipeline.yml   # Parallel GitHub Actions DevSecOps workflow
├── app/
│   ├── __init__.py
│   └── main.py                     # Intentionally vulnerable FastAPI target
├── Dockerfile                      # Container build definition for DAST stage
└── requirements.txt                # Vulnerable dependency manifest