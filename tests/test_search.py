import pytest
from app.services.search_service import SearchService
from app.integrations.crossref import CrossrefClient

def test_build_query_string():
    q = SearchService.build_query_string(
        topic="Curcumin",
        main_keywords="lipid nanoparticles, bioavailability",
        alt_keywords="SLN, NLC",
        disease_area="Alzheimer's disease",
        drug_api="Curcumin",
        delivery_system="Solid Lipid Nanoparticles",
        methodology="High pressure homogenization"
    )
    assert "(Curcumin)" in q
    assert '"lipid nanoparticles"' in q
    assert '"SLN" OR "NLC"' in q or "SLN" in q
    assert "Alzheimer's disease" in q
    assert "High pressure homogenization" in q

def test_crossref_verification_format():
    client = CrossrefClient()
    # Invalid DOI check
    res = client.verify_doi("")
    assert res["valid"] is False
    assert "error" in res
