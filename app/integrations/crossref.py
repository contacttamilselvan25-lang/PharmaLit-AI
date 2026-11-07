import urllib.parse
from typing import Dict, Any, Optional
import requests
from config.settings import settings

class CrossrefClient:
    """Client for Crossref REST API for DOI verification and metadata resolution."""

    BASE_URL = "https://api.crossref.org/works"

    def __init__(self):
        self.timeout = 10
        self.headers = {
            "User-Agent": settings.USER_AGENT
        }

    def verify_doi(self, doi: str) -> Dict[str, Any]:
        clean_doi = doi.strip()
        if clean_doi.startswith("https://doi.org/"):
            clean_doi = clean_doi.replace("https://doi.org/", "")
        elif clean_doi.startswith("http://dx.doi.org/"):
            clean_doi = clean_doi.replace("http://dx.doi.org/", "")

        if not clean_doi:
            return {"valid": False, "error": "Empty DOI provided"}

        encoded_doi = urllib.parse.quote(clean_doi)
        url = f"{self.BASE_URL}/{encoded_doi}"

        try:
            resp = requests.get(url, headers=self.headers, timeout=self.timeout)
            if resp.status_code == 200:
                msg = resp.json().get("message", {})
                title = msg.get("title", [""])[0] if msg.get("title") else ""
                journal = msg.get("container-title", [""])[0] if msg.get("container-title") else ""
                
                year = None
                date_parts = msg.get("published-print", {}).get("date-parts") or msg.get("published-online", {}).get("date-parts") or msg.get("created", {}).get("date-parts")
                if date_parts and date_parts[0]:
                    year = date_parts[0][0]

                return {
                    "valid": True,
                    "doi": clean_doi,
                    "title": title,
                    "journal": journal,
                    "year": year,
                    "publisher": msg.get("publisher", ""),
                    "is_referenced_by_count": msg.get("is-referenced-by-count", 0),
                    "url": msg.get("URL", f"https://doi.org/{clean_doi}")
                }
            elif resp.status_code == 404:
                return {"valid": False, "error": "DOI not found on Crossref"}
            else:
                return {"valid": False, "error": f"Crossref returned HTTP {resp.status_code}"}
        except Exception as e:
            return {"valid": False, "error": str(e)}
