"""OpenAlex API adapter for works and institution search."""

import hashlib
import logging
from datetime import datetime, timezone
from typing import Optional

import httpx

from app.config import settings
from app.schemas.common import NormalizedPaper

logger = logging.getLogger(__name__)

BASE_URL = "https://api.openalex.org"


def _headers() -> dict:
    return {"User-Agent": f"ResearchRadar/1.0 (mailto:{settings.openalex_email})"}


def _normalize_title_hash(title: str) -> str:
    """Create a normalized hash of the title for deduplication."""
    normalized = title.lower().strip()
    # Replace hyphens/dashes with spaces (so "self-supervised" == "self supervised")
    for ch in "-–—":
        normalized = normalized.replace(ch, " ")
    # Remove other punctuation
    for ch in ".,;:!?''\"()[]{}":
        normalized = normalized.replace(ch, "")
    # Collapse whitespace
    normalized = " ".join(normalized.split())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def normalize_openalex_work(work: dict) -> Optional[NormalizedPaper]:
    """Normalize an OpenAlex work into our unified schema."""
    title = work.get("title")
    if not title:
        return None

    # Extract abstract from inverted index if available
    abstract = None
    abstract_inv = work.get("abstract_inverted_index")
    if abstract_inv:
        abstract = _reconstruct_abstract(abstract_inv)

    # Authors
    authors = []
    for authorship in work.get("authorships", []):
        author = authorship.get("author", {})
        authors.append({
            "name": author.get("display_name", "Unknown"),
            "openalex_id": author.get("id"),
        })

    # DOI
    doi = work.get("doi")
    if doi and doi.startswith("https://doi.org/"):
        doi = doi[len("https://doi.org/"):]

    # Published date
    pub_date = None
    pub_date_str = work.get("publication_date")
    if pub_date_str:
        try:
            pub_date = datetime.fromisoformat(pub_date_str).replace(tzinfo=timezone.utc)
        except (ValueError, TypeError):
            pass

    # PDF URL
    pdf_url = None
    primary_location = work.get("primary_location") or {}
    if primary_location.get("pdf_url"):
        pdf_url = primary_location["pdf_url"]
    elif work.get("open_access", {}).get("oa_url"):
        pdf_url = work["open_access"]["oa_url"]

    # Categories/concepts
    categories = []
    for concept in work.get("concepts", [])[:5]:
        categories.append(concept.get("display_name", ""))

    # Institution IDs
    institution_ids = []
    for authorship in work.get("authorships", []):
        for inst in authorship.get("institutions", []):
            if inst.get("id"):
                institution_ids.append(inst["id"])
    institution_ids = list(set(institution_ids))

    return NormalizedPaper(
        title=title,
        abstract=abstract,
        authors=authors,
        doi=doi,
        arxiv_id=None,
        openalex_id=work.get("id"),
        source="openalex",
        pdf_url=pdf_url,
        published_date=pub_date,
        categories=categories,
        institution_ids=institution_ids,
    )


def _reconstruct_abstract(inverted_index: dict) -> str:
    """Reconstruct abstract text from OpenAlex inverted index format."""
    if not inverted_index:
        return ""
    word_positions: list[tuple[int, str]] = []
    for word, positions in inverted_index.items():
        for pos in positions:
            word_positions.append((pos, word))
    word_positions.sort(key=lambda x: x[0])
    return " ".join(w for _, w in word_positions)


async def fetch_recent_works(
    from_date: str,
    to_date: Optional[str] = None,
    per_page: int = 200,
    max_pages: int = 5,
) -> list[NormalizedPaper]:
    """Fetch recent works from OpenAlex."""
    papers = []
    filter_str = f"from_publication_date:{from_date}"
    if to_date:
        filter_str += f",to_publication_date:{to_date}"

    async with httpx.AsyncClient(timeout=30.0) as client:
        for page in range(1, max_pages + 1):
            url = f"{BASE_URL}/works"
            params = {
                "filter": filter_str,
                "per_page": per_page,
                "page": page,
                "sort": "publication_date:desc",
            }
            try:
                resp = await client.get(url, params=params, headers=_headers())
                resp.raise_for_status()
                data = resp.json()
                results = data.get("results", [])
                if not results:
                    break
                for work in results:
                    normalized = normalize_openalex_work(work)
                    if normalized:
                        papers.append(normalized)
            except httpx.HTTPError as e:
                logger.error(f"OpenAlex fetch error page {page}: {e}")
                break

    return papers


async def search_institutions(query: str, per_page: int = 10) -> list[dict]:
    """Search OpenAlex institutions."""
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            resp = await client.get(
                f"{BASE_URL}/institutions",
                params={"search": query, "per_page": per_page},
                headers=_headers(),
            )
            resp.raise_for_status()
            results = resp.json().get("results", [])
            return [
                {
                    "openalex_id": inst["id"],
                    "name": inst.get("display_name", ""),
                    "country": inst.get("country_code"),
                    "ror_id": inst.get("ror"),
                }
                for inst in results
            ]
        except httpx.HTTPError as e:
            logger.error(f"Institution search error: {e}")
            return []


async def fetch_works_by_institution(
    institution_openalex_id: str,
    from_date: Optional[str] = None,
    per_page: int = 50,
) -> list[NormalizedPaper]:
    """Fetch recent works from a specific institution."""
    filter_str = f"institutions.id:{institution_openalex_id}"
    if from_date:
        filter_str += f",from_publication_date:{from_date}"

    papers = []
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(
                f"{BASE_URL}/works",
                params={
                    "filter": filter_str,
                    "per_page": per_page,
                    "sort": "publication_date:desc",
                },
                headers=_headers(),
            )
            resp.raise_for_status()
            for work in resp.json().get("results", []):
                normalized = normalize_openalex_work(work)
                if normalized:
                    papers.append(normalized)
        except httpx.HTTPError as e:
            logger.error(f"Institution works fetch error: {e}")

    return papers


def title_hash(title: str) -> str:
    """Public alias for title hashing, used in dedup."""
    return _normalize_title_hash(title)
