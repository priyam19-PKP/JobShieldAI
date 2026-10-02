# 🛡️ JobShieldAI - AI-Powered Job Fraud Defense Platform

JobShieldAI is a full-stack, local-first cybersecurity intelligence platform designed to protect job seekers from sophisticated recruitment scams, phishing campaigns, phantom job postings, and advance-fee fraud.

Developed by **Priyam Prajapati**, Department of Artificial Intelligence & Machine Learning, Viva Institute of Technology.

---

## ✨ Features & Architecture

- **🤖 Machine Learning Classification:** TF-IDF text vectorization paired with a trained classifier model achieving high-confidence distinction between authentic and fraudulent job postings.
- **🧠 Local AI Reasoning (Ollama & LLaMA 3.2):** 100% private, on-device contextual AI explanations, breaking down why a job is flagged and issuing actionable safety advice. Includes automatic heuristic fallback when Ollama is offline.
- **🚨 Heuristic Scam Guardrails:** Real-time scanning for 10 high-risk fraudulent recruitment patterns (unrealistic compensation, upfront registration fees, free hardware offers, WhatsApp/Telegram communications, suspicious domains).
- **📊 Dynamic Risk Scoring (0–100):** Multi-factor threat calculation categorizing jobs into Low, Medium, or High Risk tiers.
- **🏢 Extracted Intelligence:** Natural language and regex parsing of vital job metadata: Company, Position, Location, Salary, Experience, Recruiter Email, and Web Domain with domain trust checks.
- **📄 Forensic PDF Export:** Generates tamper-evident, publication-ready PDF audit reports with timestamps and complete forensic breakdowns.
- **🎨 Next-Gen Glassmorphic UI:** High-tech cybersecurity dark mode, interactive 1-click sample loaders (Scam, Verified, Suspicious), and a structured 5-tab workspace.

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- (Optional) [Ollama](https://ollama.com/) with `llama3.2` pulled for local generative explanations:
  ```bash
  ollama pull llama3.2
  ```

### 2. Run the Application
Activate the virtual environment and start Streamlit:
```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`.

---

## 🛠️ Tech Stack
- **Frontend / Dashboard:** Streamlit, Custom Modern CSS (Glassmorphism & Flexbox)
- **Machine Learning:** Scikit-Learn, Joblib, TF-IDF
- **GenAI / LLM:** Ollama (`llama3.2`)
- **Document Generation:** ReportLab
- **Data & Text Processing:** Regex, Python 3
