import os
from typing import List, Dict, Any, Optional
from app.database.repository import Repository
from app.database.models import Project
from app.services.analysis_service import AnalysisService
from app.services.gap_service import GapService

class ProjectService:
    def __init__(self, repo: Repository):
        self.repo = repo

    def create_project(self, name: str, description: str = "", therapeutic_area: str = "", target_drug: str = "") -> Project:
        return self.repo.create_project(
            name=name,
            description=description,
            therapeutic_area=therapeutic_area,
            target_drug=target_drug
        )

    def list_projects(self) -> List[Project]:
        return self.repo.get_projects()

    def get_project(self, project_id: int) -> Optional[Project]:
        return self.repo.get_project_by_id(project_id)

    def delete_project(self, project_id: int) -> bool:
        return self.repo.delete_project(project_id)

    def seed_sample_project_if_empty(self) -> Project:
        existing = self.repo.get_projects()
        if existing:
            return existing[0]

        project = self.create_project(
            name="Curcumin-Loaded Lipid Nanocarriers for Neurodegenerative Therapy",
            description="Systematic literature review investigating solid lipid nanoparticles (SLN) and nanostructured lipid carriers (NLC) to bypass the blood-brain barrier and enhance curcumin bioavailability in Alzheimer's disease.",
            therapeutic_area="Neuropharmacology & Neurodegenerative Diseases",
            target_drug="Curcumin (Diferuloylmethane)"
        )

        sample_papers = [
            {
                "title": "Solid lipid nanoparticles as delivery systems for curcumin in neurological disorders: Physicochemical characterization and in vitro neuroprotection",
                "authors": "Kakkar, V., Singh, S., Singla, D., Kaur, I.P.",
                "year": 2021,
                "journal": "International Journal of Pharmaceutics",
                "doi": "10.1016/j.ijpharm.2021.120485",
                "pmid": "33744412",
                "pmcid": "PMC8012345",
                "abstract": "The therapeutic potential of curcumin in Alzheimer's disease is severely hampered by poor aqueous solubility, rapid systemic metabolism, and low blood-brain barrier penetration. In this study, we developed curcumin-loaded solid lipid nanoparticles (C-SLNs) using Compritol 888 ATO and Phospholipon 90G via hot high-pressure homogenization. The optimized C-SLNs exhibited an average particle diameter of 134.6 ± 3.8 nm, a polydispersity index of 0.162, a zeta potential of -28.4 ± 1.2 mV, and an encapsulation efficiency of 89.4 ± 2.1%. In vitro release demonstrated biphasic kinetics with an initial burst release (28% in 2 h) followed by sustained release over 72 h. In SH-SY5Y neuroblastoma cells challenged with amyloid-beta (Abeta1-42), C-SLNs significantly restored cell viability (82.4% vs 46.1% in free curcumin) and reduced intracellular reactive oxygen species (p < 0.001). However, the study did not examine long-term ICH stability under tropical climatic conditions or in vivo pharmacokinetic biodistribution.",
                "publication_type": "Original Research Article",
                "keywords": "Curcumin, Solid lipid nanoparticles, Blood-brain barrier, Neuroprotection, High pressure homogenization",
                "database_source": "PubMed, Europe PMC",
                "url": "https://doi.org/10.1016/j.ijpharm.2021.120485",
                "is_open_access": True
            },
            {
                "title": "Transferrin-functionalized nanostructured lipid carriers enhance brain targeting and oral bioavailability of curcumin in rats",
                "authors": "Ramalingam, P., Ko, Y.T.",
                "year": 2022,
                "journal": "Journal of Controlled Release",
                "doi": "10.1016/j.jconrel.2022.03.018",
                "pmid": "35278541",
                "pmcid": "PMC8998762",
                "abstract": "Active receptor-mediated transcytosis represents a promising strategy to transport neurotherapeutic agents across the blood-brain barrier. We synthesized transferrin-conjugated nanostructured lipid carriers (Tf-C-NLCs) encapsulating curcumin using Precirol ATO 5 and oleic acid. Dynamic light scattering revealed mean hydrodynamic diameter of 168.2 ± 5.4 nm and high entrapment efficiency of 92.3 ± 1.5%. Pharmacokinetic evaluation in male Sprague-Dawley rats demonstrated a 6.2-fold increase in oral bioavailability and a 4.8-fold higher brain accumulation AUC(0-t) compared to unformulated curcumin suspension (p < 0.001). Confocal laser scanning microscopy confirmed rapid cellular internalization via clathrin-dependent endocytosis. Nonetheless, industrial scale-up remains challenging due to the multi-step surface chemical crosslinking required for ligand conjugation.",
                "publication_type": "Original Research Article",
                "keywords": "Transferrin, Nanostructured lipid carriers, Brain targeting, Oral bioavailability, Curcumin",
                "database_source": "PubMed",
                "url": "https://doi.org/10.1016/j.jconrel.2022.03.018",
                "is_open_access": False
            },
            {
                "title": "Nose-to-brain delivery of curcumin-loaded lipid nanoemulsions for neurodegenerative therapy: Formulation optimization and nasal ciliotoxicity",
                "authors": "Shinde, U.A., Modani, S.H., Singh, K.H.",
                "year": 2023,
                "journal": "European Journal of Pharmaceutical Sciences",
                "doi": "10.1016/j.ejps.2023.106512",
                "pmid": "37211109",
                "pmcid": "",
                "abstract": "Intranasal administration offers a direct pathway to circumvent the blood-brain barrier via olfactory and trigeminal nerve pathways. This work aimed to formulate and evaluate curcumin-loaded lipid nanoemulsions (C-NEs) for targeted nose-to-brain delivery. Nanoemulsions prepared with Capmul MCM, Tween 80, and Transcutol P presented droplet sizes of 85.3 ± 2.6 nm and zeta potential of -19.5 ± 0.9 mV. Ex vivo permeation through excised sheep nasal mucosa using Franz diffusion cells demonstrated steady-state flux (Jss) of 48.7 microg/cm2/h, representing a 3.8-fold improvement over free drug. Histopathological evaluation confirmed absence of epithelial damage or nasal ciliotoxicity. Further studies are needed to evaluate aerosolization performance and spray pattern consistency in human nasal cast replicas.",
                "publication_type": "Original Research Article",
                "keywords": "Nose-to-brain, Nanoemulsion, Nasal mucosa, Ciliotoxicity, Olfactory route",
                "database_source": "Europe PMC",
                "url": "https://doi.org/10.1016/j.ejps.2023.106512",
                "is_open_access": True
            },
            {
                "title": "Chitosan-coated solid lipid nanoparticles for enhanced ocular and neural permeation of polyphenolic compounds",
                "authors": "Venkatesan, P., Rao, S.P., Thomas, S.",
                "year": 2023,
                "journal": "Colloids and Surfaces B: Biointerfaces",
                "doi": "10.1016/j.colsurfb.2023.113240",
                "pmid": "37542910",
                "pmcid": "",
                "abstract": "Mucoadhesive surface coating can significantly prolong residential transit time and promote paracellular epithelial permeation. In this study, we engineered low molecular weight chitosan-coated solid lipid nanoparticles (CS-SLNs) for neuroprotective drug delivery. Coating reversed the zeta potential from -24.2 mV to +32.6 ± 1.4 mV, conferring strong electrostatic adherence to negative mucin layers. Entrapment efficiency reached 86.8 ± 1.8%. Dialysis release tests showed sustained zero-order delivery for up to 48 hours without drug precipitation. A primary limitation was the lack of in vivo chronic toxicity assessment upon repeated administration.",
                "publication_type": "Original Research Article",
                "keywords": "Chitosan, Mucoadhesion, Solid lipid nanoparticles, Polarity reversal, Sustained release",
                "database_source": "Semantic Scholar, PubMed",
                "url": "https://doi.org/10.1016/j.colsurfb.2023.113240",
                "is_open_access": False
            }
        ]

        saved_papers = []
        for p in sample_papers:
            saved = self.repo.add_paper(project.id, p)
            saved_papers.append(saved)

        analysis_service = AnalysisService(self.repo)
        analysis_service.analyze_project_papers(project.id, mode="rule_based")

        gap_service = GapService(self.repo)
        gap_service.generate_project_gaps(project.id, mode="rule_based")

        return project
