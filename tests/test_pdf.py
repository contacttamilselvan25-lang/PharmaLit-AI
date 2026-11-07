import pytest
from app.services.pdf_service import PDFService

def test_doi_regex():
    sample_texts = [
        ("Published at https://doi.org/10.1016/j.ijpharm.2021.120485 for review", "10.1016/j.ijpharm.2021.120485"),
        ("doi: 10.1021/acs.molpharmaceut.1c00222. Received 12 Jan", "10.1021/acs.molpharmaceut.1c00222")
    ]
    for text, expected in sample_texts:
        m = PDFService.DOI_REGEX.search(text)
        assert m is not None
        assert expected in m.group(0)

def test_identify_sections():
    sample_paper = """
Abstract
This study investigates nanostructured lipid carriers for oral delivery.

1. Introduction
Poor water solubility limits the therapeutic usage of hydrophobic drugs.

2. Materials and Methods
Lipids were purchased from Gattefosse. SLNs were prepared by hot homogenization.

3. Results and Discussion
Formulation showed 130 nm diameter and 90% entrapment.

4. Conclusion
Lipid nanocarriers significantly enhance oral bioavailability.

References
1. Smith et al. J Control Release. 2020.
"""
    sections = PDFService.identify_sections(sample_paper)
    assert len(sections["abstract"]) > 0
    assert len(sections["introduction"]) > 0
    assert len(sections["methods"]) > 0
    assert len(sections["results"]) > 0
    assert len(sections["conclusion"]) > 0
