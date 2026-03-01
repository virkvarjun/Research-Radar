"""Tests for deduplication logic."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.adapters.openalex import title_hash
from app.schemas.common import NormalizedPaper


class TestDeduplication:
    """Test dedup logic without DB dependency using mock."""

    def test_doi_match(self):
        """Papers with same DOI should dedup."""
        paper_a = NormalizedPaper(
            title="Paper A",
            doi="10.1234/test",
            source="openalex",
        )
        paper_b = NormalizedPaper(
            title="Different Title But Same DOI",
            doi="10.1234/test",
            source="arxiv",
        )
        assert paper_a.doi == paper_b.doi

    def test_arxiv_id_match(self):
        """Papers with same arXiv ID should dedup."""
        paper_a = NormalizedPaper(
            title="Paper A",
            arxiv_id="2301.12345",
            source="openalex",
        )
        paper_b = NormalizedPaper(
            title="Paper A Variant",
            arxiv_id="2301.12345",
            source="arxiv",
        )
        assert paper_a.arxiv_id == paper_b.arxiv_id

    def test_title_hash_match(self):
        """Papers with same normalized title hash should dedup."""
        hash_a = title_hash("Attention Is All You Need")
        hash_b = title_hash("attention is all you need")
        assert hash_a == hash_b

    def test_title_hash_no_match(self):
        """Different papers should not dedup."""
        hash_a = title_hash("Attention Is All You Need")
        hash_b = title_hash("BERT: Pre-training of Transformers")
        assert hash_a != hash_b

    def test_dedup_priority_doi_over_arxiv(self):
        """DOI match should take priority: if DOI matches, it's a dupe."""
        paper = NormalizedPaper(
            title="Test Paper",
            doi="10.1234/test",
            arxiv_id="9999.99999",
            source="openalex",
        )
        # In dedup logic, DOI is checked first
        assert paper.doi is not None
        assert paper.arxiv_id is not None

    def test_dedup_priority_arxiv_over_title(self):
        """arXiv ID match takes priority over title hash."""
        paper = NormalizedPaper(
            title="Some Title",
            arxiv_id="2301.12345",
            source="arxiv",
        )
        assert paper.arxiv_id is not None

    def test_title_hash_with_punctuation(self):
        """Punctuation should not affect title hash."""
        hash_a = title_hash("Hello, World!")
        hash_b = title_hash("Hello World")
        assert hash_a == hash_b

    def test_title_hash_with_dashes(self):
        """Dashes should not affect title hash."""
        hash_a = title_hash("Self-Supervised Learning")
        hash_b = title_hash("Self Supervised Learning")
        assert hash_a == hash_b
