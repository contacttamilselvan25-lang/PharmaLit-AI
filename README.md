# 🔬 PharmaLit AI — Autonomous Biomedical Systematic Literature Review & Meta-Analysis Copilot

> **AI-Powered Biomedical Research Studio** • Automates PubMed & Europe PMC federated literature mining, deep 18-parameter formulation extraction, and research gap discovery with 100% offline capability.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![UI](https://img.shields.io/badge/Interface-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![Database](https://img.shields.io/badge/Database-SQLite%20(Local)-003B57.svg)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Security](https://img.shields.io/badge/Security-Local--First%20%7C%20Zero--Leak-success.svg)](#-privacy-security--zero-credential-sharing)

> **PharmaLit AI** is a professional, locally running biomedical research intelligence platform. It automates literature searching, deduplication, deep parameter extraction, and research gap discovery across PubMed and Europe PMC — with **zero credential requirements** and **100% offline capability**.

---

## 👥 Who Is This For?

| User Group | How PharmaLit AI Helps |
| :--- | :--- |
| 🎓 **B.Pharm & M.Pharm Students** | Conduct rapid systematic reviews for dissertations, review articles, and seminar presentations without manual searching across dozens of tabs. |
| 🔬 **PhD & Postdoctoral Scholars** | Extract quantitative formulation metrics (particle size nm, PDI, encapsulation %, zeta potential mV, IC50) and identify unexplored thesis topics. |
| 💊 **Pharmacologists & Formulation Scientists** | Compare delivery carriers (*SLNs, NLCs, liposomes, polymeric micelles, nanoemulsions*) and audit author limitations vs. study design bottlenecks. |
| ✍️ **Review Authors & Academics** | Instantly export structured 5-sheet styled Excel datasets (`.xlsx`), publication-grade HTML reports, and BibTeX citations ready for Zotero and EndNote. |

---

## 🏛️ System Architecture Diagram

Below is the simple diagrammatic workflow of how data travels inside PharmaLit AI:

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                          PHARMALIT AI ARCHITECTURE                             │
└────────────────────────────────────────────────────────────────────────────────┘

    1. USER INPUT & QUERY BUILDER
       ┌────────────────────────────────────────────────────────┐
       │ Topic • Drug/API • Carrier • Disease • Year Range      │
       └───────────────────────────┬────────────────────────────┘
                                   │
                                   ▼
    2. FEDERATED PUBLIC SEARCH APIS (Live & Genuine)
       ┌───────────────────────┬────────────────────────┬────────────────────────┐
       │   NCBI PubMed API     │     Europe PMC API     │    Crossref DOI API    │
       │   (eSearch & eFetch)  │     (EBI REST API)     │   (Metadata Verifier)  │
       └───────────────────────┴───────────┬────────────┴────────────────────────┘
                                           │
                                           ▼
    3. INTELLIGENT DEDUPLICATION CASCADE
       ┌─────────────────────────────────────────────────────────────────────────┐
       │  Stage 1: Normalized DOI  ──>  Stage 2: Exact PMID / PMCID              │
       │  Stage 3: Fuzzy Title Similarity (>=90%) + Pub Year Matching            │
       │  Stage 4: Metadata Merging & Multi-Database Provenance Tracking         │
       └───────────────────────────────────┬─────────────────────────────────────┘
                                           │
                                           ▼
    4. DUAL-ENGINE SCIENTIFIC ANALYSIS
       ┌───────────────────────────────────┴─────────────────────────────────────┐
       │                                                                         │
       ▼                                                                         ▼
   [ENGINE A: GOOGLE GEMINI AI]                             [ENGINE B: SCIENTIFIC NLP]
   • Configurable Gemini LLM                                • 100% Offline & Free
   • Multi-paper synthesis                                  • Regex & Lexicon Parser
   • Strict JSON schema output                              • Traceable Source Quotes
       │                                                                         │
       └───────────────────────────────────┬─────────────────────────────────────┘
                                           │
                                           ▼
    5. RESEARCH GAP DISCOVERY & SYNTHESIS
       ┌─────────────────────────────────────────────────────────────────────────┐
       │ Cross-Paper Analysis ──> Research Gap Matrix ──> Actionable Ideas       │
       └───────────────────────────────────┬─────────────────────────────────────┘
                                           │
                                           ▼
    6. LOCAL STORAGE & EXECUTIVE INTERFACE
       ┌───────────────────────────────────┴─────────────────────────────────────┐
       │  Local SQLite DB (pharmalit.db)  │  Interactive Streamlit UI (Port 8501)│
       └───────────────────────────────────┬─────────────────────────────────────┘
                                           │
                                           ▼
    7. MULTI-FORMAT EXPORTS
       ┌──────────────────────┬───────────────────────┬──────────────────────────┐
       │ Styled Excel (.xlsx) │ Printable HTML Report │ BibTeX References (.bib) │
       └──────────────────────┴───────────────────────┴──────────────────────────┘
```

---

## 🚀 How to Pull & Use Locally (Beginner Friendly)

Anyone can clone and run this software locally on Windows 11 with zero technical setup:

### Step 1: Clone the Repository
```bash
git clone https://github.com/contacttamilselvan25-lang/PharmaLit-AI.git
cd PharmaLit-AI
```

### Step 2: One-Click Installation
Double-click **`install.bat`** in the project folder.
- It will automatically set up your virtual environment and install all required libraries.

### Step 3: One-Click Launch
Double-click **`run.bat`** in the project folder.
- It starts the platform and opens your browser directly at:
  **`http://127.0.0.1:8501`**

*(Alternatively from the command line: `python run.py` or `streamlit run app/main.py`)*

---

## 📖 Step-by-Step How to Use

### 1. 📊 Executive Dashboard
- View live project KPIs: total papers collected, deduplication ratios, papers with DOIs, abstracts, and full texts.
- Inspect interactive Plotly charts showing publication growth trends over years, top publishing journals, and database distribution.

### 2. 🔍 Smart Literature Search
- Enter your research topic (e.g., *"Curcumin brain delivery"*).
- Add specific filters: API/Drug (*Curcumin*), Delivery System (*Solid Lipid Nanoparticles*), Disease (*Alzheimer's disease*), and Year Range (*2018 - 2026*).
- Select your target paper count (30, 50, 75, 100, or custom).
- Hit **🚀 Execute Smart Literature Search**. The progress bar tracks real-time querying across PubMed and Europe PMC.

### 3. 📚 Paper Collection & Deduplication
- Review the cleaned deduplicated paper list.
- Click **🔍 Verify DOI with Crossref** on any paper to confirm genuine publisher indexing and citation counts.
- Use the **🚫 Exclude** button to filter out ineligible studies with customized exclusion reasons.

### 4. 🔬 AI Research Analysis
- Select your analysis engine: **Auto**, **Gemini AI**, or **Rule-Based Scientific NLP (100% Offline)**.
- Click **⚡ Analyze All Active Papers**.
- Review structured tabs for every paper:
  - 🎯 **Objective & Scientific Importance**
  - 🧪 **Methodology**: Study design, biological model, formulation technique, and analytical instruments (*DLS, HPLC, TEM, DSC, XRD*).
  - 📊 **Quantitative Results**: Particle diameters (nm), encapsulation efficiency (%), zeta potential (mV), bioavailability fold improvement, IC50.
  - ⚠️ **Limitations Audit**: Strictly separates **author-reported limitations** from **senior scientist AI-inferred audit**.
  - 📝 **Traceable Evidence**: Exact verbatim quotes proving every extracted claim.

### 5. 📑 Full-Text PDF Lab
- Drag and drop research PDFs into the uploader.
- The system automatically extracts text using PyMuPDF and segments the paper into: *Abstract*, *Introduction*, *Methods*, *Results*, *Discussion*, *Conclusion*, and *References**.
- Connects the uploaded PDF directly to its database record.

### 6. 💡 Research Gap Intelligence
- Click **🧠 Synthesize Corpus & Generate Gap Matrix**.
- The platform aggregates all analyzed studies to identify:
  - Predominant vs. underexplored formulation carriers.
  - Repeated experimental limitations (e.g., lack of in vivo pharmacokinetics, missing ICH accelerated stability).
  - High-impact **Research Gap Matrix** with supporting DOIs and confidence levels.

### 7. 📥 Export & Reports
- **Download Excel (.xlsx)**: Comprehensive 5-sheet workbook styled in Oxford Navy with auto-fitted columns.
- **Download HTML Report (.html)**: Executive printable review report with responsive scientific styling.
- **Download BibTeX (.bib)**: Import citations directly into Zotero, Mendeley, or EndNote.

---

## 🔒 Privacy, Security & Zero Credential Sharing

This project adheres to the highest data privacy and security standards:

- ✅ **No Credentials in Code**: API keys, passwords, and private tokens are **NEVER committed to GitHub**.
- ✅ **`.gitignore` Protection**: Local database files (`pharmalit.db`), `.env` files, `.streamlit/credentials.toml`, and uploaded PDFs are strictly ignored.
- ✅ **Safe `.env.example`**: Only blank template environment variables are provided.
- ✅ **100% Offline Capable**: You do **not** need a paid API key or cloud account to search, deduplicate, analyze papers, or export Excel files.
- ✅ **Local Storage**: All your research projects, notes, and search histories stay completely on your computer.

---

## 🧪 Automated Testing Suite

PharmaLit AI includes 19 automated unit and integration tests. Run them anytime:
```bash
python -m pytest tests -v
```
All 19 tests verify search query syntax, Crossref verification, 4-stage deduplication, NLP extraction, PDF segmentation, SQLite persistence, and Excel generation.

---

## 📜 License & Credits

- Developed for the biomedical and pharmaceutical research community.
- Licensed under the **MIT License**.
