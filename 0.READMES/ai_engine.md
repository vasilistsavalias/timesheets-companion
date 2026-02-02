# 🧠 The AI Engine

This application employs a hybrid intelligence strategy to provide both flexible reasoning and mathematical precision.

## 1. Structural Scraper
The system first performs a deep scan of the raw Webrescom portal paste. 
*   **Logic:** Uses advanced Regular Expressions (Regex) to map the hierarchy of Work Packages (EE) to specific Deliverables (Π).
*   **Agnosticism:** It does not assume a fixed number of deliverables; it counts and maps them dynamically for every project.

## 2. OpenRouter Integration
We outsource complex semantic understanding to high-performance open-source models via the OpenRouter gateway.
*   **Reasoning:** The LLM is used to summarize findings for user verification, ensuring the "human in the loop" is confident in the data extraction.
*   **Context Injection:** The engine automatically feeds project manuals (PDFs) and UI structures into the model's system prompt to "train" it on the fly.

## 3. Strict Compliance Logic
To prevent "hallucinations" in critical financial data, we do **not** use the AI for mathematical calculations.
*   **Mechanism:** Once the structure is confirmed, a hardcoded Python engine takes over.
*   **Mathematical Rules:** 
    *   Targets are extracted from Niki's budget Excel.
    *   Hours are distributed using a greedy algorithm targeting 7.0h blocks.
    *   Compliance check: Skips weekends and Greek holidays programmatically using the `holidays` library and hardcoded ELKE rules.

## 4. Model Pool (Failover)
To ensure high availability, the application maintains a pool of free models. If the primary model (e.g., Llama 3.3) is unavailable, the system automatically fails over to alternatives like DeepSeek R1 or GPT-OSS.
