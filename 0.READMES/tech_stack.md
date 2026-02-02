# 🛠️ Tech Stack

This project is built with a modern, modular Python stack designed for security, scalability, and ease of deployment.

## Core Technologies
*   **Language:** Python 3.11+
*   **Web Framework:** [Streamlit](https://streamlit.io/) - Used for the interactive AI Assistant interface.
*   **Data Processing:** [Pandas](https://pandas.pydata.org/) & [Openpyxl](https://openpyxl.readthedocs.io/) - For robust Excel parsing and generation.
*   **Database (ORM):** [SQLAlchemy](https://www.sqlalchemy.org/) - Abstraction layer for database interactions (PostgreSQL/SQLite).
*   **Authentication:** [Bcrypt](https://pypi.org/project/bcrypt/) - Industry-standard password hashing for user security.
*   **Logging:** [Loguru](https://github.com/Delgan/loguru) - Professional-grade structured logging and debugging.

## AI & Intelligence
*   **Orchestration:** [OpenRouter API](https://openrouter.ai/) - Unified gateway to access high-performance open-source models.
*   **Primary Model:** `meta-llama/llama-3.3-70b-instruct:free` (or equivalent open-source reasoning model).
*   **Logic Type:** Hybrid (AI-driven structural parsing + Strict programmatic mathematical distribution).

## Deployment & DevOps
*   **Statelessness:** The application is designed to be stateless, processing all files in RAM (`io.BytesIO`) to ensure data privacy and compatibility with ephemeral cloud environments.
*   **Secrets Management:** Environment variables managed via `python-dotenv` and Streamlit Secrets.
