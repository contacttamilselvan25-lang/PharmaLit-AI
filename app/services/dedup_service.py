import re
from difflib import SequenceMatcher
from typing import List, Dict, Any, Tuple

class DeduplicationService:
    @staticmethod
    def normalize_doi(doi: str) -> str:
        if not doi:
            return ""
        clean = doi.strip().lower()
        clean = re.sub(r"^https?://(dx\.)?doi\.org/", "", clean)
        return clean.strip("/")

    @staticmethod
    def normalize_pmid(pmid: Any) -> str:
        if not pmid:
            return ""
        return str(pmid).strip()

    @staticmethod
    def normalize_title(title: str) -> str:
        if not title:
            return ""
        clean = title.lower()
        clean = re.sub(r"[^\w\s]", " ", clean)
        return " ".join(clean.split())

    @classmethod
    def calculate_title_similarity(cls, title1: str, title2: str) -> float:
        norm1 = cls.normalize_title(title1)
        norm2 = cls.normalize_title(title2)
        if not norm1 or not norm2:
            return 0.0
        if norm1 == norm2:
            return 1.0
        return SequenceMatcher(None, norm1, norm2).ratio()

    @classmethod
    def deduplicate(cls, papers: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        unique_papers: List[Dict[str, Any]] = []
        duplicates_log: List[Dict[str, Any]] = []

        doi_map: Dict[str, int] = {}
        pmid_map: Dict[str, int] = {}
        pmcid_map: Dict[str, int] = {}

        for p in papers:
            doi = cls.normalize_doi(p.get("doi", ""))
            pmid = cls.normalize_pmid(p.get("pmid", ""))
            pmcid = cls.normalize_pmid(p.get("pmcid", ""))
            title = p.get("title", "")
            year = p.get("year")

            match_idx = None
            reason = ""

            if doi and doi in doi_map:
                match_idx = doi_map[doi]
                reason = f"Duplicate DOI: {doi}"
            elif pmid and pmid in pmid_map:
                match_idx = pmid_map[pmid]
                reason = f"Duplicate PMID: {pmid}"
            elif pmcid and pmcid in pmcid_map:
                match_idx = pmcid_map[pmcid]
                reason = f"Duplicate PMCID: {pmcid}"
            else:
                for idx, existing in enumerate(unique_papers):
                    ex_title = existing.get("title", "")
                    sim = cls.calculate_title_similarity(title, ex_title)
                    if sim >= 0.90:
                        ex_year = existing.get("year")
                        if year and ex_year and abs(int(year) - int(ex_year)) <= 1:
                            match_idx = idx
                            reason = f"Title similarity match ({int(sim*100)}%): '{title[:50]}...'"
                            break
                        elif not year or not ex_year:
                            match_idx = idx
                            reason = f"Title similarity match ({int(sim*100)}%): '{title[:50]}...'"
                            break

            if match_idx is not None:
                existing = unique_papers[match_idx]
                srcs = set(existing.get("database_source", "").split(", "))
                new_src = p.get("database_source", "")
                if new_src:
                    srcs.add(new_src)
                existing["database_source"] = ", ".join(sorted(list(srcs)))

                if not existing.get("abstract") and p.get("abstract"):
                    existing["abstract"] = p["abstract"]
                if not existing.get("doi") and p.get("doi"):
                    existing["doi"] = p["doi"]
                    if doi:
                        doi_map[doi] = match_idx
                if not existing.get("pmid") and p.get("pmid"):
                    existing["pmid"] = p["pmid"]
                    if pmid:
                        pmid_map[pmid] = match_idx
                if not existing.get("pmcid") and p.get("pmcid"):
                    existing["pmcid"] = p["pmcid"]
                    if pmcid:
                        pmcid_map[pmcid] = match_idx
                if not existing.get("year") and p.get("year"):
                    existing["year"] = p["year"]
                if not existing.get("authors") and p.get("authors"):
                    existing["authors"] = p["authors"]
                if p.get("is_open_access"):
                    existing["is_open_access"] = True

                duplicates_log.append({
                    "title": title,
                    "doi": doi,
                    "source": p.get("database_source", ""),
                    "reason": reason
                })
            else:
                idx = len(unique_papers)
                unique_papers.append(p)
                if doi:
                    doi_map[doi] = idx
                if pmid:
                    pmid_map[pmid] = idx
                if pmcid:
                    pmcid_map[pmcid] = idx

        audit = {
            "original_count": len(papers),
            "duplicate_count": len(duplicates_log),
            "unique_count": len(unique_papers),
            "duplicates_log": duplicates_log
        }

        return unique_papers, audit
