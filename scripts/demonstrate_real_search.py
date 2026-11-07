import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.database import SessionLocal, Repository, init_db
from app.services import ProjectService, SearchService, AnalysisService, GapService
from app.exports import ExcelExporter, ReportExporter
from config.settings import EXPORTS_DIR

def run_real_demonstration():
    print("=" * 70)
    print("  PHARMALIT AI — REAL LIVE PHARMACEUTICAL SEARCH DEMONSTRATION")
    print("=" * 70)

    init_db()
    db = SessionLocal()
    repo = Repository(db)
    proj_svc = ProjectService(repo)
    search_svc = SearchService(repo)
    an_svc = AnalysisService(repo)
    gap_svc = GapService(repo)

    # 1. Create a dedicated demonstration project
    proj_name = "Targeted Glioblastoma Nanomedicine Review"
    print(f"\n[Step 1] Creating Project: '{proj_name}'...")
    project = proj_svc.create_project(
        name=proj_name,
        description="Investigation of receptor-targeted nanoparticles and peptide conjugates to traverse the blood-brain barrier for temozolomide chemotherapy in glioblastoma multiforme.",
        therapeutic_area="Neuro-Oncology & Drug Delivery",
        target_drug="Temozolomide"
    )
    print(f"-> Project created successfully with ID: {project.id}")

    # 2. Execute Real Live Multi-Database Literature Search
    print("\n[Step 2] Executing Live Multi-Database Search across PubMed & Europe PMC...")
    query_params = {
        "topic": "Glioblastoma blood brain barrier drug delivery",
        "main_keywords": "temozolomide, nanoparticles",
        "alt_keywords": "liposomes, polymeric micelles",
        "disease_area": "Glioblastoma",
        "drug_api": "Temozolomide",
        "delivery_system": "Nanoparticles",
        "methodology": ""
    }

    def progress_log(ratio, msg):
        print(f"  [{int(ratio*100)}%] {msg}")

    final_papers, audit = search_svc.execute_search(
        project_id=project.id,
        query_params=query_params,
        databases=["PubMed", "Europe PMC"],
        max_papers=15,
        start_year=2020,
        end_year=2024,
        progress_callback=progress_log
    )

    print(f"\n[Step 3] Search & Deduplication Results:")
    print(f"  Total Raw Records Retrieved: {audit['original_count']}")
    print(f"  Duplicate Records Filtered:  {audit['duplicate_count']}")
    print(f"  Clean Unique Papers Saved:   {len(final_papers)}")
    for idx, p in enumerate(final_papers[:5], 1):
        print(f"  {idx}. [{p.get('database_source')}] {p.get('title')[:75]}... (DOI: {p.get('doi', 'N/A')}, Year: {p.get('year')})")

    # 4. Deep Scientific Analysis
    print(f"\n[Step 4] Running Deep Scientific Analysis on Retrieved Papers...")
    analyzed_records = an_svc.analyze_project_papers(project.id, mode="rule_based")
    print(f"-> Deep analysis completed for {len(analyzed_records)} papers.")

    # Inspect first analyzed paper
    first_paper = repo.get_papers(project.id)[0]
    first_an = first_paper.analysis
    print(f"\n[Step 5] Extracted Scientific Evidence for Paper #1:")
    print(f"  Title:       {first_paper.title}")
    print(f"  Objective:   {first_an.research_objective}")
    print(f"  Design:      {first_an.methodology.get('study_design')}")
    print(f"  Instruments: {', '.join(first_an.methodology.get('analytical_instruments', []))}")
    print(f"  Key Finding: {first_an.results.get('main_findings')[:120]}...")
    print(f"  Author Lims: {first_an.limitations.get('author_reported_limitations')}")
    print(f"  AI Audit:    {first_an.limitations.get('ai_inferred_limitations')}")
    print(f"  Confidence:  {first_an.evidence_confidence}")

    # 6. Research Gap Matrix Generation
    print(f"\n[Step 6] Synthesizing Cross-Paper Research Gap Intelligence...")
    gap_result = gap_svc.generate_project_gaps(project.id, mode="rule_based")
    matrix = gap_result.get("gap_matrix", [])
    print(f"-> Generated {len(matrix)} high-impact research gap vectors:")
    for g_idx, item in enumerate(matrix[:3], 1):
        print(f"  {g_idx}. [{item.get('confidence_level')} Confidence] Theme: {item.get('theme')}")
        print(f"     Limitation: {item.get('identified_limitation')}")
        print(f"     Opportunity: {item.get('proposed_opportunity')}")

    # 7. Excel and Report Generation
    print(f"\n[Step 7] Generating Professional Multi-Tab Excel Workbook & HTML Report...")
    all_papers = repo.get_papers(project.id)
    excel_path = EXPORTS_DIR / "real_search_glioblastoma_review.xlsx"
    ExcelExporter.export_to_file(excel_path, project.to_dict(), all_papers, gap_result)
    print(f"-> Excel Workbook exported to: {excel_path} (Size: {excel_path.stat().st_size} bytes)")

    html_path = EXPORTS_DIR / "real_search_glioblastoma_report.html"
    html_content = ReportExporter.generate_html(project.to_dict(), all_papers, gap_result)
    html_path.write_text(html_content, encoding="utf-8")
    print(f"-> HTML Report exported to: {html_path} (Size: {html_path.stat().st_size} bytes)")

    # 8. Verify Persistence on Database Re-open
    print(f"\n[Step 8] Verifying Persistence across Application Restart...")
    db.close()
    
    # Reconnect fresh session
    db_fresh = SessionLocal()
    repo_fresh = Repository(db_fresh)
    persisted_proj = repo_fresh.get_project_by_id(project.id)
    persisted_papers = repo_fresh.get_papers(project.id)
    persisted_analyses = [p for p in persisted_papers if p.analysis]
    print(f"-> Verified: Project '{persisted_proj.name}' reloaded with {len(persisted_papers)} papers and {len(persisted_analyses)} persistent analyses.")
    db_fresh.close()

    print("\n" + "=" * 70)
    print("  LIVE DEMONSTRATION VERIFICATION COMPLETE: ALL SYSTEMS FUNCTIONAL")
    print("=" * 70)

if __name__ == "__main__":
    run_real_demonstration()
