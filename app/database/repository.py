import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct, desc
from app.database.models import Project, Paper, PaperAnalysis, SearchHistory, GapMatrix, AppSetting

class Repository:
    def __init__(self, db: Session):
        self.db = db

    def create_project(self, name: str, description: str = "", therapeutic_area: str = "", target_drug: str = "") -> Project:
        project = Project(
            name=name.strip(),
            description=description.strip(),
            therapeutic_area=therapeutic_area.strip(),
            target_drug=target_drug.strip()
        )
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def get_projects(self) -> List[Project]:
        return self.db.query(Project).order_by(desc(Project.updated_at)).all()

    def get_project_by_id(self, project_id: int) -> Optional[Project]:
        return self.db.query(Project).filter(Project.id == project_id).first()

    def delete_project(self, project_id: int) -> bool:
        project = self.get_project_by_id(project_id)
        if project:
            self.db.delete(project)
            self.db.commit()
            return True
        return False

    def add_paper(self, project_id: int, paper_dict: Dict[str, Any]) -> Paper:
        paper = Paper(
            project_id=project_id,
            title=paper_dict.get("title", "").strip(),
            authors=paper_dict.get("authors", "").strip(),
            year=paper_dict.get("year"),
            journal=paper_dict.get("journal", "").strip(),
            doi=paper_dict.get("doi", "").strip(),
            pmid=str(paper_dict.get("pmid", "")).strip(),
            pmcid=str(paper_dict.get("pmcid", "")).strip(),
            abstract=paper_dict.get("abstract", "").strip(),
            publication_type=paper_dict.get("publication_type", "Journal Article").strip(),
            keywords=paper_dict.get("keywords", "").strip(),
            database_source=paper_dict.get("database_source", "PubMed").strip(),
            url=paper_dict.get("url", "").strip(),
            is_open_access=bool(paper_dict.get("is_open_access", False)),
            is_excluded=bool(paper_dict.get("is_excluded", False)),
            exclusion_reason=paper_dict.get("exclusion_reason", "").strip(),
            has_full_text=bool(paper_dict.get("has_full_text", False)),
            full_text_path=paper_dict.get("full_text_path", "").strip()
        )
        self.db.add(paper)
        self.db.commit()
        self.db.refresh(paper)
        return paper

    def get_papers(self, project_id: int, include_excluded: bool = True) -> List[Paper]:
        q = self.db.query(Paper).filter(Paper.project_id == project_id)
        if not include_excluded:
            q = q.filter(Paper.is_excluded == False)
        return q.order_by(desc(Paper.year), Paper.title).all()

    def get_paper_by_id(self, paper_id: int) -> Optional[Paper]:
        return self.db.query(Paper).filter(Paper.id == paper_id).first()

    def update_paper_exclusion(self, paper_id: int, is_excluded: bool, reason: str = "") -> Optional[Paper]:
        paper = self.get_paper_by_id(paper_id)
        if paper:
            paper.is_excluded = is_excluded
            paper.exclusion_reason = reason if is_excluded else ""
            self.db.commit()
            self.db.refresh(paper)
        return paper

    def update_paper_full_text(self, paper_id: int, file_path: str) -> Optional[Paper]:
        paper = self.get_paper_by_id(paper_id)
        if paper:
            paper.has_full_text = True
            paper.full_text_path = file_path
            self.db.commit()
            self.db.refresh(paper)
        return paper

    def find_paper_by_doi(self, project_id: int, doi: str) -> Optional[Paper]:
        if not doi:
            return None
        return self.db.query(Paper).filter(
            Paper.project_id == project_id,
            func.lower(Paper.doi) == doi.lower().strip()
        ).first()

    def log_search(self, project_id: int, query_params: Dict[str, Any], databases: List[str], raw_count: int, deduped_count: int) -> SearchHistory:
        rec = SearchHistory(
            project_id=project_id,
            query_params_json=json.dumps(query_params),
            databases_searched=", ".join(databases),
            raw_results_count=raw_count,
            deduped_results_count=deduped_count,
            executed_at=datetime.utcnow()
        )
        self.db.add(rec)
        self.db.commit()
        self.db.refresh(rec)
        return rec

    def get_search_history(self, project_id: int) -> List[SearchHistory]:
        return self.db.query(SearchHistory).filter(SearchHistory.project_id == project_id).order_by(desc(SearchHistory.executed_at)).all()

    def save_analysis(self, paper_id: int, analysis_data: Dict[str, Any]) -> PaperAnalysis:
        analysis = self.db.query(PaperAnalysis).filter(PaperAnalysis.paper_id == paper_id).first()
        if not analysis:
            analysis = PaperAnalysis(paper_id=paper_id)
            self.db.add(analysis)

        analysis.status = analysis_data.get("status", "completed")
        analysis.analysis_mode = analysis_data.get("analysis_mode", "auto")
        analysis.model_used = analysis_data.get("model_used", "")
        analysis.research_objective = analysis_data.get("research_objective", "")
        analysis.methodology_json = json.dumps(analysis_data.get("methodology", {}))
        analysis.results_json = json.dumps(analysis_data.get("results", {}))
        analysis.limitations_json = json.dumps(analysis_data.get("limitations", {}))
        analysis.gaps_json = json.dumps(analysis_data.get("gaps", {}))
        analysis.future_directions_json = json.dumps(analysis_data.get("future_directions", {}))
        analysis.scientific_importance = analysis_data.get("scientific_importance", "")
        analysis.evidence_confidence = analysis_data.get("evidence_confidence", "Directly supported by abstract")
        analysis.evidence_snippets_json = json.dumps(analysis_data.get("evidence_snippets", []))
        analysis.analyzed_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(analysis)
        return analysis

    def get_analysis_by_paper_id(self, paper_id: int) -> Optional[PaperAnalysis]:
        return self.db.query(PaperAnalysis).filter(PaperAnalysis.paper_id == paper_id).first()

    def save_gap_matrix(self, project_id: int, matrix_items: List[Dict[str, Any]], summary: str = "") -> GapMatrix:
        gap_mat = GapMatrix(
            project_id=project_id,
            matrix_json=json.dumps(matrix_items),
            synthesis_summary=summary,
            generated_at=datetime.utcnow()
        )
        self.db.add(gap_mat)
        self.db.commit()
        self.db.refresh(gap_mat)
        return gap_mat

    def get_latest_gap_matrix(self, project_id: int) -> Optional[GapMatrix]:
        return self.db.query(GapMatrix).filter(GapMatrix.project_id == project_id).order_by(desc(GapMatrix.generated_at)).first()

    def get_setting(self, key: str, default: str = "") -> str:
        row = self.db.query(AppSetting).filter(AppSetting.key == key).first()
        return row.value if row else default

    def set_setting(self, key: str, value: str):
        row = self.db.query(AppSetting).filter(AppSetting.key == key).first()
        if row:
            row.value = value
        else:
            row = AppSetting(key=key, value=value)
            self.db.add(row)
        self.db.commit()

    def get_dashboard_metrics(self, project_id: Optional[int] = None) -> Dict[str, Any]:
        p_filter = [Paper.project_id == project_id] if project_id else []
        total_projects = self.db.query(func.count(Project.id)).scalar() or 0

        paper_query = self.db.query(Paper)
        if project_id:
            paper_query = paper_query.filter(*p_filter)

        total_papers = paper_query.count()
        unique_papers = paper_query.filter(Paper.is_excluded == False).count()
        with_doi = paper_query.filter(Paper.doi != "", Paper.doi != None).count()
        with_abstract = paper_query.filter(Paper.abstract != "", Paper.abstract != None).count()
        with_full_text = paper_query.filter(Paper.has_full_text == True).count()

        analysis_q = self.db.query(PaperAnalysis).join(Paper)
        if project_id:
            analysis_q = analysis_q.filter(Paper.project_id == project_id)
        completed_analyses = analysis_q.filter(PaperAnalysis.status == "completed").count()
        awaiting_analysis = max(0, unique_papers - completed_analyses)

        gaps_count = 0
        latest_matrix = None
        if project_id:
            latest_matrix = self.get_latest_gap_matrix(project_id)
        else:
            latest_matrix = self.db.query(GapMatrix).order_by(desc(GapMatrix.generated_at)).first()
        if latest_matrix:
            gaps_count = len(latest_matrix.matrix_items)

        year_rows = (
            self.db.query(Paper.year, func.count(Paper.id))
            .filter(*p_filter, Paper.year != None, Paper.year > 1950)
            .group_by(Paper.year)
            .order_by(Paper.year)
            .all()
        )
        years_dist = {str(yr): cnt for yr, cnt in year_rows}

        journal_rows = (
            self.db.query(Paper.journal, func.count(Paper.id))
            .filter(*p_filter, Paper.journal != "", Paper.journal != None)
            .group_by(Paper.journal)
            .order_by(desc(func.count(Paper.id)))
            .limit(10)
            .all()
        )
        journals_dist = {j: cnt for j, cnt in journal_rows}

        db_rows = (
            self.db.query(Paper.database_source, func.count(Paper.id))
            .filter(*p_filter)
            .group_by(Paper.database_source)
            .all()
        )
        sources_dist = {src: cnt for src, cnt in db_rows}

        type_rows = (
            self.db.query(Paper.publication_type, func.count(Paper.id))
            .filter(*p_filter)
            .group_by(Paper.publication_type)
            .all()
        )
        types_dist = {t: cnt for t, cnt in type_rows}

        return {
            "total_projects": total_projects,
            "total_papers": total_papers,
            "unique_papers": unique_papers,
            "with_doi": with_doi,
            "with_abstract": with_abstract,
            "with_full_text": with_full_text,
            "completed_analyses": completed_analyses,
            "awaiting_analysis": awaiting_analysis,
            "gaps_count": gaps_count,
            "years_dist": years_dist,
            "journals_dist": journals_dist,
            "sources_dist": sources_dist,
            "types_dist": types_dist
        }
