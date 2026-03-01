"""PDF extraction and evidence/rigour analysis."""

import logging
import re
import tempfile
from typing import Optional

import httpx

from app.services.embeddings import embed_texts

logger = logging.getLogger(__name__)

# Patterns for evidence extraction
DATASET_PATTERNS = [
    r"(?:the\s+)?([A-Z][A-Za-z0-9\-]+(?:[\s\-][A-Z0-9][A-Za-z0-9\-]*)*)\s+(?:dataset|benchmark|corpus)",
    r"(?:dataset|benchmark|corpus)(?:s)?[\s:]+([A-Z][A-Za-z0-9\-]+(?:[\s\-][A-Za-z0-9\-]+)*)",
    r"(?:trained|evaluated|tested)\s+on\s+(?:the\s+)?([A-Z][A-Za-z0-9\-]+(?:[\s\-][A-Za-z0-9\-]+)*)",
]

METRIC_PATTERNS = [
    r"(accuracy|precision|recall|F1|BLEU|ROUGE|AUC|mAP|IoU|perplexity|loss)\s*(?:of|=|:)?\s*([\d.]+%?)",
]

BASELINE_PATTERNS = [
    r"(?:[Cc]ompar(?:ed?|ing)\s+(?:to|with|against))\s+([A-Z][A-Za-z0-9\-]+(?:\s+(?:and\s+)?[A-Z][A-Za-z0-9\-]+)*)",
    r"(?:[Bb]aseline(?:s)?|[Oo]utperform(?:s|ed)?)\s+([A-Z][A-Za-z0-9\-]+(?:\s[A-Za-z0-9\-]+)*)",
    r"([A-Z][A-Za-z0-9\-]+(?:\s+and\s+[A-Z][A-Za-z0-9\-]+)*)\s+baseline(?:s)?",
]

CODE_LINK_PATTERNS = [
    r"(https?://github\.com/[\w\-]+/[\w\-]+)",
    r"(https?://gitlab\.com/[\w\-]+/[\w\-]+)",
    r"(?:code|implementation|source)\s+(?:is\s+)?(?:available\s+)?(?:at\s+)?(https?://[^\s]+)",
]

LIMITATION_PATTERNS = [
    r"(?:limitation|shortcoming|weakness|drawback|caveat)s?\s*(?::|include|are|is)?\s*(.{20,200}?)(?:\.|$)",
]


def extract_evidence(text: str) -> dict:
    """Extract evidence fields from paper text.

    Returns dict with: datasets, metrics, baselines, limitations, code_link
    Each field is either a list/string or None.
    Status indicators: found (✅), partial (⚠️), not_found (❌)
    """
    evidence = {
        "datasets": {"items": [], "status": "not_found", "indicator": "❌"},
        "metrics": {"items": [], "status": "not_found", "indicator": "❌"},
        "baselines": {"items": [], "status": "not_found", "indicator": "❌"},
        "limitations": {"items": [], "status": "not_found", "indicator": "❌"},
        "code_link": {"url": None, "status": "not_found", "indicator": "❌"},
    }

    if not text:
        return evidence

    # Datasets
    for pattern in DATASET_PATTERNS:
        matches = re.findall(pattern, text)
        evidence["datasets"]["items"].extend(matches[:10])
    if evidence["datasets"]["items"]:
        evidence["datasets"]["status"] = "found"
        evidence["datasets"]["indicator"] = "✅"

    # Metrics
    for pattern in METRIC_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        evidence["metrics"]["items"].extend(
            [{"name": m[0], "value": m[1]} for m in matches[:10]]
        )
    if evidence["metrics"]["items"]:
        evidence["metrics"]["status"] = "found"
        evidence["metrics"]["indicator"] = "✅"

    # Baselines
    for pattern in BASELINE_PATTERNS:
        matches = re.findall(pattern, text)
        evidence["baselines"]["items"].extend(matches[:10])
    if evidence["baselines"]["items"]:
        evidence["baselines"]["status"] = "found"
        evidence["baselines"]["indicator"] = "✅"

    # Code link
    for pattern in CODE_LINK_PATTERNS:
        match = re.search(pattern, text)
        if match:
            evidence["code_link"]["url"] = match.group(1) if match.lastindex else match.group(0)
            evidence["code_link"]["status"] = "found"
            evidence["code_link"]["indicator"] = "✅"
            break

    # Limitations
    for pattern in LIMITATION_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        evidence["limitations"]["items"].extend(matches[:5])
    if evidence["limitations"]["items"]:
        evidence["limitations"]["status"] = "found"
        evidence["limitations"]["indicator"] = "✅"

    return evidence


async def fetch_and_extract_pdf(pdf_url: str) -> Optional[tuple[str, list[dict]]]:
    """Download PDF and extract text + chunks.

    Returns (full_text, chunks_list) or None on failure.
    chunks_list: [{"index": int, "text": str}, ...]
    """
    if not pdf_url:
        return None

    try:
        async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
            resp = await client.get(pdf_url)
            resp.raise_for_status()
            pdf_bytes = resp.content
    except httpx.HTTPError as e:
        logger.error(f"PDF download error for {pdf_url}: {e}")
        return None

    return extract_text_from_pdf_bytes(pdf_bytes)


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> Optional[tuple[str, list[dict]]]:
    """Extract text from PDF bytes using PyMuPDF."""
    try:
        import fitz  # PyMuPDF

        with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp:
            tmp.write(pdf_bytes)
            tmp.flush()

            doc = fitz.open(tmp.name)
            full_text = ""
            chunks = []
            chunk_size = 1000  # chars per chunk, with overlap

            for page in doc:
                full_text += page.get_text() + "\n"
            doc.close()

            # Split into chunks with overlap
            overlap = 200
            pos = 0
            idx = 0
            while pos < len(full_text):
                end = pos + chunk_size
                chunk_text = full_text[pos:end].strip()
                if chunk_text:
                    chunks.append({"index": idx, "text": chunk_text})
                    idx += 1
                pos += chunk_size - overlap

            return full_text, chunks

    except Exception as e:
        logger.error(f"PDF extraction error: {e}")
        return None


def build_rigour_panel(evidence: dict) -> dict:
    """Build the rigour panel summary from evidence."""
    panel = {}
    for key in ["datasets", "metrics", "baselines", "limitations", "code_link"]:
        entry = evidence.get(key, {})
        panel[key] = {
            "status": entry.get("status", "not_found"),
            "indicator": entry.get("indicator", "❌"),
        }
        if key == "code_link":
            panel[key]["url"] = entry.get("url")
        else:
            panel[key]["items"] = entry.get("items", [])
            panel[key]["count"] = len(entry.get("items", []))
    return panel
