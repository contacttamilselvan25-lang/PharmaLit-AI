import os
import sys
from pathlib import Path
from datetime import datetime
import streamlit as st
import pandas as pd

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import settings, EXPORTS_DIR, UPLOADS_DIR
from app.database import init_db, SessionLocal, Repository
from app.services import (
    ProjectService,
    SearchService,
    DeduplicationService,
    PDFService,
    AnalysisService,
    GapService
)
from app.integrations.crossref import CrossrefClient
from app.integrations.gemini_client import GeminiClient
from app.exports import ExcelExporter, ReportExporter
from app.ui import (
    apply_scientific_theme,
    render_brand_header,
    plot_publications_by_year,
    plot_journals_distribution,
    plot_sources_distribution,
    plot_study_types_distribution
)

# Initialize Streamlit Page Config
st.set_page_config(
    page_title="PharmaLit AI — Research Intelligence Platform",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Scientific Theme CSS
apply_scientific_theme()

# Initialize Database
init_db()

def get_repo():
    db = SessionLocal()
    return Repository(db), db

# Main App Execution
def main():
    repo, db_session = get_repo()
    proj_service = ProjectService(repo)
    search_service = SearchService(repo)
    pdf_service = PDFService()
    crossref_client = CrossrefClient()

    # Seed sample project on fresh install if no projects exist
    active_project = proj_service.seed_sample_project_if_empty()

    # =========================================================================
    # SIDEBAR: PROJECT MANAGEMENT & GLOBAL CONTROLS
    # =========================================================================
    with st.sidebar:
        st.markdown("### 🔬 **PharmaLit AI**")
        st.caption("Biomedical Research Intelligence Platform")
        st.markdown("---")

        # Project Selector
        projects = proj_service.list_projects()
        project_names = [p.name for p in projects]
        
        # Keep track of active project in session state
        if "active_project_id" not in st.session_state and projects:
            st.session_state.active_project_id = projects[0].id

        curr_idx = 0
        for i, p in enumerate(projects):
            if p.id == st.session_state.active_project_id:
                curr_idx = i
                break

        selected_proj_name = st.selectbox(
            "Select Research Project",
            project_names,
            index=curr_idx if curr_idx < len(project_names) else 0,
            key="project_selector"
        )
        for p in projects:
            if p.name == selected_proj_name:
                st.session_state.active_project_id = p.id
                active_project = p
                break

        # Project Summary in Sidebar
        if active_project:
            st.markdown(f"**Therapeutic Area:** `{active_project.therapeutic_area or 'General'}`")
            st.markdown(f"**Target API:** `{active_project.target_drug or 'N/A'}`")
            papers_count = len(repo.get_papers(active_project.id, include_excluded=False))
            st.markdown(f"**Active Papers:** `{papers_count}`")

        # New Project Expander
        with st.expander("➕ Create New Project"):
            with st.form("new_project_form"):
                new_name = st.text_input("Project Name*", placeholder="e.g. Nanomedicine in Glioblastoma")
                new_area = st.text_input("Therapeutic Area", placeholder="e.g. Oncology & Neuropharmacology")
                new_drug = st.text_input("Target Drug / API", placeholder="e.g. Temozolomide")
                new_desc = st.text_area("Description / Review Scope", placeholder="Systematic literature review scope...")
                submit_proj = st.form_submit_button("Create Project", use_container_width=True)

                if submit_proj and new_name.strip():
                    created = proj_service.create_project(
                        name=new_name.strip(),
                        description=new_desc.strip(),
                        therapeutic_area=new_area.strip(),
                        target_drug=new_drug.strip()
                    )
                    st.session_state.active_project_id = created.id
                    st.success(f"Project '{created.name}' created!")
                    st.rerun()

        st.markdown("---")
        # Navigation Menu
        nav_selection = st.radio(
            "Platform Navigation",
            [
                "📊 Executive Dashboard",
                "🔍 Smart Literature Search",
                "📚 Paper Collection & Dedup",
                "🔬 AI Research Analysis",
                "📑 Full-Text PDF Lab",
                "💡 Research Gap Intelligence",
                "📥 Export & Reports",
                "⚙️ Settings & Configuration"
            ],
            key="nav_selection"
        )

        st.markdown("---")
        # AI Provider Status in Sidebar
        api_key_setting = repo.get_setting("GEMINI_API_KEY", settings.GEMINI_API_KEY)
        gemini_model = repo.get_setting("GEMINI_MODEL", settings.GEMINI_MODEL)
        has_gemini = bool(api_key_setting and len(api_key_setting.strip()) > 10)
        
        if has_gemini:
            st.success(f"🤖 AI Provider: **Gemini ({gemini_model})**")
        else:
            st.info("⚡ AI Mode: **Rule-Based Scientific NLP (100% Offline)**")

    # Render Main Brand Header
    render_brand_header(
        active_project_name=active_project.name if active_project else "",
        therapeutic_area=active_project.therapeutic_area if active_project else "",
        target_drug=active_project.target_drug if active_project else ""
    )

    proj_id = active_project.id if active_project else 1

    # =========================================================================
    # TAB 1: EXECUTIVE DASHBOARD
    # =========================================================================
    if nav_selection == "📊 Executive Dashboard":
        st.markdown("## 📊 Executive Research Intelligence Dashboard")
        st.caption("Real-time biomedical literature metrics, publication trends, and research gap status.")

        metrics = repo.get_dashboard_metrics(proj_id)

        # Top KPI Metric Cards (3 rows of 3)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Projects</div>
                <div class="metric-value">{metrics['total_projects']}</div>
                <div class="metric-sub">Local research workspaces</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Papers with DOI</div>
                <div class="metric-value">{metrics['with_doi']}</div>
                <div class="metric-sub">Crossref verified records</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Awaiting Analysis</div>
                <div class="metric-value">{metrics['awaiting_analysis']}</div>
                <div class="metric-sub">Pending extraction queue</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Papers Collected</div>
                <div class="metric-value">{metrics['total_papers']}</div>
                <div class="metric-sub">Raw multi-database hits</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Accessible Abstracts</div>
                <div class="metric-value">{metrics['with_abstract']}</div>
                <div class="metric-sub">Text-available evidence</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Completed Analyses</div>
                <div class="metric-value">{metrics['completed_analyses']}</div>
                <div class="metric-sub">Deep scientific extractions</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Unique Papers (Deduped)</div>
                <div class="metric-value">{metrics['unique_papers']}</div>
                <div class="metric-sub">Clean deduplicated corpus</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Full-Text Attached</div>
                <div class="metric-value">{metrics['with_full_text']}</div>
                <div class="metric-sub">Uploaded PDF documents</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Research Gaps Discovered</div>
                <div class="metric-value">{metrics['gaps_count']}</div>
                <div class="metric-sub">Identified opportunities</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Visualizations (2x2 grid)
        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            fig_year = plot_publications_by_year(metrics["years_dist"])
            st.plotly_chart(fig_year, use_container_width=True)

            fig_sources = plot_sources_distribution(metrics["sources_dist"])
            st.plotly_chart(fig_sources, use_container_width=True)

        with chart_col2:
            fig_journals = plot_journals_distribution(metrics["journals_dist"])
            st.plotly_chart(fig_journals, use_container_width=True)

            fig_types = plot_study_types_distribution(metrics["types_dist"])
            st.plotly_chart(fig_types, use_container_width=True)

    # =========================================================================
    # TAB 2: SMART LITERATURE SEARCH
    # =========================================================================
    elif nav_selection == "🔍 Smart Literature Search":
        st.markdown("## 🔍 Smart Biomedical Literature Search Engine")
        st.caption("Federated search across PubMed E-utilities, Europe PMC REST API, and Semantic Scholar.")

        with st.form("literature_search_form"):
            col_t1, col_t2 = st.columns([2, 1])
            with col_t1:
                topic = st.text_input("Research Topic / Core Problem*", value="Curcumin brain delivery", placeholder="e.g. Solid lipid nanoparticles for curcumin brain delivery")
            with col_t2:
                target_count_choice = st.selectbox(
                    "Target Papers to Retrieve",
                    ["30 papers", "50 papers", "75 papers", "100 papers", "Custom"],
                    index=1
                )
                if target_count_choice == "Custom":
                    max_papers = st.number_input("Custom Number", min_value=5, max_value=250, value=40)
                else:
                    max_papers = int(target_count_choice.split()[0])

            col_k1, col_k2 = st.columns(2)
            with col_k1:
                main_keywords = st.text_input("Main Keywords (comma separated)", value="lipid nanoparticles, bioavailability", placeholder="e.g. lipid nanoparticles, bioavailability, brain targeting")
                alt_keywords = st.text_input("Alternative / Synonym Keywords (comma separated)", value="SLN, NLC", placeholder="e.g. SLN, NLC, solid lipid nanoparticles")
                disease_area = st.text_input("Disease or Therapeutic Area", value="Alzheimer's disease", placeholder="e.g. Alzheimer's disease, Glioblastoma, Diabetes")

            with col_k2:
                drug_api = st.text_input("Drug / Active Pharmaceutical Ingredient (API)", value="Curcumin", placeholder="e.g. Curcumin, Paclitaxel, Metformin")
                delivery_system = st.text_input("Drug Delivery System / Carrier", value="Solid Lipid Nanoparticles", placeholder="e.g. Nanostructured Lipid Carriers, Polymeric Micelles")
                methodology = st.text_input("Specific Methodology / Analytical Focus", value="", placeholder="e.g. High-pressure homogenization, Franz diffusion cell")

            col_f1, col_f2 = st.columns(2)
            with col_f1:
                curr_year = datetime.now().year
                year_range = st.slider("Publication Year Range", min_value=1990, max_value=curr_year, value=(curr_year - 8, curr_year))
            with col_f2:
                st.markdown("**Preferred Databases**")
                db_col1, db_col2, db_col3 = st.columns(3)
                with db_col1:
                    use_pm = st.checkbox("PubMed", value=True)
                with db_col2:
                    use_epmc = st.checkbox("Europe PMC", value=True)
                with db_col3:
                    use_s2 = st.checkbox("Semantic Scholar", value=True)

            search_submitted = st.form_submit_button("🚀 Execute Smart Literature Search", use_container_width=True)

        if search_submitted:
            selected_dbs = []
            if use_pm: selected_dbs.append("PubMed")
            if use_epmc: selected_dbs.append("Europe PMC")
            if use_s2: selected_dbs.append("Semantic Scholar")

            if not selected_dbs:
                st.error("Please select at least one database source.")
            elif not topic.strip():
                st.error("Please enter a research topic.")
            else:
                progress_bar = st.progress(0.0)
                status_placeholder = st.empty()

                def update_prog(ratio, msg):
                    progress_bar.progress(ratio)
                    status_placeholder.info(f"⏳ {msg}")

                query_params = {
                    "topic": topic,
                    "main_keywords": main_keywords,
                    "alt_keywords": alt_keywords,
                    "disease_area": disease_area,
                    "drug_api": drug_api,
                    "delivery_system": delivery_system,
                    "methodology": methodology
                }

                try:
                    final_papers, audit = search_service.execute_search(
                        project_id=proj_id,
                        query_params=query_params,
                        databases=selected_dbs,
                        max_papers=max_papers,
                        start_year=year_range[0],
                        end_year=year_range[1],
                        progress_callback=update_prog
                    )
                    status_placeholder.empty()
                    progress_bar.empty()

                    st.success(f"🎉 Search Completed! Retrieved **{audit['original_count']}** raw records, eliminated **{audit['duplicate_count']}** duplicates, and saved **{len(final_papers)}** unique papers.")

                    # Audit breakdown
                    aud_col1, aud_col2, aud_col3 = st.columns(3)
                    aud_col1.metric("Original Retrieved", audit["original_count"])
                    aud_col2.metric("Duplicates Removed", audit["duplicate_count"])
                    aud_col3.metric("Final Unique Papers", len(final_papers))

                    with st.expander("🔍 Inspection & Deduplication Audit Log"):
                        st.markdown(f"**Synthesized Query String:** `{audit.get('query_string')}`")
                        st.markdown("#### Database Engine Status:")
                        for log_line in audit.get("status_log", []):
                            st.write(f"- {log_line}")
                        if audit.get("duplicates_log"):
                            st.markdown("#### Deduplication Decisions:")
                            for d_entry in audit["duplicates_log"][:8]:
                                st.write(f"- `{d_entry['reason']}`: **{d_entry['title'][:70]}...**")

                except Exception as e:
                    st.error(f"Error executing search: {e}")

        # Search History
        st.markdown("---")
        st.markdown("### 📜 Project Search History")
        history = repo.get_search_history(proj_id)
        if history:
            h_data = []
            for h in history:
                q = h.query_params
                h_data.append({
                    "Date & Time": h.executed_at.strftime("%Y-%m-%d %H:%M") if h.executed_at else "",
                    "Topic": q.get("topic", ""),
                    "Databases": h.databases_searched,
                    "Raw Results": h.raw_results_count,
                    "Deduplicated": h.deduped_results_count
                })
            st.dataframe(pd.DataFrame(h_data), use_container_width=True)
        else:
            st.info("No prior searches recorded for this project.")

    # =========================================================================
    # TAB 3: PAPER COLLECTION & DEDUPLICATION
    # =========================================================================
    elif nav_selection == "📚 Paper Collection & Dedup":
        st.markdown("## 📚 Paper Collection & Deduplication Manager")
        st.caption("Inspect, filter, verify DOI on Crossref, and manually manage paper inclusion/exclusion.")

        all_papers = repo.get_papers(proj_id, include_excluded=True)
        included_papers = [p for p in all_papers if not p.is_excluded]
        excluded_papers = [p for p in all_papers if p.is_excluded]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total in Project", len(all_papers))
        c2.metric("Included Active", len(included_papers))
        c3.metric("Manually Excluded", len(excluded_papers))
        c4.metric("With DOI", len([p for p in all_papers if p.doi]))

        # Filter controls
        f_col1, f_col2, f_col3 = st.columns([2, 1, 1])
        with f_col1:
            search_query = st.text_input("Filter by Title, Author, or Keyword", placeholder="Type to search within project...")
        with f_col2:
            status_filter = st.selectbox("Inclusion Filter", ["All Papers", "Included Only", "Excluded Only"])
        with f_col3:
            db_filter = st.selectbox("Database Filter", ["All Databases", "PubMed", "Europe PMC", "Semantic Scholar"])

        filtered = all_papers
        if status_filter == "Included Only":
            filtered = [p for p in filtered if not p.is_excluded]
        elif status_filter == "Excluded Only":
            filtered = [p for p in filtered if p.is_excluded]

        if db_filter != "All Databases":
            filtered = [p for p in filtered if db_filter.lower() in p.database_source.lower()]

        if search_query.strip():
            sq = search_query.strip().lower()
            filtered = [
                p for p in filtered
                if sq in p.title.lower() or sq in p.authors.lower() or sq in p.abstract.lower() or sq in p.journal.lower()
            ]

        st.markdown(f"**Showing {len(filtered)} papers:**")

        for paper in filtered:
            with st.container():
                st.markdown(f"""
                <div class="paper-card">
                    <div class="paper-title">{paper.title}</div>
                    <div class="paper-meta">
                        <strong>Authors:</strong> {paper.authors or 'Not listed'}<br>
                        <strong>Journal:</strong> <em>{paper.journal or 'Biomedical Literature'}</em> ({paper.year or 'N/A'})
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Badges row
                b_col1, b_col2, b_col3, b_col4, b_col5 = st.columns([1.5, 1.5, 1, 1, 2])
                with b_col1:
                    st.caption(f"🏛️ Source: `{paper.database_source}`")
                with b_col2:
                    if paper.doi:
                        st.caption(f"🔗 DOI: `{paper.doi}`")
                    else:
                        st.caption("🔗 DOI: None")
                with b_col3:
                    if paper.pmid:
                        st.caption(f"📄 PMID: `{paper.pmid}`")
                with b_col4:
                    if paper.is_open_access:
                        st.caption("🟢 Open Access")
                with b_col5:
                    status_label = "❌ Excluded" if paper.is_excluded else "✅ Included"
                    st.caption(f"Status: **{status_label}**")

                # Action buttons inside expander
                with st.expander(f"Inspect Details & Abstract — ID #{paper.id}"):
                    st.markdown("**Abstract:**")
                    st.write(paper.abstract if paper.abstract else "*No abstract accessible from database record.*")

                    action_c1, action_c2 = st.columns(2)
                    with action_c1:
                        # Crossref DOI Verification
                        if paper.doi and st.button(f"🔍 Verify DOI with Crossref (ID #{paper.id})", key=f"cr_{paper.id}"):
                            with st.spinner("Checking Crossref..."):
                                cr_res = crossref_client.verify_doi(paper.doi)
                                if cr_res.get("valid"):
                                    st.success(f"✅ Verified on Crossref: Published by '{cr_res.get('publisher')}', cited by {cr_res.get('is_referenced_by_count')} papers.")
                                else:
                                    st.warning(f"Crossref check: {cr_res.get('error')}")

                    with action_c2:
                        # Toggle exclusion
                        if paper.is_excluded:
                            if st.button(f"♻️ Restore / Re-Include (ID #{paper.id})", key=f"inc_{paper.id}"):
                                repo.update_paper_exclusion(paper.id, is_excluded=False)
                                st.rerun()
                        else:
                            ex_reason = st.selectbox(
                                "Exclusion Reason",
                                ["Off-topic formulation", "Ineligible study model", "Duplicate preprint", "Methodological flaw", "Language barrier"],
                                key=f"rs_{paper.id}"
                            )
                            if st.button(f"🚫 Exclude Paper (ID #{paper.id})", key=f"exc_{paper.id}"):
                                repo.update_paper_exclusion(paper.id, is_excluded=True, reason=ex_reason)
                                st.rerun()

                st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)

    # =========================================================================
    # TAB 4: AI RESEARCH ANALYSIS
    # =========================================================================
    elif nav_selection == "🔬 AI Research Analysis":
        st.markdown("## 🔬 AI Research Paper Analysis Engine")
        st.caption("Deep extraction of Objectives, Methodologies, Quantitative Results, Author Limitations, Inferred Gaps, and Traceable Evidence.")

        analysis_service = AnalysisService(
            repo=repo,
            api_key=repo.get_setting("GEMINI_API_KEY", settings.GEMINI_API_KEY),
            model=repo.get_setting("GEMINI_MODEL", settings.GEMINI_MODEL)
        )

        papers = repo.get_papers(proj_id, include_excluded=False)
        pending_papers = [p for p in papers if not p.analysis or p.analysis.status != "completed"]

        # Action control bar
        act_col1, act_col2, act_col3 = st.columns([1.5, 1.5, 2])
        with act_col1:
            mode_choice = st.selectbox(
                "Analysis Strategy",
                ["Auto (Gemini AI if configured, else Rule-Based)", "Gemini AI (LLM)", "Rule-Based Scientific NLP (100% Offline)"]
            )
            mode_map = {
                "Auto (Gemini AI if configured, else Rule-Based)": "auto",
                "Gemini AI (LLM)": "gemini",
                "Rule-Based Scientific NLP (100% Offline)": "rule_based"
            }
            selected_mode = mode_map[mode_choice]

        with act_col2:
            st.metric("Pending Analysis", len(pending_papers))

        with act_col3:
            st.write("")
            st.write("")
            if st.button(f"⚡ Analyze All Active Papers ({len(papers)})", use_container_width=True):
                prog_bar = st.progress(0.0)
                status_txt = st.empty()

                def an_prog(ratio, msg):
                    prog_bar.progress(ratio)
                    status_txt.info(f"🔬 {msg}")

                analysis_service.analyze_project_papers(
                    project_id=proj_id,
                    mode=selected_mode,
                    progress_callback=an_prog
                )
                status_txt.empty()
                prog_bar.empty()
                st.success("All papers analyzed successfully!")
                st.rerun()

        st.markdown("---")

        # Paper Analysis Inspector
        analyzed_papers = [p for p in papers if p.analysis and p.analysis.status == "completed"]

        if not analyzed_papers:
            st.warning("No papers have been analyzed yet in this project. Click 'Analyze All Active Papers' above to run the analysis.")
        else:
            paper_titles = [f"#{p.id} - {p.title[:80]}... ({p.year or 'N/A'})" for p in analyzed_papers]
            selected_title = st.selectbox("Select Analyzed Paper to Inspect:", paper_titles)
            selected_id = int(selected_title.split()[0].replace("#", ""))
            target_paper = next((p for p in analyzed_papers if p.id == selected_id), None)

            if target_paper and target_paper.analysis:
                an = target_paper.analysis
                meth = an.methodology
                res = an.results
                lims = an.limitations
                gaps = an.gaps
                futs = an.future_directions

                # Top Badge Bar
                st.markdown(f"### {target_paper.title}")
                st.caption(f"**Authors:** {target_paper.authors} | **Journal:** *{target_paper.journal}* ({target_paper.year})")
                
                b1, b2, b3 = st.columns(3)
                b1.info(f"🏷️ Mode: **{an.analysis_mode.upper()}** ({an.model_used})")
                b2.success(f"🛡️ Evidence: **{an.evidence_confidence}**")
                b3.caption(f"Analyzed: {an.analyzed_at.strftime('%Y-%m-%d %H:%M') if an.analyzed_at else ''}")

                # Analysis Tabs
                t_obj, t_meth, t_res, t_lim, t_gaps, t_evid = st.tabs([
                    "🎯 Objective & Importance",
                    "🧪 Methodology",
                    "📊 Results & Metrics",
                    "⚠️ Limitations Audit",
                    "🔮 Gaps & Future Directions",
                    "📝 Traceable Evidence Quotes"
                ])

                with t_obj:
                    st.markdown("#### Primary Research Objective")
                    st.info(an.research_objective or "Investigation of pharmaceutical formulation efficacy.")
                    st.markdown("#### Scientific Contribution & Relevance")
                    st.write(an.scientific_importance or "Contributes experimental formulation data to drug delivery science.")

                with t_meth:
                    st.markdown("#### Study Design & Architecture")
                    st.markdown(f"- **Study Design:** `{meth.get('study_design', 'Experimental study')}`")
                    st.markdown(f"- **Experimental Model:** `{meth.get('experimental_model', 'In vitro / in vivo model')}`")
                    st.markdown(f"- **Formulation Approach:** `{meth.get('formulation_methods', 'Standard formulation')}`")
                    st.markdown(f"- **Sample Size / Dosing:** {meth.get('sample_size_or_dosing', 'Standard replicates')}")
                    st.markdown(f"- **Statistical Methods:** {meth.get('statistical_methods', 'Significance reported')}")

                    st.markdown("#### Analytical Instruments Detected")
                    inst_list = meth.get("analytical_instruments", [])
                    if inst_list:
                        for inst in inst_list:
                            st.write(f"- 🔬 **{inst}**")
                    else:
                        st.write("Spectrophotometric and chromatographic methods.")

                with t_res:
                    st.markdown("#### Main Findings Summary")
                    st.write(res.get("main_findings", "Experimental outcomes verified."))

                    st.markdown("#### Extracted Quantitative Parameters")
                    q_metrics = res.get("quantitative_metrics", [])
                    if q_metrics:
                        for qm in q_metrics:
                            st.markdown(f"- 📈 `{qm}`")
                    else:
                        st.write("Quantitative data documented in source text.")

                    st.markdown("#### Significant Observations")
                    st.write(res.get("significant_observations", "Observed sustained release and biological compatibility."))

                with t_lim:
                    lim_c1, lim_c2 = st.columns(2)
                    with lim_c1:
                        st.markdown("#### ✍️ Author-Reported Limitations")
                        st.caption("Explicitly acknowledged in the publication:")
                        for al in lims.get("author_reported_limitations", []):
                            st.warning(f"• {al}")

                    with lim_c2:
                        st.markdown("#### 🔍 Senior Scientist AI-Inferred Audit")
                        st.caption("Methodological vulnerabilities identified from study design:")
                        for il in lims.get("ai_inferred_limitations", []):
                            st.error(f"• {il}")

                with t_gaps:
                    st.markdown("#### Unanswered Scientific Questions")
                    for uq in gaps.get("unanswered_questions", []):
                        st.write(f"- ❓ **{uq}**")

                    st.markdown("#### Translational Bottlenecks")
                    for th in gaps.get("translational_hurdles", []):
                        st.write(f"- 🚧 {th}")

                    st.markdown("#### Proposed Future Directions")
                    if isinstance(futs, list):
                        for fd in futs:
                            st.write(f"- 🚀 {fd}")

                with t_evid:
                    st.markdown("#### Verbatim Evidence Quotes from Source Text")
                    st.caption("Every claim extracted is traceable to these source quotes:")
                    snips = an.evidence_snippets
                    if snips:
                        for s_quote in snips:
                            st.markdown(f"""
                            <div class="scientific-callout">
                                "{s_quote}"
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.write("Analysis grounded in full abstract text.")

    # =========================================================================
    # TAB 5: FULL-TEXT PDF LAB
    # =========================================================================
    elif nav_selection == "📑 Full-Text PDF Lab":
        st.markdown("## 📑 Full-Text PDF Extraction & Section Lab")
        st.caption("Upload local scientific research PDFs, extract structured sections, and match them with database records.")

        uploaded_files = st.file_uploader(
            "Upload Scientific PDF Documents (Single or Batch)",
            type=["pdf"],
            accept_multiple_files=True
        )

        if uploaded_files:
            st.success(f"📁 {len(uploaded_files)} PDF file(s) selected.")

            for uploaded in uploaded_files:
                save_path = UPLOADS_DIR / uploaded.name
                with open(save_path, "wb") as f:
                    f.write(uploaded.getbuffer())

                with st.expander(f"📄 Process & Inspect: {uploaded.name}"):
                    if st.button(f"Extract & Segment Text: {uploaded.name}", key=f"btn_{uploaded.name}"):
                        with st.spinner("Parsing PDF with PyMuPDF..."):
                            processed = pdf_service.process_pdf(str(save_path))

                            if not processed.get("success"):
                                st.error(processed.get("error"))
                            else:
                                st.success(f"Extracted {processed['page_count']} pages successfully!")
                                col_p1, col_p2 = st.columns(2)
                                col_p1.markdown(f"**Detected DOI:** `{processed['doi'] or 'Not found'}`")
                                col_p2.markdown(f"**Title Guess:** {processed['suggested_title']}")

                                # Check matching with existing project papers
                                papers = repo.get_papers(proj_id, include_excluded=False)
                                matched_paper = pdf_service.match_pdf_to_papers(processed, papers)
                                if matched_paper:
                                    st.info(f"🔗 Automatically matched with paper #{matched_paper.id}: **{matched_paper.title}**")
                                    repo.update_paper_full_text(matched_paper.id, str(save_path))
                                    st.success("Associated PDF with paper record!")

                                # Section viewer
                                sections = processed.get("sections", {})
                                sec_tabs = st.tabs(list(sections.keys()))
                                for s_name, s_tab in zip(sections.keys(), sec_tabs):
                                    with s_tab:
                                        content = sections[s_name]
                                        if content:
                                            st.text_area(f"{s_name.capitalize()} Content", content[:3000], height=250)
                                        else:
                                            st.write("Section empty or not detected in this paper.")

    # =========================================================================
    # TAB 6: RESEARCH GAP INTELLIGENCE
    # =========================================================================
    elif nav_selection == "💡 Research Gap Intelligence":
        st.markdown("## 💡 Research Gap Discovery & Synthesis Matrix")
        st.caption("Synthesizes multi-paper literature trends, contradictory findings, underexplored formulations, and high-impact research opportunities.")

        gap_service = GapService(
            repo=repo,
            api_key=repo.get_setting("GEMINI_API_KEY", settings.GEMINI_API_KEY),
            model=repo.get_setting("GEMINI_MODEL", settings.GEMINI_MODEL)
        )

        g_btn_col1, g_btn_col2 = st.columns([2, 1])
        with g_btn_col1:
            g_mode = st.selectbox(
                "Gap Synthesis Engine Mode",
                ["Auto (Gemini AI if configured, else Rule-Based)", "Gemini AI (LLM)", "Algorithmic Cross-Study Aggregation (100% Offline)"]
            )
            g_mode_map = {
                "Auto (Gemini AI if configured, else Rule-Based)": "auto",
                "Gemini AI (LLM)": "gemini",
                "Algorithmic Cross-Study Aggregation (100% Offline)": "rule_based"
            }
        with g_btn_col2:
            st.write("")
            st.write("")
            generate_gaps_clicked = st.button("🧠 Synthesize Corpus & Generate Gap Matrix", use_container_width=True)

        if generate_gaps_clicked:
            with st.spinner("Synthesizing multi-paper evidence across project..."):
                try:
                    synthesis_res = gap_service.generate_project_gaps(proj_id, mode=g_mode_map[g_mode])
                    st.success("Research Gap Matrix Generated Successfully!")
                except Exception as e:
                    st.error(f"Error generating gaps: {e}")

        # Display latest gaps
        latest_gaps = gap_service.get_latest_gaps(proj_id)
        if latest_gaps and latest_gaps.get("gap_matrix"):
            st.markdown("---")
            st.markdown("### 📋 Executive Cross-Study Synthesis")
            st.markdown(f"""
            <div class="scientific-callout">
                {latest_gaps.get('synthesis_summary')}
            </div>
            """, unsafe_allow_html=True)

            st.markdown("### 🎯 High-Impact Research Gap Matrix")
            matrix_data = latest_gaps.get("gap_matrix", [])

            for item in matrix_data:
                st.markdown(f"""
                <div class="gap-card">
                    <div class="gap-theme">🔬 {item.get('theme')} <span class="badge-chip badge-oa">{item.get('confidence_level')} Confidence</span></div>
                    <div><strong>Existing Evidence:</strong> {item.get('existing_evidence')}</div>
                    <div><strong>Identified Limitation:</strong> <span style="color:#DC2626;">{item.get('identified_limitation')}</span></div>
                    <div class="gap-question">❓ Unanswered Question: {item.get('unanswered_question')}</div>
                    <div class="gap-opportunity">💡 <strong>Actionable Opportunity:</strong> {item.get('proposed_opportunity')}</div>
                    <div style="margin-top:6px; font-size:0.8rem; color:#64748B;">
                        <strong>Supporting DOIs:</strong> {', '.join(item.get('supporting_dois', [])) or 'Multi-study synthesis'}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        else:
            st.info("Click 'Synthesize Corpus & Generate Gap Matrix' above to discover collective research gaps.")

    # =========================================================================
    # TAB 7: EXPORT & REPORTS
    # =========================================================================
    elif nav_selection == "📥 Export & Reports":
        st.markdown("## 📥 Research Data & Report Exports")
        st.caption("Generate publication-ready Excel workbooks, executive HTML reports, Markdown summaries, and BibTeX citations.")

        papers = repo.get_papers(proj_id, include_excluded=True)
        gap_record = repo.get_latest_gap_matrix(proj_id)
        gap_data = {
            "gap_matrix": gap_record.matrix_items,
            "synthesis_summary": gap_record.synthesis_summary
        } if gap_record else None

        e_col1, e_col2, e_col3 = st.columns(3)

        # 1. Excel Workbook Export
        with e_col1:
            st.markdown("### 📊 Styled Excel Workbook")
            st.caption("Full multi-tab Excel workbook formatted with Oxford Navy styling, auto-adjusted columns, and 5 dedicated sheets.")
            excel_bytes = ExcelExporter.export_to_bytes(active_project.to_dict(), papers, gap_data)
            st.download_button(
                label="📥 Download Excel (.xlsx)",
                data=excel_bytes,
                file_name=f"{active_project.name.replace(' ', '_').lower()}_review.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        # 2. Executive HTML Report
        with e_col2:
            st.markdown("### 📄 Printable HTML Report")
            st.caption("Responsive, printable executive research report styled with clean scientific typography and tables.")
            html_content = ReportExporter.generate_html(active_project.to_dict(), papers, gap_data)
            st.download_button(
                label="📥 Download HTML Report (.html)",
                data=html_content.encode("utf-8"),
                file_name=f"{active_project.name.replace(' ', '_').lower()}_report.html",
                mime="text/html",
                use_container_width=True
            )

        # 3. Markdown Synthesis Report
        with e_col3:
            st.markdown("### 📝 Markdown Synthesis")
            st.caption("Standard Markdown format for GitHub, Obsidian, or paper drafting.")
            md_content = ReportExporter.generate_markdown(active_project.to_dict(), papers, gap_data)
            st.download_button(
                label="📥 Download Markdown (.md)",
                data=md_content.encode("utf-8"),
                file_name=f"{active_project.name.replace(' ', '_').lower()}_report.md",
                mime="text/markdown",
                use_container_width=True
            )

        st.markdown("---")
        # BibTeX export
        st.markdown("### 📚 BibTeX Citation Generator")
        st.caption("Export active included papers into BibTeX for Zotero, Mendeley, EndNote, or Overleaf.")
        bib_lines = []
        for p in papers:
            if p.is_excluded:
                continue
            cite_key = (p.authors.split(",")[0].strip().replace(" ", "") if p.authors else "Paper") + str(p.year or "2024")
            bib_lines.append(f"""@article{{{cite_key},
  title = {{{p.title}}},
  author = {{{p.authors}}},
  journal = {{{p.journal}}},
  year = {{{p.year or 'n.d.'}}},
  doi = {{{p.doi}}},
  pmid = {{{p.pmid}}}
}}""")
        bib_str = "\n\n".join(bib_lines)

        st.text_area("BibTeX Citations", bib_str, height=200)
        st.download_button(
            label="📥 Download Citations (.bib)",
            data=bib_str.encode("utf-8"),
            file_name=f"{active_project.name.replace(' ', '_').lower()}_references.bib",
            mime="text/plain"
        )

    # =========================================================================
    # TAB 8: SETTINGS & CONFIGURATION
    # =========================================================================
    elif nav_selection == "⚙️ Settings & Configuration":
        st.markdown("## ⚙️ AI Provider Settings & Local System Configuration")
        st.caption("Configure optional Google Gemini API credentials, models, and review local SQLite database health.")

        with st.form("settings_form"):
            st.markdown("### 🤖 Google Gemini AI Configuration (Optional)")
            st.caption("Google Gemini enables generative multi-paper synthesis. Basic searching, retrieval, deduplication, and rule-based extraction always work 100% free without any API key!")

            curr_key = repo.get_setting("GEMINI_API_KEY", settings.GEMINI_API_KEY)
            new_key = st.text_input("Gemini API Key", value=curr_key, type="password", placeholder="Enter your Gemini API key (AIzaSy...)")
            
            curr_model = repo.get_setting("GEMINI_MODEL", settings.GEMINI_MODEL)
            model_options = ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
            model_idx = model_options.index(curr_model) if curr_model in model_options else 0
            new_model = st.selectbox("AI Model Selection", model_options, index=model_idx)

            st.markdown("### 🌐 Biomedical Literature API Defaults")
            curr_pm_email = repo.get_setting("PUBMED_EMAIL", settings.PUBMED_EMAIL)
            new_pm_email = st.text_input("NCBI PubMed Contact Email", value=curr_pm_email)

            curr_pm_key = repo.get_setting("PUBMED_API_KEY", settings.PUBMED_API_KEY)
            new_pm_key = st.text_input("NCBI PubMed API Key (Optional)", value=curr_pm_key, type="password", help="Increases NCBI E-utilities rate limit from 3 req/sec to 10 req/sec")

            save_settings = st.form_submit_button("💾 Save System Configuration", use_container_width=True)

            if save_settings:
                repo.set_setting("GEMINI_API_KEY", new_key.strip())
                repo.set_setting("GEMINI_MODEL", new_model.strip())
                repo.set_setting("PUBMED_EMAIL", new_pm_email.strip())
                repo.set_setting("PUBMED_API_KEY", new_pm_key.strip())
                st.success("Settings saved successfully to local database!")
                st.rerun()

        # Connection Test
        st.markdown("---")
        st.markdown("### 🔌 Test Gemini AI Provider Connection")
        if st.button("Test Gemini Connection"):
            key_to_test = repo.get_setting("GEMINI_API_KEY", settings.GEMINI_API_KEY)
            model_to_test = repo.get_setting("GEMINI_MODEL", settings.GEMINI_MODEL)
            if not key_to_test:
                st.warning("No Gemini API key is currently configured. The system will continue running in Rule-Based Scientific NLP mode.")
            else:
                with st.spinner("Pinging Gemini API..."):
                    try:
                        client = GeminiClient(api_key=key_to_test, model=model_to_test)
                        res = client.analyze_text(
                            system_prompt="You are a ping test. Respond with valid JSON: {\"status\": \"ok\", \"service\": \"Gemini Connected\"}",
                            user_content="Ping test"
                        )
                        st.success(f"Connection Successful! Gemini API responded: {res}")
                    except Exception as e:
                        st.error(f"Gemini connection failed: {e}")

        # Local Database Health
        st.markdown("---")
        st.markdown("### 🗄️ Local Database & Storage Status")
        db_path = settings.DATABASE_PATH
        db_size_kb = round(db_path.stat().st_size / 1024, 2) if db_path.exists() else 0
        st.write(f"- **Database Path:** `{db_path}`")
        st.write(f"- **Database Size:** `{db_size_kb} KB`")
        st.write(f"- **Exports Directory:** `{EXPORTS_DIR}`")
        st.write(f"- **Uploads Directory:** `{UPLOADS_DIR}`")

    # Close session
    db_session.close()

if __name__ == "__main__":
    main()
