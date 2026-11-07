from typing import Dict, Any, List, Optional
from datetime import datetime

class ReportExporter:
    @classmethod
    def generate_markdown(
        cls,
        project_dict: Dict[str, Any],
        papers: List[Any],
        gap_data: Optional[Dict[str, Any]] = None
    ) -> str:
        analyzed_papers = [p for p in papers if p.analysis and p.analysis.status == "completed"]
        included_papers = [p for p in papers if not p.is_excluded]

        md = []
        md.append(f"# PharmaLit AI — Research Intelligence Report")
        md.append(f"**Project:** {project_dict.get('name', 'Biomedical Review')}")
        md.append(f"**Therapeutic Area:** {project_dict.get('therapeutic_area', 'Pharmaceutical Sciences')} | **Target Drug/API:** {project_dict.get('target_drug', 'N/A')}")
        md.append(f"**Date Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        md.append(f"**Scope:** {len(papers)} Total Papers Collected | {len(included_papers)} Deduplicated / Included | {len(analyzed_papers)} Deeply Analyzed\n")
        md.append("---\n")

        md.append("## 1. Executive Literature Review Synthesis")
        if gap_data and gap_data.get("synthesis_summary"):
            md.append(gap_data["synthesis_summary"] + "\n")
        else:
            md.append("This report summarizes the multi-database systematic literature review conducted across PubMed, Europe PMC, and Semantic Scholar.\n")

        md.append("## 2. Research Gap Discovery Matrix")
        matrix_items = gap_data.get("gap_matrix", []) if gap_data else []
        if matrix_items:
            md.append("| Research Theme | Existing Evidence | Limitation Identified | Unanswered Scientific Question | Actionable Opportunity | Confidence |")
            md.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
            for item in matrix_items:
                theme = item.get("theme", "").replace("|", "-")
                evid = item.get("existing_evidence", "").replace("|", "-")
                lim = item.get("identified_limitation", "").replace("|", "-")
                unans = item.get("unanswered_question", "").replace("|", "-")
                opp = item.get("proposed_opportunity", "").replace("|", "-")
                conf = item.get("confidence_level", "")
                md.append(f"| **{theme}** | {evid} | {lim} | *{unans}* | {opp} | `{conf}` |")
            md.append("\n")
        else:
            md.append("*No gap matrix has been generated yet for this project.*\n")

        if gap_data:
            md.append("### Strategic Domain Trends")
            if gap_data.get("frequently_studied_topics"):
                md.append("- **Predominant Formulations & Topics:** " + ", ".join(gap_data["frequently_studied_topics"]))
            if gap_data.get("underexplored_topics"):
                md.append("- **Underexplored Research Avenues:** " + ", ".join(gap_data["underexplored_topics"]))
            if gap_data.get("missing_methodologies"):
                md.append("- **Critical Missing Methodologies:** " + ", ".join(gap_data["missing_methodologies"]))
            if gap_data.get("formulation_opportunities"):
                md.append("- **Formulation Translation Opportunities:** " + ", ".join(gap_data["formulation_opportunities"]))
            md.append("\n")

        md.append("## 3. Individual Research Paper Deep Extractions\n")
        for idx, p in enumerate(analyzed_papers, 1):
            an = p.analysis
            meth = an.methodology
            res = an.results
            lims = an.limitations
            gaps = an.gaps

            md.append(f"### {idx}. {p.title}")
            md.append(f"- **Authors:** {p.authors}")
            md.append(f"- **Journal & Year:** *{p.journal}* ({p.year}) | **Source:** `{p.database_source}`")
            if p.doi:
                md.append(f"- **DOI:** [{p.doi}](https://doi.org/{p.doi})")
            if p.pmid:
                md.append(f"- **PMID:** [{p.pmid}](https://pubmed.ncbi.nlm.nih.gov/{p.pmid}/)")
            md.append(f"- **Evidence Confidence:** `{an.evidence_confidence}`\n")

            md.append(f"**Research Objective:**\n> {an.research_objective}\n")

            md.append(f"**Methodology & Formulation:**")
            md.append(f"- *Study Design:* {meth.get('study_design', 'N/A')}")
            md.append(f"- *Experimental Model:* {meth.get('experimental_model', 'N/A')}")
            md.append(f"- *Formulation:* {meth.get('formulation_methods', 'N/A')}")
            md.append(f"- *Analytical Instruments:* {', '.join(meth.get('analytical_instruments', []))}")
            md.append(f"- *Statistical Analysis:* {meth.get('statistical_methods', 'N/A')}\n")

            md.append(f"**Key Findings & Quantitative Results:**")
            md.append(f"- {res.get('main_findings', 'N/A')}")
            for qm in res.get("quantitative_metrics", []):
                md.append(f"  - 📊 `{qm}`")
            md.append("")

            md.append(f"**Limitations & Vulnerabilities:**")
            for al in lims.get("author_reported_limitations", []):
                md.append(f"- ✍️ *Author Reported:* {al}")
            for il in lims.get("ai_inferred_limitations", []):
                md.append(f"- 🔍 *Scientific Audit:* {il}")
            md.append("")

            if an.evidence_snippets:
                md.append(f"**Verbatim Evidence Traceability Quotes:**")
                for snip in an.evidence_snippets[:3]:
                    md.append(f"> \"{snip}\"")
                md.append("")

            md.append("---\n")

        md.append("## 4. Systematic Literature Review References\n")
        for idx, p in enumerate(included_papers, 1):
            doi_link = f" https://doi.org/{p.doi}" if p.doi else ""
            md.append(f"{idx}. {p.authors} ({p.year or 'n.d.'}). **{p.title}**. *{p.journal}*.{doi_link}")

        return "\n".join(md)

    @classmethod
    def generate_html(
        cls,
        project_dict: Dict[str, Any],
        papers: List[Any],
        gap_data: Optional[Dict[str, Any]] = None
    ) -> str:
        md_text = cls.generate_markdown(project_dict, papers, gap_data)
        import html
        escaped_title = html.escape(project_dict.get("name", "Biomedical Literature Report"))

        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{escaped_title} — PharmaLit AI Report</title>
<style>
    body {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        color: #1a202c;
        background: #f8fafc;
        line-height: 1.6;
        padding: 40px 20px;
        margin: 0;
    }}
    .container {{
        max-width: 1000px;
        margin: 0 auto;
        background: #ffffff;
        padding: 48px;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
        border: 1px solid #e2e8f0;
    }}
    h1 {{
        color: #1b365d;
        font-size: 2.2rem;
        border-bottom: 3px solid #008080;
        padding-bottom: 12px;
        margin-top: 0;
    }}
    h2 {{
        color: #1b365d;
        font-size: 1.5rem;
        margin-top: 36px;
        border-bottom: 1px solid #e2e8f0;
        padding-bottom: 8px;
    }}
    h3 {{
        color: #008080;
        font-size: 1.2rem;
        margin-top: 24px;
    }}
    table {{
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
        font-size: 0.95rem;
    }}
    th {{
        background: #1b365d;
        color: #ffffff;
        text-align: left;
        padding: 12px 14px;
        font-weight: 600;
    }}
    td {{
        padding: 10px 14px;
        border-bottom: 1px solid #e2e8f0;
        vertical-align: top;
    }}
    tr:nth-child(even) {{
        background: #f8fafc;
    }}
    blockquote {{
        border-left: 4px solid #008080;
        margin: 12px 0;
        padding: 8px 16px;
        background: #f0fdfa;
        color: #134e4a;
        font-style: italic;
    }}
    code {{
        background: #edf2f7;
        color: #2b6cb0;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 0.9em;
    }}
    .badge {{
        display: inline-block;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        background: #e6fffa;
        color: #047481;
    }}
    .footer {{
        margin-top: 48px;
        padding-top: 20px;
        border-top: 1px solid #e2e8f0;
        text-align: center;
        color: #718096;
        font-size: 0.85rem;
    }}
    @media print {{
        body {{ background: #fff; padding: 0; }}
        .container {{ box-shadow: none; border: none; padding: 20px; }}
    }}
</style>
</head>
<body>
<div class="container">
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <div>
            <span class="badge">PharmaLit AI Research Intelligence</span>
            <h1 style="margin-top:10px;">{escaped_title}</h1>
        </div>
    </div>
    <p><strong>Therapeutic Domain:</strong> {html.escape(project_dict.get('therapeutic_area', 'Pharmaceutical Sciences'))} | <strong>Target API:</strong> {html.escape(project_dict.get('target_drug', 'N/A'))}</p>
    <p><strong>Export Date:</strong> {datetime.utcnow().strftime('%B %d, %Y - %H:%M UTC')}</p>
    <hr style="border:0; border-top:1px solid #e2e8f0; margin:24px 0;">

    <div class="content">
        <div style="white-space: pre-line;">{html.escape(md_text)}</div>
    </div>

    <div class="footer">
        Generated autonomously by <strong>PharmaLit AI</strong> — AI-Powered Literature Review & Research Intelligence Platform.<br>
        Reproducible, Evidence-Grounded Biomedical Research Synthesis.
    </div>
</div>
</body>
</html>
"""
        return html_template
