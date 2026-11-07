import re
from typing import List, Dict, Any, Optional
import requests
from config.settings import settings

class EuropePMCClient:
    """Client for Europe PMC REST API."""

    BASE_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"

    def __init__(self):
        self.timeout = settings.REQUEST_TIMEOUT
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "application/json"
        }

    def search_and_retrieve(
        self,
        query: str,
        max_results: int = 50,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        clean_query = query.strip()
        if start_year and end_year:
            clean_query += f" AND (PUB_YEAR:[{start_year} TO {end_year}])"
        elif start_year:
            clean_query += f" AND (PUB_YEAR:[{start_year} TO 3000])"
        elif end_year:
            clean_query += f" AND (PUB_YEAR:[1900 TO {end_year}])"

        params = {
            "query": clean_query,
            "format": "json",
            "pageSize": min(max_results, 100),
            "resultType": "core",
            "sort": "P_PDATE_D desc"
        }

        papers = []
        try:
            resp = requests.get(self.BASE_URL, params=params, headers=self.headers, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            result_list = data.get("resultList", {}).get("result", [])

            for item in result_list:
                title = item.get("title", "").strip()
                title = re.sub(r"<[^>]+>", "", title).strip()
                if not title:
                    continue

                pub_year = None
                raw_year = item.get("pubYear")
                if raw_year:
                    try:
                        pub_year = int(str(raw_year)[:4])
                    except ValueError:
                        pass

                journal = item.get("journalTitle") or item.get("bookOrReportDetails", {}).get("publisher") or "Biomedical Literature"
                if isinstance(journal, dict):
                    journal = journal.get("journalTitle", "Biomedical Literature")

                abstract = item.get("abstractText", "")
                abstract = re.sub(r"<[^>]+>", "", abstract).strip()

                doi = item.get("doi", "").strip()
                pmid = item.get("pmid", "").strip()
                pmcid = item.get("pmcid", "").strip()

                authors = item.get("authorString", "").strip()

                pub_type = item.get("pubType", "Journal Article")
                if isinstance(pub_type, list):
                    pub_type = ", ".join(pub_type)

                is_open_access = item.get("isOpenAccess", "N").upper() == "Y"

                keywords = []
                mesh_head = item.get("meshHeadingList", {}).get("meshHeading", [])
                for mh in mesh_head:
                    if isinstance(mh, dict) and "descriptorName" in mh:
                        keywords.append(mh["descriptorName"])
                    elif isinstance(mh, str):
                        keywords.append(mh)
                keywords_str = ", ".join(keywords[:10])

                url = f"https://europepmc.org/article/{item.get('source', 'MED')}/{pmid or doi or item.get('id', '')}"

                papers.append({
                    "title": title,
                    "authors": authors,
                    "year": pub_year,
                    "journal": str(journal),
                    "doi": doi,
                    "pmid": pmid,
                    "pmcid": pmcid,
                    "abstract": abstract,
                    "publication_type": pub_type,
                    "keywords": keywords_str,
                    "database_source": "Europe PMC",
                    "url": url,
                    "is_open_access": is_open_access,
                    "has_full_text": False
                })

        except Exception as e:
            print(f"[EuropePMCClient] Error querying Europe PMC: {e}")

        return papers
