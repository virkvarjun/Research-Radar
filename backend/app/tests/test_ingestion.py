"""Tests for ingestion service logic (dedup + evidence extraction)."""

import pytest

from app.schemas.common import NormalizedPaper
from app.services.evidence import extract_evidence


class TestIngestionEvidence:
    """Verify that evidence extraction would work on typical abstracts."""

    def test_abstract_with_datasets(self):
        """Abstracts mentioning datasets should extract them."""
        abstract = (
            "We evaluate on the ImageNet dataset and CIFAR-10 benchmark. "
            "Our method achieves accuracy of 95.3%."
        )
        evidence = extract_evidence(abstract)
        assert evidence["datasets"]["status"] == "found"
        assert evidence["metrics"]["status"] == "found"

    def test_abstract_with_code_link(self):
        """Abstracts with GitHub links should extract them."""
        abstract = "Code available at https://github.com/test/repo"
        evidence = extract_evidence(abstract)
        assert evidence["code_link"]["status"] == "found"
        assert evidence["code_link"]["url"] == "https://github.com/test/repo"

    def test_abstract_without_evidence(self):
        """Abstracts without evidence should return all not_found."""
        abstract = "We propose a new approach to solving problems."
        evidence = extract_evidence(abstract)
        assert evidence["datasets"]["status"] == "not_found"
        assert evidence["metrics"]["status"] == "not_found"
        assert evidence["baselines"]["status"] == "not_found"
        assert evidence["code_link"]["status"] == "not_found"
        assert evidence["limitations"]["status"] == "not_found"

    def test_normalized_paper_builds_correctly(self):
        """NormalizedPaper should accept all fields."""
        paper = NormalizedPaper(
            title="Test Paper",
            abstract="An abstract.",
            authors=[{"name": "Alice"}],
            doi="10.1234/test",
            arxiv_id="2301.12345",
            openalex_id="W12345",
            source="openalex",
            pdf_url="https://example.com/paper.pdf",
            categories=["ML"],
            institution_ids=["I1"],
        )
        assert paper.title == "Test Paper"
        assert paper.doi == "10.1234/test"

    def test_normalized_paper_minimal(self):
        """NormalizedPaper with just required fields."""
        paper = NormalizedPaper(title="Minimal", source="arxiv")
        assert paper.abstract is None
        assert paper.authors == []
        assert paper.categories == []
