from typing import Dict, Any, Optional
from app.database.repository import Repository
from app.analysis.gap_analyzer import GapAnalyzer

class GapService:
    def __init__(self, repo: Repository, api_key: Optional[str] = None, model: Optional[str] = None):
        self.repo = repo
        self.analyzer = GapAnalyzer(api_key=api_key, model=model)

    def generate_project_gaps(self, project_id: int, mode: str = "auto") -> Dict[str, Any]:
        project = self.repo.get_project_by_id(project_id)
        if not project:
            raise ValueError(f"Project with ID {project_id} not found.")

        papers = self.repo.get_papers(project_id, include_excluded=False)
        analyzed_papers = []

        for p in papers:
            if p.analysis and p.analysis.status == "completed":
                analyzed_papers.append({
                    "id": p.id,
                    "title": p.title,
                    "doi": p.doi,
                    "year": p.year,
                    "journal": p.journal,
                    "abstract": p.abstract,
                    "analysis": p.analysis.to_dict()
                })

        project_ctx = {
            "name": project.name,
            "therapeutic_area": project.therapeutic_area,
            "target_drug": project.target_drug
        }

        synthesis_result = self.analyzer.analyze_corpus(analyzed_papers, project_ctx, mode=mode)

        gap_items = synthesis_result.get("gap_matrix", [])
        summary = synthesis_result.get("synthesis_summary", "")
        self.repo.save_gap_matrix(project_id, gap_items, summary)

        return synthesis_result

    def get_latest_gaps(self, project_id: int) -> Optional[Dict[str, Any]]:
        record = self.repo.get_latest_gap_matrix(project_id)
        if not record:
            return None
        return {
            "gap_matrix": record.matrix_items,
            "synthesis_summary": record.synthesis_summary,
            "generated_at": record.generated_at.isoformat() if record.generated_at else None
        }
