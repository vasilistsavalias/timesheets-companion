# 🛡️ Security Architecture

Security is a primary pillar of this project, ensuring that sensitive financial and personal data is handled responsibly.

## 1. Authentication & Access Control
*   **Invite-Only System:** Public registration is disabled. Users are created exclusively by administrators via the CLI management tool.
*   **Hashed Credentials:** Passwords are never stored in plain text. We use `bcrypt` with a unique salt for every user.
*   **Role-Based Access (RBAC):** Distinct roles for `User` and `Admin`. Administrative features (user management) are strictly gated behind admin status checks.

## 2. Data Privacy (Stateless Processing)
*   **In-Memory Lifecycle:** Uploaded files and generated reports are processed entirely in RAM.
*   **Zero-Disk Footprint:** The server does not write any user data to persistent storage (no `.xlsx` or `.csv` files saved on the server).
*   **Automatic Cleanup:** When a browser session ends, the in-memory data is cleared by the OS/Streamlit garbage collector.

## 3. Secrets & API Security
*   **Environment Isolation:** Sensitive keys (OpenRouter, Database URL) are never committed to version control. They are managed through `.env` files locally and `secrets.toml` in production.
*   **Sanitized Logs:** All logs are reviewed to ensure no PII (Personally Identifiable Information) or raw API payloads are leaked into the logging stream.

## 4. Database Security
*   **Encrypted Connections:** Production database connections (PostgreSQL) are enforced with SSL requirements.
*   **SQL Injection Prevention:** All database queries are executed through SQLAlchemy's parameterized ORM layer.
