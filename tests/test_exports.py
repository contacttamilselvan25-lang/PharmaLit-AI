import pytest
import io
import openpyxl
from app.exports.excel_exporter import ExcelExporter
from app.exports.report_exporter import ReportExporter

class MockAnalysis:
    status = "completed"
    analysis_mode = "rule_based"
    evidence_confidence = "Directly supported by abstract"
    research_objective = "To evaluate nanocarriers"
    methodology = {"study_design": "In vitro", "analytical_instruments": ["DLS", "HPLC"], "formulation_methods": "SLN"}
    results = {"main_findings": "High entrapment", "quantitative_metrics": ["Size: 130 nm", "EE: 90%"]}
    limitations = {"author_reported_limitations": ["Short duration"], "ai_inferred_limitations": ["No in vivo"]}
    gaps = {"unanswered_questions": ["Long-term stability"]}
    future_directions = ["Animal studies"]
    scientific_importance = "Novel drug delivery"
    evidence_snippets = ["Size: 130 nm"]

class MockPaper:
    id = 1
    title = "Curcumin SLN Study"
    authors = "Kakkar et al."
    year = 2021
    journal = "Int J Pharm"
    doi = "10.1016/j.ijpharm.2021.120485"
    pmid = "33744412"
    pmcid = "PMC8012345"
    database_source = "PubMed"
    is_open_access = True
    is_excluded = False
    abstract = "Abstract text about lipid nanoparticles."
    has_full_text = False
    analysis = MockAnalysis()

def test_excel_export_structure():
    proj = {
        "name": "Test Project",
        "therapeutic_area": "Neurology",
        "target_drug": "Curcumin",
        "description": "Test description",
        "updated_at": "2026-01-01"
    }
    papers = [MockPaper()]
    gap_data = {
        "synthesis_summary": "Test synthesis summary.",
        "gap_matrix": [
            {
                "theme": "Pharmacokinetics",
                "existing_evidence": "In vitro release",
                "supporting_papers_count": 1,
                "identified_limitation": "No in vivo",
                "unanswered_question": "Bioavailability?",
                "proposed_opportunity": "Run PK study",
                "supporting_dois": ["10.1016/j.ijpharm.2021.120485"],
                "confidence_level": "High"
            }
        ]
    }

    raw_bytes = ExcelExporter.export_to_bytes(proj, papers, gap_data)
    assert len(raw_bytes) > 2000

    wb = openpyxl.load_workbook(io.BytesIO(raw_bytes))
    sheet_names = wb.sheetnames
    assert "Project Summary" in sheet_names
    assert "Collected Papers" in sheet_names
    assert "Detailed AI Analysis" in sheet_names
    assert "Research Gap Matrix" in sheet_names
    assert "Evidence Snippets" in sheet_names

    ws_papers = wb["Collected Papers"]
    assert ws_papers.cell(row=2, column=2).value == "Curcumin SLN Study"

def test_report_export():
    proj = {"name": "Test Report", "therapeutic_area": "Oncology", "target_drug": "Paclitaxel"}
    papers = [MockPaper()]
    gap_data = {"synthesis_summary": "Executive summary text."}

    md = ReportExporter.generate_markdown(proj, papers, gap_data)
    assert "# PharmaLit AI — Research Intelligence Report" in md
    assert "Curcumin SLN Study" in md

    html = ReportExporter.generate_html(proj, papers, gap_data)
    assert "<!DOCTYPE html>" in html
    assert "PharmaLit AI" in html
