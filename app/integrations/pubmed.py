import time
import urllib.parse
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
import requests
from config.settings import settings

class PubMedClient:
    """Client for NCBI PubMed E-utilities API (eSearch and eFetch)."""

    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    def __init__(self, api_key: Optional[str] = None, email: Optional[str] = None):
        self.api_key = api_key or settings.PUBMED_API_KEY
        self.email = email or settings.PUBMED_EMAIL
        self.timeout = settings.REQUEST_TIMEOUT
        self.headers = {
            "User-Agent": settings.USER_AGENT
        }

    def _get_base_params(self) -> Dict[str, str]:
        params = {"email": self.email, "tool": "pharmalit_ai"}
        if self.api_key:
            params["api_key"] = self.api_key
        return params

    def search(self, query: str, max_results: int = 50, start_year: Optional[int] = None, end_year: Optional[int] = None) -> List[str]:
        term = query.strip()
        if start_year and end_year:
            term += f' AND ("{start_year}"[Date - Publication] : "{end_year}"[Date - Publication])'
        elif start_year:
            term += f' AND ("{start_year}"[Date - Publication] : "3000"[Date - Publication])'
        elif end_year:
            term += f' AND ("1900"[Date - Publication] : "{end_year}"[Date - Publication])'

        params = self._get_base_params()
        params.update({
            "db": "pubmed",
            "term": term,
            "retmode": "json",
            "retmax": str(max_results),
            "sort": "relevance"
        })

        url = f"{self.BASE_URL}/esearch.fcgi"
        try:
            resp = requests.get(url, params=params, headers=self.headers, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            id_list = data.get("esearchresult", {}).get("idlist", [])
            return id_list
        except Exception as e:
            print(f"[PubMedClient.search] Error querying PubMed: {e}")
            return []

    def fetch_details(self, pmids: List[str]) -> List[Dict[str, Any]]:
        if not pmids:
            return []

        all_papers = []
        chunk_size = 50

        for i in range(0, len(pmids), chunk_size):
            chunk = pmids[i:i + chunk_size]
            params = self._get_base_params()
            params.update({
                "db": "pubmed",
                "id": ",".join(chunk),
                "retmode": "xml"
            })
            url = f"{self.BASE_URL}/efetch.fcgi"

            try:
                resp = requests.get(url, params=params, headers=self.headers, timeout=self.timeout)
                resp.raise_for_status()
                papers = self._parse_pubmed_xml(resp.content)
                all_papers.extend(papers)
                time.sleep(0.35)
            except Exception as e:
                print(f"[PubMedClient.fetch_details] Error fetching XML for chunk: {e}")

        return all_papers

    def _parse_pubmed_xml(self, xml_bytes: bytes) -> List[Dict[str, Any]]:
        papers = []
        try:
            root = ET.fromstring(xml_bytes)
        except ET.ParseError as e:
            print(f"[PubMedClient] XML Parse error: {e}")
            return papers

        for article in root.findall(".//PubmedArticle"):
            try:
                pmid_elem = article.find(".//MedlineCitation/PMID")
                pmid = pmid_elem.text.strip() if pmid_elem is not None and pmid_elem.text else ""

                title_elem = article.find(".//ArticleTitle")
                title = "".join(title_elem.itertext()).strip() if title_elem is not None else ""
                if not title:
                    continue

                journal_elem = article.find(".//Journal/Title")
                journal = journal_elem.text.strip() if journal_elem is not None and journal_elem.text else ""
                if not journal:
                    j_short = article.find(".//Journal/ISOAbbreviation")
                    journal = j_short.text.strip() if j_short is not None and j_short.text else "Biomedical Journal"

                year = None
                pub_date = article.find(".//JournalIssue/PubDate")
                if pub_date is not None:
                    y_elem = pub_date.find("Year")
                    if y_elem is not None and y_elem.text:
                        try:
                            year = int(y_elem.text.strip()[:4])
                        except ValueError:
                            pass
                    if not year:
                        med_elem = pub_date.find("MedlineDate")
                        if med_elem is not None and med_elem.text:
                            for token in med_elem.text.split():
                                if token.isdigit() and len(token) == 4:
                                    year = int(token)
                                    break

                authors_list = []
                for author in article.findall(".//AuthorList/Author"):
                    last = author.find("LastName")
                    fore = author.find("ForeName") or author.find("FirstName")
                    if last is not None and last.text:
                        name = last.text.strip()
                        if fore is not None and fore.text:
                            name = f"{last.text.strip()} {fore.text.strip()}"
                        authors_list.append(name)
                    else:
                        collab = author.find("CollectiveName")
                        if collab is not None and collab.text:
                            authors_list.append(collab.text.strip())
                authors_str = ", ".join(authors_list)

                abstract_parts = []
                for abs_elem in article.findall(".//Abstract/AbstractText"):
                    label = abs_elem.get("Label")
                    text = "".join(abs_elem.itertext()).strip()
                    if text:
                        if label:
                            abstract_parts.append(f"{label}: {text}")
                        else:
                            abstract_parts.append(text)
                abstract_str = "\n\n".join(abstract_parts)

                doi = ""
                pmcid = ""
                for article_id in article.findall(".//ArticleIdList/ArticleId"):
                    id_type = article_id.get("IdType")
                    val = article_id.text.strip() if article_id.text else ""
                    if id_type == "doi" and not doi:
                        doi = val
                    elif id_type == "pmc" and not pmcid:
                        pmcid = val

                if not doi:
                    for eloc in article.findall(".//ELocationID"):
                        if eloc.get("EIdType") == "doi" and eloc.text:
                            doi = eloc.text.strip()
                            break

                pub_types = []
                for pt in article.findall(".//PublicationType"):
                    if pt.text:
                        pub_types.append(pt.text.strip())
                publication_type = ", ".join(pub_types) if pub_types else "Journal Article"

                mesh_terms = []
                for mesh in article.findall(".//MeshHeading/DescriptorName"):
                    if mesh.text:
                        mesh_terms.append(mesh.text.strip())
                keywords = ", ".join(mesh_terms)

                url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else f"https://doi.org/{doi}" if doi else ""

                papers.append({
                    "title": title,
                    "authors": authors_str,
                    "year": year,
                    "journal": journal,
                    "doi": doi,
                    "pmid": pmid,
                    "pmcid": pmcid,
                    "abstract": abstract_str,
                    "publication_type": publication_type,
                    "keywords": keywords,
                    "database_source": "PubMed",
                    "url": url,
                    "is_open_access": bool(pmcid),
                    "has_full_text": False
                })
            except Exception as e:
                print(f"[PubMedClient] Error parsing article node: {e}")
                continue

        return papers

    def search_and_retrieve(self, query: str, max_results: int = 50, start_year: Optional[int] = None, end_year: Optional[int] = None) -> List[Dict[str, Any]]:
        pmids = self.search(query, max_results=max_results, start_year=start_year, end_year=end_year)
        if not pmids:
            return []
        return self.fetch_details(pmids)
