"""arXiv API adapter for recent works ingestion."""

import hashlib
import logging
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Optional

import httpx

from app.schemas.common import NormalizedPaper

logger = logging.getLogger(__name__)

BASE_URL = "http://export.arxiv.org/api/query"
ATOM_NS = "{http://www.w3.org/2005/Atom}"
ARXIV_NS = "{http://arxiv.org/schemas/atom}"

DEFAULT_CATEGORIES = ["cs.AI", "cs.RO", "stat.ML"]


def normalize_arxiv_entry(entry: ET.Element) -> Optional[NormalizedPaper]:
    """Normalize an arXiv Atom entry into our unified schema."""
    title_el = entry.find(f"{ATOM_NS}title")
    if title_el is None or not title_el.text:
        return None

    title = _clean_text(title_el.text)

    # Abstract
    abstract = None
    summary_el = entry.find(f"{ATOM_NS}summary")
    if summary_el is not None and summary_el.text:
        abstract = _clean_text(summary_el.text)

    # Authors
    authors = []
    for author_el in entry.findall(f"{ATOM_NS}author"):
        name_el = author_el.find(f"{ATOM_NS}name")
        if name_el is not None and name_el.text:
            authors.append({"name": name_el.text.strip()})

    # arXiv ID
    id_el = entry.find(f"{ATOM_NS}id")
    arxiv_id = None
    if id_el is not None and id_el.text:
        # Extract ID from URL like http://arxiv.org/abs/2301.12345v1
        match = re.search(r"(\d{4}\.\d{4,5})(v\d+)?$", id_el.text)
        if match:
            arxiv_id = match.group(1)

    # DOI
    doi = None
    doi_el = entry.find(f"{ARXIV_NS}doi")
    if doi_el is not None and doi_el.text:
        doi = doi_el.text.strip()

    # Published date
    pub_date = None
    published_el = entry.find(f"{ATOM_NS}published")
    if published_el is not None and published_el.text:
        try:
            pub_date = datetime.fromisoformat(
                published_el.text.replace("Z", "+00:00")
            )
        except (ValueError, TypeError):
            pass

    # PDF URL
    pdf_url = None
    for link_el in entry.findall(f"{ATOM_NS}link"):
        if link_el.get("title") == "pdf":
            pdf_url = link_el.get("href")
            break

    # Categories
    categories = []
    for cat_el in entry.findall(f"{ARXIV_NS}primary_category"):
        term = cat_el.get("term")
        if term:
            categories.append(term)
    for cat_el in entry.findall(f"{ATOM_NS}category"):
        term = cat_el.get("term")
        if term and term not in categories:
            categories.append(term)

    return NormalizedPaper(
        title=title,
        abstract=abstract,
        authors=authors,
        doi=doi,
        arxiv_id=arxiv_id,
        openalex_id=None,
        source="arxiv",
        pdf_url=pdf_url,
        published_date=pub_date,
        categories=categories,
        institution_ids=[],
    )


def _clean_text(text: str) -> str:
    """Remove extra whitespace and newlines from text."""
    return " ".join(text.split())


async def fetch_recent_papers(
    categories: Optional[list[str]] = None,
    max_results: int = 200,
) -> list[NormalizedPaper]:
    """Fetch recent papers from arXiv for given categories."""
    if categories is None:
        categories = DEFAULT_CATEGORIES

    # Build search query: cat:cs.AI OR cat:cs.RO OR cat:stat.ML
    cat_query = "+OR+".join(f"cat:{cat}" for cat in categories)
    query = f"({cat_query})"

    papers = []
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            resp = await client.get(
                BASE_URL,
                params={
                    "search_query": query,
                    "start": 0,
                    "max_results": max_results,
                    "sortBy": "submittedDate",
                    "sortOrder": "descending",
                },
            )
            resp.raise_for_status()
            root = ET.fromstring(resp.text)
            for entry in root.findall(f"{ATOM_NS}entry"):
                normalized = normalize_arxiv_entry(entry)
                if normalized:
                    papers.append(normalized)
        except httpx.HTTPError as e:
            logger.error(f"arXiv fetch error: {e}")
        except ET.ParseError as e:
            logger.error(f"arXiv XML parse error: {e}")

    return papers


def title_hash(title: str) -> str:
    """Create normalized title hash for dedup."""
    normalized = title.lower().strip()
    for ch in "-–—":
        normalized = normalized.replace(ch, " ")
    for ch in ".,;:!?''\"()[]{}":
        normalized = normalized.replace(ch, "")
    normalized = " ".join(normalized.split())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
