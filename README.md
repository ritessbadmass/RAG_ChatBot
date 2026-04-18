# Mutual Fund AI Assistant (Facts-Only MVP)

A compliance-first, retrieval-augmented generation (RAG) chatbot designed to retrieve verifiable, objective facts about Mutual Funds. This Proof-of-Concept is styled as a native platform integration for wealth tech applications (inspired by the design language of Kuvera) and focuses heavily on FinTech guardrails.

## 🎯 Product Objective
In FinTech, LLM "hallucinations" pose severe regulatory risks. The objective of this project is to build an AI assistant that categorically **refuses to give financial advice** or subjective comparisons, instead providing ONLY hard, verifiable facts derived from official Asset Management Company (AMC) documents.

## 🛠️ Architecture & Product Tradeoffs

### 1. Zero-Memory Fallback RAG Architecture
To guarantee 100% uptime within a strict 512MB RAM hosting constraint (Render Free Tier), we bypassed heavy, memory-intensive ML embedding models (like ChromaDB/FastEmbed). Instead, we optimized the RAG pipeline to use a lightweight, deterministic structured-search mechanism. This guarantees high availability (no Out-Of-Memory crashes) while maintaining context-accurate retrieval.

### 2. Pre-LLM Compliance Classifier
Before user input ever reaches the generative LLM, it passes through a strict `QueryClassifier`. If a prompt seeks investment advice, portfolio comparisons, or predictions (e.g., *"Should I buy HDFC Flexi Cap?"*), the system instantly forces an `ADVISORY_REFUSAL` payload. It refuses to answer and redirects users to educational resources provided by SEBI and AMFI.

### 3. Stateless Privacy
The Next.js frontend is entirely stateless. There are no logins, no persistence of Personally Identifiable Information (PII), and no tracking.

## 📊 Scoped Corpus (Seed Data)
This MVP uses a controlled dataset containing strictly public, factual data (Minimum SIP, Expense Ratio, Exit Load, Riskometer) derived from the official SID/Factsheets of:

1. **HDFC** Flexi Cap Fund
2. **HDFC** Mid-Cap Opportunities Fund
3. **SBI** Bluechip Fund
4. **SBI** Small Cap Fund
5. **ICICI Prudential** Bluechip Fund
6. **Nippon India** Small Cap Fund
7. **Kotak** Flexicap Fund

## 💻 Tech Stack
* **Frontend**: Next.js (React), TailwindCSS, fully responsive minimalist UI.
* **Backend**: Python 3.11, FastAPI.
* **AI/LLM Engine**: Groq API / LangChain.
* **Deployment**: Dockerized Backend (Render), Edge Frontend (Vercel).
* **Pipelines**: GitHub Actions (`daily-ingestion.yml`) engineered for automated daily CRON syncing of data.

---

## 🚀 Setup Instructions

### Environment Variables
Clone the repository and create an `.env` file in the root folder using `.env.example`:
```bash
GROQ_API_KEY="your-groq-api-key"
```

### Run the Backend (FastAPI)
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m mf_assistant.main
```
The backend API will start at `http://localhost:8000`

### Run the Frontend (Next.js)
```bash
cd frontend
npm install
npm run dev
```
The UI will be accessible at `http://localhost:3000`

## ⚠️ Known Limitations
- **Temporal Memory**: Currently scoped to the uploaded `seed_data.json` context window. Expanding to thousands of funds will require transitioning back to a Vector Database (ChromaDB) on a server with >2GB RAM.
- **Strict Adherence**: The bot is heavily constrained. It may refuse seemingly benign questions if they even lightly trigger the advisory/predictive thresholds.

---
*Disclaimer: Facts-only. No investment advice. Data sourced from official public AMC documents.*
