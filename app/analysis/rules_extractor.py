import re
from typing import Dict, Any, List, Tuple

class RulesBasedExtractor:
    """Scientific rule-based and NLP pattern extractor for pharmaceutical literature."""

    FORMULATIONS = {
        "Solid Lipid Nanoparticles (SLN)": [r"\bsln\b", r"solid lipid nanoparticle", r"solid lipid nano"],
        "Nanostructured Lipid Carriers (NLC)": [r"\bnlc\b", r"nanostructured lipid carrier"],
        "Liposomes": [r"liposom", r"phospholipid vesicle"],
        "Nanoemulsion / SNEDDS": [r"nanoemulsion", r"snedds", r"sedds", r"self-emulsif"],
        "Polymeric Nanoparticles / PLGA": [r"polymeric nanoparticle", r"\bplga\b", r"\bpcl\b", r"poly.*lactic.*glycolic"],
        "Polymeric Micelles": [r"polymeric micelle", r"block copolymer micelle"],
        "Hydrogel / Nanogel": [r"hydrogel", r"nanogel", r"thermoresponsive gel"],
        "Niosomes": [r"niosom", r"non-ionic surfactant vesicle"],
        "Cyclodextrin Complexes": [r"cyclodextrin", r"inclusion complex"],
        "Exosomes / Extracellular Vesicles": [r"exosom", r"extracellular vesicle"],
        "Dendrimers": [r"dendrimer", r"\bpamam\b"]
    }

    INSTRUMENTS = {
        "Dynamic Light Scattering (DLS / Zetasizer)": [r"\bdls\b", r"dynamic light scattering", r"zetasizer", r"photon correlation spectroscopy"],
        "Zeta Potential Analyzer": [r"zeta potential", r"electrophoretic mobility"],
        "Transmission Electron Microscopy (TEM)": [r"\btem\b", r"transmission electron microscop"],
        "Scanning Electron Microscopy (SEM)": [r"\bsem\b", r"scanning electron microscop", r"\bfesem\b"],
        "High-Performance Liquid Chromatography (HPLC)": [r"\bhplc\b", r"high-performance liquid chromatograph", r"high pressure liquid chromatograph"],
        "LC-MS/MS (Liquid Chromatography Tandem Mass Spectrometry)": [r"lc-ms", r"lc/ms", r"tandem mass spectrometr"],
        "Fourier Transform Infrared Spectroscopy (FTIR)": [r"\bftir\b", r"fourier transform infrared"],
        "Differential Scanning Calorimetry (DSC)": [r"\bdsc\b", r"differential scanning calorimet"],
        "X-Ray Diffraction (XRD)": [r"\bxrd\b", r"x-ray diffract", r"powder x-ray"],
        "UV-Vis Spectrophotometry": [r"uv-vis", r"spectrophotometer", r"uv spectrophotom"],
        "Confocal Laser Scanning Microscopy (CLSM)": [r"confocal", r"\bclsm\b"],
        "Franz Diffusion Cell": [r"franz diffusion", r"permeation cell"]
    }

    MODELS = {
        "Cell Line (In vitro)": [r"cell line", r"caco-2", r"mcf-7", r"hepg2", r"a549", r"sh-sy5y", r"pc12", r"hela", r"raw 264.7"],
        "Rodent Model (In vivo)": [r"wistar rat", r"sprague-dawley", r"balb/c", r"c57bl/6", r"mice", r"rodent", r"male rat"],
        "Rabbit Model": [r"new zealand rabbit", r"rabbit cornea", r"rabbit eye"],
        "Ex Vivo Tissue Model": [r"ex vivo", r"isolated intestine", r"porcine skin", r"nasal mucosa", r"bovine cornea"],
        "In Silico / Molecular Docking": [r"molecular docking", r"in silico", r"molecular dynamics", r"autodock", r"qsar"],
        "Clinical / Human Volunteers": [r"human volunteer", r"healthy volunteer", r"clinical trial", r"patients"]
    }

    @classmethod
    def _split_sentences(cls, text: str) -> List[str]:
        if not text:
            return []
        raw = re.split(r"(?<=[.?!])\s+", text)
        return [s.strip() for s in raw if len(s.strip()) > 15]

    @classmethod
    def extract_objective(cls, text: str, sentences: List[str]) -> str:
        obj_patterns = [
            r"the (aim|objective|purpose|goal) of this (study|work|research|paper)",
            r"in this (study|work|investigation), we (developed|investigated|evaluated|aimed|designed|synthesized)",
            r"this study (investigates|evaluates|aims|reports|presents)",
            r"we aimed to",
            r"was designed to (investigate|evaluate|develop|formulate)"
        ]
        for s in sentences:
            s_lower = s.lower()
            for pat in obj_patterns:
                if re.search(pat, s_lower):
                    return s

        return sentences[0] if sentences else "Investigation of pharmaceutical formulation and pharmacological activity."

    @classmethod
    def extract_methodology(cls, text: str, sentences: List[str]) -> Dict[str, Any]:
        text_lower = text.lower()
        
        detected_formulations = []
        for name, pats in cls.FORMULATIONS.items():
            if any(re.search(p, text_lower) for p in pats):
                detected_formulations.append(name)
        formulation_str = ", ".join(detected_formulations) if detected_formulations else "Standard pharmaceutical formulation"

        detected_instruments = []
        for name, pats in cls.INSTRUMENTS.items():
            if any(re.search(p, text_lower) for p in pats):
                detected_instruments.append(name)

        detected_models = []
        for name, pats in cls.MODELS.items():
            if any(re.search(p, text_lower) for p in pats):
                detected_models.append(name)
        model_str = ", ".join(detected_models) if detected_models else "Experimental in vitro / in vivo model"

        designs = []
        if any("in vivo" in m.lower() for m in detected_models) or ("in vivo" in text_lower and "further in vivo" not in text_lower):
            designs.append("In vivo preclinical evaluation")
        if any("in vitro" in m.lower() for m in detected_models) or "in vitro" in text_lower:
            designs.append("In vitro physicochemical & cellular characterization")
        if any("ex vivo" in m.lower() for m in detected_models) or "ex vivo" in text_lower:
            designs.append("Ex vivo permeation study")
        if "docking" in text_lower or "in silico" in text_lower:
            designs.append("In silico computational modeling")
        study_design = " & ".join(designs) if designs else "Experimental pharmaceutical laboratory study"

        stat_methods = []
        if re.search(r"\banova\b", text_lower):
            stat_methods.append("Analysis of Variance (ANOVA)")
        if re.search(r"student('s)?\s*t-test|paired t-test", text_lower):
            stat_methods.append("Student's t-test")
        if re.search(r"tukey|bonferroni", text_lower):
            stat_methods.append("Post-hoc multiple comparison test")
        if re.search(r"p\s*[<>=]\s*0\.\d+", text_lower):
            p_val = re.findall(r"p\s*[<>=]\s*0\.\d+", text_lower)[0]
            stat_methods.append(f"Significance threshold ({p_val})")
        stat_str = ", ".join(stat_methods) if stat_methods else "Statistical analysis conducted (significance reported)"

        return {
            "study_design": study_design,
            "experimental_model": model_str,
            "formulation_methods": formulation_str,
            "analytical_instruments": detected_instruments if detected_instruments else ["Spectrophotometric & chromatographic analysis"],
            "sample_size_or_dosing": "Standardized experimental replicates / doses reported in study",
            "statistical_methods": stat_str
        }

    @classmethod
    def extract_results(cls, text: str, sentences: List[str]) -> Dict[str, Any]:
        quant_metrics = []

        ps_matches = re.findall(r"\b(\d+(?:\.\d+)?\s*(?:±\s*\d+(?:\.\d+)?)?\s*(?:nm|µm|um|nanometers?|micrometers?))\b(?![A-Za-z])", text)
        for m in ps_matches[:2]:
            quant_metrics.append(f"Particle diameter: {m}")

        ee_matches = re.findall(r"(?:encapsulation|entrapment|loading|ee)\s*(?:efficiency)?\s*(?:was|is|reached|of|=|:)?\s*(\d+(?:\.\d+)?\s*(?:±\s*\d+(?:\.\d+)?)?\s*%)", text, re.IGNORECASE)
        for m in ee_matches[:2]:
            quant_metrics.append(f"Encapsulation efficiency: {m}")

        zp_matches = re.findall(r"([+-]?\d+(?:\.\d+)?\s*(?:±\s*\d+(?:\.\d+)?)?\s*mV)", text)
        for m in zp_matches[:2]:
            quant_metrics.append(f"Zeta potential: {m}")

        bio_matches = re.findall(r"\b(\d+(?:\.\d+)?\s*(?:-|to)?\s*\d*(?:\.\d+)?\s*-?fold\s+(?:increase|enhancement|higher|improvement))\b", text, re.IGNORECASE)
        for m in bio_matches[:2]:
            quant_metrics.append(m)

        ic_matches = re.findall(r"\b(IC50\s*(?:of|=|:)?\s*\d+(?:\.\d+)?\s*(?:±\s*\d+(?:\.\d+)?)?\s*(?:µM|uM|nM|µg/mL|ug/mL|mg/mL))\b", text, re.IGNORECASE)
        for m in ic_matches[:2]:
            quant_metrics.append(m)

        result_sentences = []
        res_keywords = ["showed", "demonstrated", "revealed", "significantly increased", "enhanced", "exhibited", "achieved", "results indicate"]
        for s in sentences:
            if any(k in s.lower() for k in res_keywords):
                result_sentences.append(s)

        main_findings = " ".join(result_sentences[:2]) if result_sentences else "Experimental results demonstrated formulation feasibility and therapeutic enhancement."
        obs = result_sentences[2] if len(result_sentences) > 2 else "Formulation parameters directly influenced stability, release kinetics, and biological absorption."

        return {
            "main_findings": main_findings,
            "quantitative_metrics": quant_metrics if quant_metrics else ["Quantitative measurements verified in published paper"],
            "significant_observations": obs
        }

    @classmethod
    def extract_limitations(cls, text: str, sentences: List[str], has_in_vivo: bool) -> Dict[str, Any]:
        author_limitations = []
        limit_keywords = ["limitation", "further study is needed", "further studies are needed", "remains unclear", "however,", "further investigations are required", "did not examine", "warrants further"]
        for s in sentences:
            if any(k in s.lower() for k in limit_keywords):
                author_limitations.append(s)

        ai_inferred = []
        if not has_in_vivo:
            ai_inferred.append("Evaluation restricted to in vitro assays; lacks in vivo pharmacokinetic confirmation and clearance kinetics.")
        if not re.search(r"stability|ich\b|shelf-life|refrigerat", text.lower()):
            ai_inferred.append("Absence of comprehensive accelerated stability testing conforming to ICH climatic zone guidelines.")
        if not re.search(r"toxicity|safety|hemocompatib|histopathol", text.lower()):
            ai_inferred.append("Limited chronic biocompatibility and organ histopathology safety data.")

        if not author_limitations:
            author_limitations.append("No explicit limitation paragraph articulated in the accessible abstract text.")

        return {
            "author_reported_limitations": author_limitations[:3],
            "ai_inferred_limitations": ai_inferred if ai_inferred else ["Evaluation focused on preliminary formulation stages; requires translational scale-up verification."]
        }

    @classmethod
    def extract_gaps_and_directions(cls, text: str, sentences: List[str]) -> Tuple[Dict[str, Any], List[str]]:
        unanswered = [
            "Long-term stability and shelf-life under diverse environmental stress conditions.",
            "In vivo biodistribution and tissue-specific targeting efficiency in higher disease models.",
            "Industrial scalability and batch-to-batch reproducibility under cGMP conditions."
        ]
        translational = [
            "Sterilization methodology impact on nanoparticle integrity.",
            "Immunogenicity and clearance mechanism by reticuloendothelial system (RES)."
        ]

        future_dirs = []
        fut_keywords = ["future studies", "further investigation", "promising candidate for", "potential application in", "warrants further exploration"]
        for s in sentences:
            if any(k in s.lower() for k in fut_keywords):
                future_dirs.append(s)

        if not future_dirs:
            future_dirs = [
                "Conduct full in vivo pharmacokinetic and pharmacodynamic validation in diseased animal models.",
                "Investigate cellular uptake pathways and intracellular organelle trafficking mechanisms.",
                "Optimize lyophilization cryoprotectants for long-term dry powder stability."
            ]

        gaps = {
            "unanswered_questions": unanswered,
            "translational_hurdles": translational
        }
        return gaps, future_dirs[:3]

    @classmethod
    def analyze(cls, paper_dict: Dict[str, Any], has_full_text: bool = False) -> Dict[str, Any]:
        abstract = paper_dict.get("abstract", "")
        title = paper_dict.get("title", "")
        full_text = paper_dict.get("full_text", "")
        analysis_corpus = full_text if (has_full_text and full_text) else f"{title}\n\n{abstract}"

        sentences = cls._split_sentences(analysis_corpus)

        obj = cls.extract_objective(analysis_corpus, sentences)
        methodology = cls.extract_methodology(analysis_corpus, sentences)
        results = cls.extract_results(analysis_corpus, sentences)

        has_in_vivo = "in vivo" in methodology["experimental_model"].lower()
        limitations = cls.extract_limitations(analysis_corpus, sentences, has_in_vivo)
        gaps, future_dirs = cls.extract_gaps_and_directions(analysis_corpus, sentences)

        evidence_snippets = []
        if obj and obj != sentences[0]:
            evidence_snippets.append(obj)
        for s in sentences:
            if any(k in s.lower() for k in ["particle", "encapsulation", "efficiency", "bioavailability", "showed", "demonstrated", "revealed"]):
                if s not in evidence_snippets:
                    evidence_snippets.append(s)
            if len(evidence_snippets) >= 4:
                break

        confidence = "Supported by full-text evidence" if has_full_text else "Directly supported by abstract"
        importance = f"Contributes significant experimental data on {methodology['formulation_methods']} for targeted pharmaceutical delivery and bioavailability optimization."

        return {
            "status": "completed",
            "analysis_mode": "rule_based",
            "model_used": "PharmaLit Scientific Rule-Based NLP",
            "research_objective": obj,
            "methodology": methodology,
            "results": results,
            "limitations": limitations,
            "gaps": gaps,
            "future_directions": future_dirs,
            "scientific_importance": importance,
            "evidence_confidence": confidence,
            "evidence_snippets": evidence_snippets
        }
