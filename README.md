# Carik: Autonomous Humanized Editorial Studio

Carik is an automated editorial engine designed to translate Bahasa Indonesia drafts into natural English, run multi-dimensional quality audits (Plagiarism, Grammar, and Robotic/AI-ism Detection), and perform targeted 3-pass humanizing rewrites until strict quality thresholds are met.

---

## 📂 Project Blueprint Structure

This workspace has been structured with enterprise-grade specifications ready for development in **Antigravity IDE**:

1. **[requirements.md](file:///C:/Users/QA%20Engineer-Fritzie/Documents/Projects/learning-by-doing/carik/requirements.md)**: Detailed functional requirements, threshold metrics, and zero-cost stack breakdown.
2. **[architecture.md](file:///C:/Users/QA%20Engineer-Fritzie/Documents/Projects/learning-by-doing/carik/architecture.md)**: SOLID and Clean Architecture layers (Domain, Application, Infrastructure, Presentation), finite state machine flow, and Pydantic schemas.
3. **[design.md](file:///C:/Users/QA%20Engineer-Fritzie/Documents/Projects/learning-by-doing/carik/design.md)**: UI/UX design specifications following `pbakaus/impeccable`, `Nutlope/hallmark` anti-AI-slop guidelines, and modern W3C standards (`:has()`, container queries, native `<dialog>`).
4. **[.antigravityrules](file:///C:/Users/QA%20Engineer-Fritzie/Documents/Projects/learning-by-doing/carik/.antigravityrules)**: Automated rules configuration loaded by Antigravity IDE enforcing Clean Code, Writing Skills, and UI polish.

---

## 🛠️ The 100% Free & Alternative Tech Stack

| Component | Technology | Cost / Free Tier |
| :--- | :--- | :--- |
| **Translation Engine** | Google Gemini 2.5 Flash | Free Tier (15 RPM / 1M TPM) |
| **Plagiarism Checker** | DuckDuckGo N-Gram searcher | $0.00 (No API key needed) |
| **Grammar Linter** | `language-tool-python` (Local) | Free & Open Source |
| **Robotic & Burstiness Check** | Local NumPy + regex rules | $0.00 (Zero latency compute) |
| **Humanizer Engine** | Gemini 2.5 Flash (3-Pass prompt) | Free Tier |
| **Backend & Models** | FastAPI + Pydantic v2 | Free & Open Source |
| **Frontend** | Modern Semantic HTML/CSS/JS | Free & Open Source |

---

## 🚀 Getting Started in Antigravity IDE

### 1. Set Active Workspace
In Antigravity IDE, open folder:
`C:\Users\QA Engineer-Fritzie\Documents\Projects\learning-by-doing\carik`

### 2. Environment Setup
```bash
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

# Install core dependencies
pip install fastapi uvicorn pydantic numpy google-genai duckduckgo-search language-tool-python
```

### 3. Set Gemini Free API Key
```bash
$env:GEMINI_API_KEY="your-free-gemini-api-key"
```

---

## 🎯 Built-in Skills & Guidelines Integrated
- **`blader/humanizer`**: Banned AI words list, em-dash eradication, sentence rhythm metrics.
- **`conorbronsdon/avoid-ai-writing`**: Specificity rule, anti-generalization, thought-leadership tone.
- **`lguz/humanize-writing-skill`**: George Orwell’s 6 rules for writing, deep syntax restructuring.
- **`markoa/clean-code-skill` & `sickn33/clean-code`**: Max 25-line functions, early return guard clauses, strict SOLID.
- **`PatrickJS/awesome-cursorrules`**: Strict type annotations and schema validation.
- **`pbakaus/impeccable` & `Nutlope/hallmark`**: High-contrast editorial workbench, zero purple-cyan gradient slop.