import os
import re
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from config.settings import UPLOADS_DIR
from app.services.dedup_service import DeduplicationService

class PDFService:
    DOI_REGEX = re.compile(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+", re.IGNORECASE)

    SECTION_HEADERS = {
        "abstract": re.compile(r"^(\d+\.?\s*)?(abstract|summary)\b", re.IGNORECASE),
        "introduction": re.compile(r"^(\d+\.?\s*)?(introduction|background)\b", re.IGNORECASE),
        "methods": re.compile(r"^(\d+\.?\s*)?(materials?\s+and\s+methods?|experimental(\s+section)?|methodology|methods)\b", re.IGNORECASE),
        "results": re.compile(r"^(\d+\.?\s*)?(results?(\s+and\s+discussion)?)\b", re.IGNORECASE),
        "discussion": re.compile(r"^(\d+\.?\s*)?(discussion)\b", re.IGNORECASE),
        "conclusion": re.compile(r"^(\d+\.?\s*)?(conclusions?|concluding\s+remarks)\b", re.IGNORECASE),
        "references": re.compile(r"^(\d+\.?\s*)?(references|bibliography|literature\s+cited)\b", re.IGNORECASE)
    }

    @classmethod
    def extract_text_from_pdf(cls, file_path: str) -> Dict[str, Any]:
        if not os.path.exists(file_path):
            return {"success": False, "error": f"File does not exist: {file_path}"}

        full_text = ""
        pages_text = []

        try:
            import fitz
            doc = fitz.open(file_path)
            for page_idx in range(len(doc)):
                page = doc[page_idx]
                t = page.get_text("text")
                pages_text.append(t)
                full_text += f"\n--- Page {page_idx + 1} ---\n" + t
            doc.close()
        except Exception as e_fitz:
            try:
                import pypdf
                reader = pypdf.PdfReader(file_path)
                for idx, page in enumerate(reader.pages):
                    t = page.extract_text() or ""
                    pages_text.append(t)
                    full_text += f"\n--- Page {idx + 1} ---\n" + t
            except Exception as e_pypdf:
                return {
                    "success": False,
                    "error": f"Text extraction failed: {e_fitz} / {e_pypdf}"
                }

        if not full_text.strip():
            return {
                "success": False,
                "error": "Extracted text is empty. The PDF may be a scanned image without an OCR text layer."
            }

        return {
            "success": True,
            "full_text": full_text,
            "pages_text": pages_text,
            "page_count": len(pages_text)
        }

    @classmethod
    def identify_sections(cls, full_text: str) -> Dict[str, str]:
        lines = full_text.splitlines()
        sections: Dict[str, List[str]] = {
            "abstract": [],
            "introduction": [],
            "methods": [],
            "results": [],
            "discussion": [],
            "conclusion": [],
            "references": [],
            "other": []
        }

        current_sec = "other"

        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue

            if len(line_str) < 60:
                matched_sec = None
                for sec_name, pattern in cls.SECTION_HEADERS.items():
                    if pattern.match(line_str):
                        matched_sec = sec_name
                        break
                if matched_sec:
                    current_sec = matched_sec
                    continue

            sections[current_sec].append(line_str)

        return {k: "\n".join(v).strip() for k, v in sections.items()}

    @classmethod
    def extract_metadata_from_pdf(cls, full_text: str, first_page_text: str) -> Dict[str, Any]:
        doi_match = cls.DOI_REGEX.search(full_text)
        doi = doi_match.group(0).strip(".,;()") if doi_match else ""

        lines = [l.strip() for l in first_page_text.splitlines() if len(l.strip()) > 10]
        title = ""
        for l in lines[:10]:
            if not any(k in l.lower() for k in ["journal", "vol.", "elsevier", "springer", "wiley", "http", "doi:", "issn"]):
                title = l
                break

        return {
            "doi": doi,
            "suggested_title": title
        }

    @classmethod
    def process_pdf(cls, file_path: str) -> Dict[str, Any]:
        extraction = cls.extract_text_from_pdf(file_path)
        if not extraction.get("success"):
            return extraction

        full_text = extraction["full_text"]
        pages = extraction["pages_text"]
        first_page = pages[0] if pages else ""

        sections = cls.identify_sections(full_text)
        meta = cls.extract_metadata_from_pdf(full_text, first_page)

        return {
            "success": True,
            "page_count": extraction["page_count"],
            "doi": meta["doi"],
            "suggested_title": meta["suggested_title"],
            "sections": sections,
            "full_text": full_text
        }

    @classmethod
    def match_pdf_to_papers(cls, pdf_meta: Dict[str, Any], papers: List[Any]) -> Optional[Any]:
        pdf_doi = DeduplicationService.normalize_doi(pdf_meta.get("doi", ""))
        pdf_title = pdf_meta.get("suggested_title", "")

        if pdf_doi:
            for p in papers:
                if DeduplicationService.normalize_doi(p.doi) == pdf_doi:
                    return p

        if pdf_title and len(pdf_title) > 15:
            for p in papers:
                sim = DeduplicationService.calculate_title_similarity(pdf_title, p.title)
                if sim >= 0.85:
                    return p

        return None
