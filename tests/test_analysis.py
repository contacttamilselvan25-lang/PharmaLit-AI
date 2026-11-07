import pytest
from app.analysis.rules_extractor import RulesBasedExtractor

def test_extract_objective():
    text = (
        "Alzheimer's disease is characterized by amyloid beta plaques. "
        "The objective of this study was to design and evaluate curcumin-loaded solid lipid nanoparticles "
        "for enhanced nose-to-brain delivery. Formulations were characterized by dynamic light scattering."
    )
    sentences = RulesBasedExtractor._split_sentences(text)
    obj = RulesBasedExtractor.extract_objective(text, sentences)
    assert "objective of this study was to design" in obj.lower()

def test_extract_methodology_and_instruments():
    text = (
        "Nanoparticles were formulated by high-pressure homogenization. "
        "Particle size was measured using Dynamic Light Scattering (DLS) with a Zetasizer Nano ZS. "
        "Morphology was verified by Transmission Electron Microscopy (TEM). "
        "Drug content was quantified by HPLC at 425 nm. "
        "Cell viability was assessed in SH-SY5Y neuroblastoma cells."
    )
    sentences = RulesBasedExtractor._split_sentences(text)
    meth = RulesBasedExtractor.extract_methodology(text, sentences)

    assert "Solid Lipid Nanoparticles (SLN)" in meth["formulation_methods"] or "Nanostructured" in meth["formulation_methods"] or "Standard" in meth["formulation_methods"]
    inst_names = " ".join(meth["analytical_instruments"])
    assert "DLS" in inst_names or "Dynamic Light Scattering" in inst_names
    assert "TEM" in inst_names or "Transmission Electron" in inst_names
    assert "HPLC" in inst_names

def test_extract_quantitative_metrics():
    text = (
        "The optimized formulation exhibited a mean particle size of 142.5 ± 3.8 nm and a zeta potential of -28.4 ± 1.2 mV. "
        "The encapsulation efficiency was 89.4 ± 2.1%. In vivo pharmacokinetic evaluation showed a 4.5-fold increase in oral bioavailability. "
        "The IC50 was 12.5 µM against MCF-7 cells."
    )
    sentences = RulesBasedExtractor._split_sentences(text)
    res = RulesBasedExtractor.extract_results(text, sentences)

    metrics = " ".join(res["quantitative_metrics"])
    assert "142.5" in metrics
    assert "89.4" in metrics or "encapsulation" in metrics.lower()
    assert "-28.4" in metrics
    assert "4.5-fold" in metrics or "fold" in metrics

def test_extract_limitations_and_scientific_audit():
    text = (
        "In this work, we synthesized polymeric micelles in vitro. "
        "However, further studies are needed to evaluate long-term in vivo biodistribution. "
        "The formulation showed 85% release after 24 hours."
    )
    sentences = RulesBasedExtractor._split_sentences(text)
    lims = RulesBasedExtractor.extract_limitations(text, sentences, has_in_vivo=False)

    # Check author-reported limitation was caught
    auth_lims = " ".join(lims["author_reported_limitations"])
    assert "further studies are needed" in auth_lims.lower()

    # Check AI-inferred limitation deduced lack of in vivo confirmation
    ai_lims = " ".join(lims["ai_inferred_limitations"])
    assert "in vitro" in ai_lims.lower() or "in vivo" in ai_lims.lower()
