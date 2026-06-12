# 🧬 Agentic Author: Autonomous AI Research Engine

> **Autonomous Multi-Agent Studio for Academic-Grade Research and Content Generation.**

[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/Framework-LangGraph-orange.svg)](https://github.com/langchain-ai/langgraph)
[![Gemini 1.5 Flash](https://img.shields.io/badge/LLM-Gemini%201.5%20Flash-red.svg)](https://aistudio.google.com/)
[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)

Agentic Author is an advanced multi-agent system designed to automate the heavy lifting of academic research and technical writing. By orchestrating specialized AI agents through a stateful graph, it transforms a simple niche or topic into a peer-review quality blog post, complete with citations and historical context.

---

## 🚀 Core Features

*   **Self-Correction via Reflection Loops:** A dedicated Critic node evaluates every draft against rigorous technical rubrics, triggering automatic revisions (up to 3 loops) to eliminate "AI fluff" and ensure technical accuracy.
*   **Academic Bibliographic Memory:** Powered by **ChromaDB**, the system maintains a persistent "Knowledge Vault" of past blogs and Arxiv papers, allowing it to build upon past research rather than repeating it.
*   **Context-Aware Strategy:** A Strategist node analyzes your past work to suggest unique technical angles, ensuring every new publication provides fresh value.
*   **BYOK (Bring Your Own Key) Model:** Architected for the free tier, allowing users to provide their own Gemini and Tavily keys directly in the UI or via `.env`.
*   **Token-Optimized Distillation:** A specialized Distiller node compresses massive research datasets into high-density fact sheets, preventing context overflow and reducing API usage.

---

## 🛠️ Tech Stack

### **Core Frameworks**
*   **Orchestration:** [LangGraph](https://github.com/langchain-ai/langgraph) (Stateful multi-agent workflows)
*   **Brain (LLM):** [Gemini 1.5 Flash](https://aistudio.google.com/) (High-speed, large-context LLM via LangChain)
*   **UI/Frontend:** [Streamlit](https://streamlit.io/) (Enterprise-grade dashboard)

### **Data & Memory**
*   **Vector DB:** [ChromaDB](https://www.trychroma.com/) (On-disk persistent vector storage for "Knowledge Vault")

### **Research Tools**
*   **Web Search:** [Tavily AI](https://tavily.com/) (Technical web search)
*   **Academic Search:** [Arxiv API](https://arxiv.org/help/api/index) (Querying academic papers)

### **Utilities**
*   **Schema & Validation:** [Pydantic](https://docs.pydantic.dev/) (Strict type safety for AgentState)
*   **Embeddings:** [Google Gemini Embedding v2](https://ai.google.dev/gemini-api/docs/embeddings)
*   **Configuration:** Python Dotenv

---

## 🧠 System Architecture

The workflow is managed as a stateful graph where each node represents a specialized agent:

1.  **Discovery Agent:** Checks niche alignment and suggests trending topics based on project history.
2.  **Strategist Agent:** Develops a structured content plan and generates targeted research queries.
3.  **Researcher Agent:** Fetches data from Arxiv (primary) and Tavily (fallback), gathering technical evidence.
4.  **Distiller Agent:** Synthesizes raw research notes into a high-density "Technical Fact Sheet."
5.  **Writer Agent:** Crafts the full blog post in a user-selected style (e.g., Paper-to-Practice, Deep-Dive).
6.  **Critic Agent:** Conducts a quality check; if technical rigor is lacking, it sends feedback back to the Writer for revision.
7.  **Publisher Agent:** Finalizes metadata, extracts references, and prepares the post for the Knowledge Vault.

---

## 🏁 Getting Started

### 1. Prerequisites
*   Python 3.13+
*   Google Gemini API Key
*   Tavily API Key

### 2. Clone the Repository
```bash
git clone https://github.com/the-pika/agentic-author.git
cd agentic-author
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
1.  Copy the example environment file:
    ```bash
    cp .env.example .env
    ```
2.  Open `.env` and fill in your API keys:
    ```bash
    GOOGLE_API_KEY="your_gemini_api_key"
    TAVILY_API_KEY="your_tavily_api_key"
    ```

### 5. Run the Application
```bash
streamlit run app.py
```

---

## 🛠️ Utility Scripts

*   **`reset_db.py`**: Hard reset of the local ChromaDB. Deletes the `./chroma_db` folder.
*   **`reset_db_polite.py`**: Soft reset. Uses the ChromaDB API to delete all collections without deleting the folder. Useful if you encounter "File in use" errors on Windows.

---

## ⚖️ Licensing

This project is licensed under the **Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)**.

Full license details can be found [here](https://creativecommons.org/licenses/by-nc/4.0/).

---

*Built with ❤️ for the AI Research Community.*
