import os
from typing import List, Dict, Any, Optional
from app.database.repository import Repository
from app.analysis.extractor import PaperAnalysisExtractor
from app.services.pdf_service import PDFService

class AnalysisService:
    def __init__(self, repo: Repository, api_key: Optional[str] = None, model: Optional[str] = None):
        self.repo = repo
        self.extractor = PaperAnalysisExtractor(api_key=api_key, model=model)

    def analyze_single_paper(self, paper_id: int, mode: str = "auto") -> Dict[str, Any]:
        paper = self.repo.get_paper_by_id(paper_id)
        if not paper:
            raise ValueError(f"Paper with ID {paper_id} not found.")

        full_text = None
        if paper.has_full_text and paper.full_text_path and os.path.exists(paper.full_text_path):
            pdf_data = PDFService.extract_text_from_pdf(paper.full_text_path)
            if pdf_data.get("success"):
                full_text = pdf_data.get("full_text")

        paper_dict = paper.to_dict()
        analysis_data = self.extractor.analyze_paper(paper_dict, mode=mode, full_text=full_text)
        
        saved = self.repo.save_analysis(paper_id, analysis_data)
        return saved.to_dict()

    def analyze_project_papers(
        self,
        project_id: int,
        paper_ids: Optional[List[int]] = None,
        mode: str = "auto",
        progress_callback: Optional[callable] = None
    ) -> List[Dict[str, Any]]:
        all_papers = self.repo.get_papers(project_id, include_excluded=False)
        if paper_ids:
            target_papers = [p for p in all_papers if p.id in paper_ids]
        else:
            target_papers = all_papers

        results = []
        total = len(target_papers)

        for idx, paper in enumerate(target_papers):
            if progress_callback:
                progress_callback(
                    (idx) / max(1, total),
                    f"Analyzing paper {idx + 1} of {total}: {paper.title[:50]}..."
                )

            try:
                res = self.analyze_single_paper(paper.id, mode=mode)
                results.append(res)
            except Exception as e:
                print(f"[AnalysisService] Error analyzing paper {paper.id}: {e}")

        if progress_callback:
            progress_callback(1.0, f"Analysis completed! {len(results)} papers processed.")

        return results
