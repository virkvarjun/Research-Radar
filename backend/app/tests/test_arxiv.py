"""Tests for arXiv adapter normalization."""

import xml.etree.ElementTree as ET

import pytest

from app.adapters.arxiv import normalize_arxiv_entry, title_hash, _clean_text

ATOM_NS = "{http://www.w3.org/2005/Atom}"


def _parse_first_entry(xml_str: str) -> ET.Element:
    root = ET.fromstring(xml_str)
    return root.find(f"{ATOM_NS}entry")


class TestNormalizeArxivEntry:
    def test_full_entry(self, sample_arxiv_xml):
        entry = _parse_first_entry(sample_arxiv_xml)
        result = normalize_arxiv_entry(entry)
        assert result is not None
        assert result.title == "A Novel Approach to Robot Learning"
        assert "transformers" in result.abstract.lower()
        assert len(result.authors) == 2
        assert result.authors[0]["name"] == "Jane Smith"
        assert result.arxiv_id == "2301.12345"
        assert result.doi == "10.1234/test.doi"
        assert result.source == "arxiv"
        assert result.pdf_url == "http://arxiv.org/pdf/2301.12345v1"
        assert "cs.RO" in result.categories
        assert "cs.AI" in result.categories
        assert result.published_date is not None
        assert result.published_date.year == 2023

    def test_minimal_entry(self, sample_arxiv_xml_minimal):
        entry = _parse_first_entry(sample_arxiv_xml_minimal)
        result = normalize_arxiv_entry(entry)
        assert result is not None
        assert result.title == "Minimal arXiv Paper"
        assert result.abstract is None
        assert result.authors == []
        assert result.arxiv_id == "2302.99999"
        assert result.doi is None
        assert result.pdf_url is None

    def test_no_title_returns_none(self, sample_arxiv_xml_no_title):
        entry = _parse_first_entry(sample_arxiv_xml_no_title)
        result = normalize_arxiv_entry(entry)
        assert result is None

    def test_multiple_categories(self, sample_arxiv_xml):
        entry = _parse_first_entry(sample_arxiv_xml)
        result = normalize_arxiv_entry(entry)
        assert len(result.categories) >= 2
        assert result.categories[0] == "cs.RO"  # Primary first


class TestCleanText:
    def test_removes_extra_whitespace(self):
        assert _clean_text("  hello   world  ") == "hello world"

    def test_removes_newlines(self):
        assert _clean_text("hello\n  world") == "hello world"


class TestArxivTitleHash:
    def test_same_as_openalex_hash(self):
        from app.adapters.openalex import title_hash as oa_hash
        # Both should produce the same hash for the same title
        assert title_hash("Test Paper") == oa_hash("Test Paper")

    def test_case_insensitive(self):
        assert title_hash("HELLO") == title_hash("hello")
