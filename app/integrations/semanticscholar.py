from typing import List, Dict, Any, Optional
import requests
from config.settings import settings

class SemanticScholarClient:
    """Client for Semantic Scholar Academic Graph API."""

    BASE_URL = "https://api.semanticscholar.org/graph/v1/paper/search"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.timeout = settings.REQUEST_TIMEOUT
        self.headers = {
            "User-Agent": settings.USER_AGENT,
            "Accept": "application/json"
        }
        if self.api_key:
            self.headers["x-api-key"] = self.api_key

    def search_and_retrieve(
        self,
        query: str,
        max_results: int = 50,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        params = {
            "query": query.strip(),
            "limit": min(max_results, 100),
            "fields": "title,authors,year,journal,externalIds,abstract,isOpenAccess,publicationTypes,url"
        }
        if start_year and end_year:
            params["year"] = f"{start_year}-{end_year}"
        elif start_year:
            params["year"] = f"{start_year}-"
        elif end_year:
            params["year"] = f"-{end_year}"

        papers = []
        try:
            resp = requests.get(self.BASE_URL, params=params, headers=self.headers, timeout=self.timeout)
            if resp.status_code == 429:
                print("[SemanticScholarClient] Rate limit encountered on Semantic Scholar, skipping gracefully.")
                return []
            resp.raise_for_status()
            data = resp.json()
            items = data.get("data", [])

            for item in items:
                title = (item.get("title") or "").strip()
                if not title:
                    continue

                year = item.get("year")
                abstract = (item.get("abstract") or "").strip()
                
                author_names = []
                for a in item.get("authors", []):
                    name = a.get("name")
                    if name:
                        author_names.append(name.strip())
                authors_str = ", ".join(author_names)

                j_obj = item.get("journal")
                journal = ""
                if isinstance(j_obj, dict):
                    journal = j_obj.get("name") or ""
                elif isinstance(j_obj, str):
                    journal = j_obj

                ext_ids = item.get("externalIds") or {}
                doi = ext_ids.get("DOI", "") or ""
                pmid = ext_ids.get("PubMed", "") or ""
                pmcid = ext_ids.get("PubMedCentral", "") or ""

                pub_types = item.get("publicationTypes") or []
                pub_type_str = ", ".join(pub_types) if pub_types else "Journal Article"

                url = item.get("url") or (f"https://doi.org/{doi}" if doi else "")

                papers.append({
                    "title": title,
                    "authors": authors_str,
                    "year": year,
                    "journal": journal or "Academic Publication",
                    "doi": doi,
                    "pmid": str(pmid),
                    "pmcid": str(pmcid),
                    "abstract": abstract,
                    "publication_type": pub_type_str,
                    "keywords": "",
                    "database_source": "Semantic Scholar",
                    "url": url,
                    "is_open_access": bool(item.get("isOpenAccess", False)),
                    "has_full_text": False
                })

        except Exception as e:
            print(f"[SemanticScholarClient] Error querying Semantic Scholar: {e}")

        return papers
