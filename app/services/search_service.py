from typing import List, Dict, Any, Optional, Tuple
from app.integrations.pubmed import PubMedClient
from app.integrations.europepmc import EuropePMCClient
from app.integrations.semanticscholar import SemanticScholarClient
from app.services.dedup_service import DeduplicationService
from app.database.repository import Repository

class SearchService:
    def __init__(self, repo: Repository):
        self.repo = repo
        self.pubmed_client = PubMedClient()
        self.europepmc_client = EuropePMCClient()
        self.semanticscholar_client = SemanticScholarClient()

    @staticmethod
    def build_query_string(
        topic: str,
        main_keywords: str = "",
        alt_keywords: str = "",
        disease_area: str = "",
        drug_api: str = "",
        delivery_system: str = "",
        methodology: str = ""
    ) -> str:
        clauses = []
        if topic.strip():
            clauses.append(f"({topic.strip()})")

        if main_keywords.strip():
            m_terms = [f'"{k.strip()}"' if " " in k.strip() else k.strip() for k in main_keywords.split(",") if k.strip()]
            if m_terms:
                clauses.append(f"({' AND '.join(m_terms)})")

        if alt_keywords.strip():
            a_terms = [f'"{k.strip()}"' if " " in k.strip() else k.strip() for k in alt_keywords.split(",") if k.strip()]
            if a_terms:
                clauses.append(f"({' OR '.join(a_terms)})")

        if disease_area.strip():
            clauses.append(f'("{disease_area.strip()}" OR {disease_area.strip()})')

        if drug_api.strip():
            clauses.append(f'("{drug_api.strip()}" OR {drug_api.strip()})')

        if delivery_system.strip():
            clauses.append(f'("{delivery_system.strip()}" OR {delivery_system.strip()})')

        if methodology.strip():
            clauses.append(f'("{methodology.strip()}")')

        if not clauses:
            return "pharmacology drug delivery"
        return " AND ".join(clauses)

    def execute_search(
        self,
        project_id: int,
        query_params: Dict[str, Any],
        databases: List[str],
        max_papers: int = 50,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        progress_callback: Optional[callable] = None
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        query_string = self.build_query_string(
            topic=query_params.get("topic", ""),
            main_keywords=query_params.get("main_keywords", ""),
            alt_keywords=query_params.get("alt_keywords", ""),
            disease_area=query_params.get("disease_area", ""),
            drug_api=query_params.get("drug_api", ""),
            delivery_system=query_params.get("delivery_system", ""),
            methodology=query_params.get("methodology", "")
        )

        all_retrieved: List[Dict[str, Any]] = []
        status_log: List[str] = []
        per_db_target = max(15, int(max_papers * 1.2 / max(1, len(databases))))

        if "PubMed" in databases:
            if progress_callback:
                progress_callback(0.15, "Searching PubMed E-utilities...")
            try:
                pm_papers = self.pubmed_client.search_and_retrieve(
                    query=query_string,
                    max_results=per_db_target,
                    start_year=start_year,
                    end_year=end_year
                )
                all_retrieved.extend(pm_papers)
                status_log.append(f"PubMed: Retrieved {len(pm_papers)} records.")
            except Exception as e:
                status_log.append(f"PubMed Error: {e}")

        if "Europe PMC" in databases:
            if progress_callback:
                progress_callback(0.45, "Searching Europe PMC REST API...")
            try:
                epmc_papers = self.europepmc_client.search_and_retrieve(
                    query=query_string,
                    max_results=per_db_target,
                    start_year=start_year,
                    end_year=end_year
                )
                all_retrieved.extend(epmc_papers)
                status_log.append(f"Europe PMC: Retrieved {len(epmc_papers)} records.")
            except Exception as e:
                status_log.append(f"Europe PMC Error: {e}")

        if "Semantic Scholar" in databases:
            if progress_callback:
                progress_callback(0.70, "Searching Semantic Scholar Academic Graph...")
            try:
                s2_papers = self.semanticscholar_client.search_and_retrieve(
                    query=query_string,
                    max_results=per_db_target,
                    start_year=start_year,
                    end_year=end_year
                )
                all_retrieved.extend(s2_papers)
                status_log.append(f"Semantic Scholar: Retrieved {len(s2_papers)} records.")
            except Exception as e:
                status_log.append(f"Semantic Scholar Error: {e}")

        if progress_callback:
            progress_callback(0.85, "Running intelligent deduplication cascade...")

        unique_papers, audit = DeduplicationService.deduplicate(all_retrieved)
        final_papers = unique_papers[:max_papers]

        if progress_callback:
            progress_callback(0.95, f"Saving {len(final_papers)} unique papers to project...")

        saved_entities = []
        for p in final_papers:
            existing = None
            if p.get("doi"):
                existing = self.repo.find_paper_by_doi(project_id, p["doi"])
            if not existing:
                saved = self.repo.add_paper(project_id, p)
                saved_entities.append(saved)

        self.repo.log_search(
            project_id=project_id,
            query_params=query_params,
            databases=databases,
            raw_count=len(all_retrieved),
            deduped_count=len(final_papers)
        )

        audit["saved_new_count"] = len(saved_entities)
        audit["status_log"] = status_log
        audit["query_string"] = query_string

        if progress_callback:
            progress_callback(1.0, f"Search completed! {len(final_papers)} papers ready.")

        return final_papers, audit
