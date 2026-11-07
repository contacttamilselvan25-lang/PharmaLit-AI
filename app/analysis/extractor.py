import json
from typing import Dict, Any, Optional
from config.settings import settings
from app.integrations.gemini_client import GeminiClient
from app.analysis.prompts import ANALYSIS_SYSTEM_PROMPT
from app.analysis.rules_extractor import RulesBasedExtractor

class PaperAnalysisExtractor:
    """Orchestrates paper analysis using either Gemini AI or Scientific Rule-Based NLP."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL
        self.gemini_client = GeminiClient(api_key=self.api_key, model=self.model)

    def analyze_paper(
        self,
        paper_dict: Dict[str, Any],
        mode: str = "auto",
        full_text: Optional[str] = None
    ) -> Dict[str, Any]:
        has_full_text = bool(full_text and len(full_text.strip()) > 300)
        content_type = "FULL-TEXT ARTICLE" if has_full_text else "ABSTRACT ONLY"

        use_gemini = False
        if mode == "gemini":
            use_gemini = True
        elif mode == "auto":
            use_gemini = self.gemini_client.is_configured()

        if use_gemini:
            try:
                doc_text = f"""
TITLE: {paper_dict.get('title', '')}
AUTHORS: {paper_dict.get('authors', '')}
JOURNAL: {paper_dict.get('journal', '')} ({paper_dict.get('year', '')})
DOI: {paper_dict.get('doi', '')}
CONTENT TYPE: {content_type}

ABSTRACT:
{paper_dict.get('abstract', '')}
"""
                if has_full_text:
                    doc_text += f"\n\nFULL TEXT EXCERPTS:\n{full_text[:25000]}"

                res = self.gemini_client.analyze_text(
                    system_prompt=ANALYSIS_SYSTEM_PROMPT,
                    user_content=doc_text,
                    temperature=0.2
                )

                confidence = "Supported by full-text evidence" if has_full_text else "Directly supported by abstract"
                res["evidence_confidence"] = confidence
                res["status"] = "completed"
                res["analysis_mode"] = "gemini"
                res["model_used"] = self.model
                return res

            except Exception as e:
                print(f"[PaperAnalysisExtractor] Gemini analysis failed ({e}). Falling back to Rule-Based Extractor.")
                fallback_res = RulesBasedExtractor.analyze(paper_dict, has_full_text=has_full_text)
                fallback_res["analysis_mode"] = "rule_based_fallback"
                fallback_res["model_used"] = f"Rule-Based (Gemini fallback: {str(e)[:40]}...)"
                return fallback_res

        return RulesBasedExtractor.analyze(paper_dict, has_full_text=has_full_text)
