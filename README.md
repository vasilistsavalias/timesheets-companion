# timesheets-companion - Modular Timesheet Automation

**timesheets-companion** is a professional, secure, and modular Streamlit application designed to automate monthly research timesheets for timesheets-companion projects. It leverages AI reasoning (via OpenRouter) and strict programmatic logic to ensure 100% financial and rule compliance.

## 🚀 Key Features

* **Agnostic Data Parsing**: Dynamically extracts budget targets from Excel and structural hierarchy from Webrescom UI pastes.
* **Strict Compliance**: Enforces 0.5h rounding, skips holidays/weekends, and respects 2-6h daily ranges.
* **In-Memory Processing**: Stateless design ensures zero-disk footprint; files are processed entirely in RAM.
* **Secure Authentication**: Role-based access control with hashed passwords (Bcrypt) and PostgreSQL integration.

## 📂 Architecture Overview

Following professional standards (inspired by "Hop-On Companion"):

* `run.py`: The main entry point. Handles routing and initialization.
* `src/database/`: SQLAlchemy ORM layer and Neon/Postgres connection pooling.
* `src/services/`: Modular business logic (Auth, AI interaction, Timesheet generation).
* `src/components/`: Reusable Streamlit UI components (Sidebar, Dashboard, Profile).
* `src/core/`: The mathematical engine and calendar utilities.
* `src/io/`: Robust file parsers and exporters for Excel handling.
*   `scripts/`: Administrative CLI tools for user management.

## 📚 Documentation
Detailed architectural and logic guides can be found in the `0.READMES/` folder:
*   [**Tech Stack**](./0.READMES/tech_stack.md) - Core technologies and logic frameworks.
*   [**Security Architecture**](./0.READMES/security.md) - Authentication, data privacy, and secrets.
*   [**AI Engine & Intelligence**](./0.READMES/ai_engine.md) - Scrapers, LLM integration, and compliance rules.

## 🛠️ Setup & Deployment

### 1. Requirements

```bash
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the root:

```env
DATABASE_URL=postgresql://user:pass@host:5432/dbname
OPENROUTER_API_KEY=sk-or-v1-...
```

### 3. Initialize Database & Admin

```bash
python scripts/manage_users.py add admin yourpassword --admin --name "Administrator"
```

### 4. Run Application

```bash
python streamlit_app.py
```

## 🧪 Testing

Run the automated test suite to verify the logic:

```bash
pytest tests/
```

---
**Disclaimer:** This tool is for administrative assistance only. Always verify generated files before official submission.
