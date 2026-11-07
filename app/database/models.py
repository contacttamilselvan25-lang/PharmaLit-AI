import json
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Float
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, default="")
    therapeutic_area = Column(String(255), default="")
    target_drug = Column(String(255), default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    papers = relationship("Paper", back_populates="project", cascade="all, delete-orphan")
    searches = relationship("SearchHistory", back_populates="project", cascade="all, delete-orphan")
    gap_matrices = relationship("GapMatrix", back_populates="project", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "therapeutic_area": self.therapeutic_area,
            "target_drug": self.target_drug,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

class SearchHistory(Base):
    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    query_params_json = Column(Text, default="{}")
    databases_searched = Column(String(255), default="")
    raw_results_count = Column(Integer, default=0)
    deduped_results_count = Column(Integer, default=0)
    executed_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="searches")

    @property
    def query_params(self):
        try:
            return json.loads(self.query_params_json or "{}")
        except Exception:
            return {}

class Paper(Base):
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    title = Column(Text, nullable=False)
    authors = Column(Text, default="")
    year = Column(Integer, nullable=True)
    journal = Column(String(255), default="")
    doi = Column(String(255), default="", index=True)
    pmid = Column(String(64), default="", index=True)
    pmcid = Column(String(64), default="", index=True)
    abstract = Column(Text, default="")
    publication_type = Column(String(128), default="Journal Article")
    keywords = Column(Text, default="")
    database_source = Column(String(128), default="PubMed")
    url = Column(Text, default="")
    is_open_access = Column(Boolean, default=False)
    is_excluded = Column(Boolean, default=False)
    exclusion_reason = Column(String(255), default="")
    has_full_text = Column(Boolean, default=False)
    full_text_path = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="papers")
    analysis = relationship("PaperAnalysis", back_populates="paper", uselist=False, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "title": self.title,
            "authors": self.authors,
            "year": self.year,
            "journal": self.journal,
            "doi": self.doi,
            "pmid": self.pmid,
            "pmcid": self.pmcid,
            "abstract": self.abstract,
            "publication_type": self.publication_type,
            "keywords": self.keywords,
            "database_source": self.database_source,
            "url": self.url,
            "is_open_access": self.is_open_access,
            "is_excluded": self.is_excluded,
            "exclusion_reason": self.exclusion_reason,
            "has_full_text": self.has_full_text,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

class PaperAnalysis(Base):
    __tablename__ = "paper_analyses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=False, unique=True)
    status = Column(String(32), default="completed")
    analysis_mode = Column(String(32), default="auto")
    model_used = Column(String(64), default="")
    
    research_objective = Column(Text, default="")
    methodology_json = Column(Text, default="{}")
    results_json = Column(Text, default="{}")
    limitations_json = Column(Text, default="{}")
    gaps_json = Column(Text, default="{}")
    future_directions_json = Column(Text, default="{}")
    scientific_importance = Column(Text, default="")
    evidence_confidence = Column(String(64), default="Directly supported by abstract")
    evidence_snippets_json = Column(Text, default="[]")
    
    analyzed_at = Column(DateTime, default=datetime.utcnow)

    paper = relationship("Paper", back_populates="analysis")

    @property
    def methodology(self):
        try:
            return json.loads(self.methodology_json or "{}")
        except Exception:
            return {}

    @property
    def results(self):
        try:
            return json.loads(self.results_json or "{}")
        except Exception:
            return {}

    @property
    def limitations(self):
        try:
            return json.loads(self.limitations_json or "{}")
        except Exception:
            return {}

    @property
    def gaps(self):
        try:
            return json.loads(self.gaps_json or "{}")
        except Exception:
            return {}

    @property
    def future_directions(self):
        try:
            return json.loads(self.future_directions_json or "{}")
        except Exception:
            return {}

    @property
    def evidence_snippets(self):
        try:
            return json.loads(self.evidence_snippets_json or "[]")
        except Exception:
            return []

    def to_dict(self):
        return {
            "id": self.id,
            "paper_id": self.paper_id,
            "status": self.status,
            "analysis_mode": self.analysis_mode,
            "model_used": self.model_used,
            "research_objective": self.research_objective,
            "methodology": self.methodology,
            "results": self.results,
            "limitations": self.limitations,
            "gaps": self.gaps,
            "future_directions": self.future_directions,
            "scientific_importance": self.scientific_importance,
            "evidence_confidence": self.evidence_confidence,
            "evidence_snippets": self.evidence_snippets,
            "analyzed_at": self.analyzed_at.isoformat() if self.analyzed_at else None,
        }

class GapMatrix(Base):
    __tablename__ = "gap_matrices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    matrix_json = Column(Text, default="[]")
    synthesis_summary = Column(Text, default="")
    generated_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="gap_matrices")

    @property
    def matrix_items(self):
        try:
            return json.loads(self.matrix_json or "[]")
        except Exception:
            return []

class AppSetting(Base):
    __tablename__ = "app_settings"

    key = Column(String(128), primary_key=True)
    value = Column(Text, default="")
