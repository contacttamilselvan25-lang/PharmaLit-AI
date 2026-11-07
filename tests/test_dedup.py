import pytest
from app.services.dedup_service import DeduplicationService

def test_normalize_doi():
    assert DeduplicationService.normalize_doi("https://doi.org/10.1016/j.ijpharm.2021.120485") == "10.1016/j.ijpharm.2021.120485"
    assert DeduplicationService.normalize_doi("http://dx.doi.org/10.1021/acs.molpharmaceut.1c00222/") == "10.1021/acs.molpharmaceut.1c00222"
    assert DeduplicationService.normalize_doi("10.1016/J.IJPHARM.2021.120485") == "10.1016/j.ijpharm.2021.120485"

def test_title_similarity():
    t1 = "Solid lipid nanoparticles as delivery systems for curcumin in neurological disorders"
    t2 = "Solid Lipid Nanoparticles as Delivery Systems for Curcumin in Neurological Disorders."
    t3 = "Polymeric micelles for paclitaxel delivery in lung cancer chemotherapy"
    
    assert DeduplicationService.calculate_title_similarity(t1, t2) == 1.0
    assert DeduplicationService.calculate_title_similarity(t1, t3) < 0.40

def test_deduplicate_by_doi():
    papers = [
        {
            "title": "Study on Liposomes A",
            "doi": "10.1016/j.jconrel.2020.01.001",
            "pmid": "11111",
            "database_source": "PubMed",
            "abstract": "First abstract"
        },
        {
            "title": "Study on Liposomes A (Europe PMC version)",
            "doi": "10.1016/j.jconrel.2020.01.001",
            "pmid": "",
            "database_source": "Europe PMC",
            "abstract": ""
        }
    ]
    unique, audit = DeduplicationService.deduplicate(papers)
    assert len(unique) == 1
    assert audit["duplicate_count"] == 1
    assert "PubMed" in unique[0]["database_source"]
    assert "Europe PMC" in unique[0]["database_source"]
    assert unique[0]["abstract"] == "First abstract"

def test_deduplicate_by_pmid():
    papers = [
        {"title": "Paper 1", "doi": "", "pmid": "99999", "database_source": "PubMed"},
        {"title": "Paper 1 duplicate", "doi": "", "pmid": "99999", "database_source": "Europe PMC"}
    ]
    unique, audit = DeduplicationService.deduplicate(papers)
    assert len(unique) == 1
    assert audit["duplicate_count"] == 1

def test_deduplicate_by_fuzzy_title_and_year():
    papers = [
        {
            "title": "Formulation and Evaluation of Curcumin Solid Lipid Nanoparticles",
            "year": 2022,
            "doi": "",
            "pmid": ""
        },
        {
            "title": "Formulation and Evaluation of Curcumin Solid Lipid Nanoparticles.",
            "year": 2022,
            "doi": "",
            "pmid": ""
        },
        {
            "title": "Completely Unrelated Research on Monoclonal Antibodies",
            "year": 2022,
            "doi": "",
            "pmid": ""
        }
    ]
    unique, audit = DeduplicationService.deduplicate(papers)
    assert len(unique) == 2
    assert audit["duplicate_count"] == 1
