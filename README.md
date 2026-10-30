# 👻 GhostText

### AI Document Forensics & Hidden Instruction Detector

GhostText is a cybersecurity project designed to analyze PDF and DOCX documents for potentially suspicious instructions, unusual Unicode characters, and other document indicators.

It combines rule-based detection, document extraction, risk scoring, and analysis history in a web-based dashboard.

> **Disclaimer:** GhostText is a heuristic analysis tool. Its findings are indicators for further investigation, not proof of malicious activity. A clean result does not guarantee that a document is safe.

---

## ✨ Features

- 📄 **Document Analysis** — Upload PDF and DOCX files for analysis.
- 🔎 **Suspicious Instruction Detection** — Identify potentially suspicious instruction patterns.
- 🔤 **Unicode Analysis** — Detect unusual Unicode characters.
- 🕵️ **PDF Inspection** — Check for hidden text and suspicious metadata indicators.
- ⚖️ **Risk Scoring** — Assign risk levels based on detected findings.
- 🔐 **User Authentication** — Register and log in using password hashing and signed sessions.
- 📚 **Analysis History** — View and clear your own analysis history.
- 📊 **Web Dashboard** — Review findings through a browser interface.
- 📤 **JSON Export** — Export analysis results as JSON.
- 🧪 **Automated Tests** — Verify application behavior with pytest.
- 🐳 **Docker Support** — Includes a Dockerfile for containerization.

## 🛠️ Technology Stack

- **Backend:** Python, FastAPI
- **Frontend:** HTML, CSS, JavaScript
- **Database:** SQLite
- **Document Processing:** PyMuPDF, python-docx
- **Authentication:** Argon2, ItsDangerous
- **Testing:** pytest
- **Deployment:** Docker

## 📁 Project Structure

```text
ghosttext/
├── app/
│   ├── auth.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── analyzer.py
│   ├── document_extractor.py
│   ├── detectors/
│   └── routes/
├── static/
│   ├── index.html
│   ├── css/
│   └── js/
├── tests/
├── samples/
├── scripts/
├── .env.example
├── .gitignore
├── Dockerfile
├── requirements.txt
└── README.md
```

## ⚙️ Requirements

- Python 3.11 or a compatible version supported by your dependencies
- Git
- Windows, Linux, or macOS

## 🚀 Installation

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd ghosttext
```

Replace `YOUR_GITHUB_REPOSITORY_URL` with your repository's actual URL after publishing it.

### 2. Create a virtual environment

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux/macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure the session secret

Set a unique session secret before starting the application.

**Windows PowerShell:**

```powershell
$env:GHOSTTEXT_SESSION_SECRET = python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Keep this value private. For persistent deployments, configure a stable secret using your deployment platform's environment-variable settings.

For HTTPS deployments, configure:

```text
GHOSTTEXT_HTTPS=true
```

Only set this to `true` when the application is accessed through HTTPS.

## ▶️ Run GhostText

Start the development server:

```bash
python -m uvicorn app.main:app --reload
```

Open the dashboard:

```text
http://127.0.0.1:8000
```

API documentation is available during development at:

```text
http://127.0.0.1:8000/docs
```

## 🧪 Run Tests

Execute the automated test suite:

```bash
python -m pytest -v
```

## 🔐 Security Notes

- Passwords are hashed using Argon2.
- Session tokens are signed.
- Session cookies use `HttpOnly` and `SameSite=Lax`.
- Uploads are limited by the configured maximum file size and allowed extensions.
- Analysis history is associated with the authenticated user.
- Uploaded documents should be treated as untrusted input.
- Keep `.env` files, session secrets, databases containing private data, and other sensitive information out of version control.
- Additional security review is necessary before exposing the application to the public internet.

## ⚠️ Limitations

- Detection relies on heuristics and known patterns.
- False positives and false negatives are possible.
- The tool analyzes extracted document content and selected PDF properties; it does not prove that a document is harmless.
- Results should be reviewed by a human before making security decisions.

## 🎯 Project Goal

GhostText explores document security and the detection of potentially suspicious instructions in documents. It is intended as a learning and portfolio project for cybersecurity, secure application development, and document forensics.

## 📜 License

Choose and add a license before permitting others to reuse or distribute this project.
