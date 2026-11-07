import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Base
from app.database.repository import Repository

@pytest.fixture
def in_memory_repo():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    repo = Repository(session)
    yield repo
    session.close()

def test_project_crud(in_memory_repo):
    p = in_memory_repo.create_project(
        name="Targeted Glioblastoma Therapy",
        description="Nanocarriers for BBB crossing",
        therapeutic_area="Oncology",
        target_drug="Temozolomide"
    )
    assert p.id is not None
    assert p.name == "Targeted Glioblastoma Therapy"

    all_projs = in_memory_repo.get_projects()
    assert len(all_projs) == 1

    fetched = in_memory_repo.get_project_by_id(p.id)
    assert fetched.target_drug == "Temozolomide"

def test_paper_and_exclusion(in_memory_repo):
    p = in_memory_repo.create_project(name="Test Proj")
    paper_data = {
        "title": "Lipid Nanoparticles in Drug Delivery",
        "authors": "Smith, J., Doe, A.",
        "year": 2023,
        "journal": "Pharm Res",
        "doi": "10.1007/s11095-023-01234-x",
        "pmid": "12345678",
        "abstract": "Test abstract content."
    }
    paper = in_memory_repo.add_paper(p.id, paper_data)
    assert paper.id is not None
    assert paper.is_excluded is False

    # Exclude paper
    in_memory_repo.update_paper_exclusion(paper.id, is_excluded=True, reason="Irrelevant study design")
    updated = in_memory_repo.get_paper_by_id(paper.id)
    assert updated.is_excluded is True
    assert updated.exclusion_reason == "Irrelevant study design"

def test_analysis_persistence(in_memory_repo):
    p = in_memory_repo.create_project(name="Analysis Test")
    paper = in_memory_repo.add_paper(p.id, {"title": "Sample Paper", "abstract": "Sample abstract"})

    analysis_data = {
        "status": "completed",
        "analysis_mode": "rule_based",
        "model_used": "PharmaLit NLP",
        "research_objective": "To test nanocarrier formulation stability.",
        "methodology": {"study_design": "In vitro"},
        "results": {"main_findings": "Enhanced stability by 40%."},
        "limitations": {"author_reported_limitations": ["In vitro only"]},
        "gaps": {"unanswered_questions": ["In vivo kinetics"]},
        "future_directions": ["Test in animal model"],
        "scientific_importance": "Critical for formulation science.",
        "evidence_confidence": "Directly supported by abstract",
        "evidence_snippets": ["Enhanced stability by 40%."]
    }

    an = in_memory_repo.save_analysis(paper.id, analysis_data)
    assert an.id is not None
    assert an.research_objective == "To test nanocarrier formulation stability."
    assert an.methodology["study_design"] == "In vitro"
    assert len(an.evidence_snippets) == 1

def test_dashboard_metrics(in_memory_repo):
    p = in_memory_repo.create_project(name="Metrics Proj")
    in_memory_repo.add_paper(p.id, {"title": "Paper 1", "year": 2021, "doi": "10.1016/1", "journal": "JCR", "database_source": "PubMed"})
    in_memory_repo.add_paper(p.id, {"title": "Paper 2", "year": 2022, "doi": "10.1016/2", "journal": "IJP", "database_source": "Europe PMC"})

    metrics = in_memory_repo.get_dashboard_metrics(p.id)
    assert metrics["total_papers"] == 2
    assert metrics["unique_papers"] == 2
    assert metrics["with_doi"] == 2
    assert metrics["years_dist"]["2021"] == 1
    assert metrics["years_dist"]["2022"] == 1
    assert "PubMed" in metrics["sources_dist"]
    assert "Europe PMC" in metrics["sources_dist"]
