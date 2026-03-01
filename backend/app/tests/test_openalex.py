"""Tests for OpenAlex adapter normalization."""

import pytest

from app.adapters.openalex import (
    _normalize_title_hash,
    _reconstruct_abstract,
    normalize_openalex_work,
    title_hash,
)


class TestNormalizeOpenAlexWork:
    def test_full_work(self, sample_openalex_work):
        result = normalize_openalex_work(sample_openalex_work)
        assert result is not None
        assert result.title == "Attention Is All You Need"
        assert result.doi == "10.48550/arXiv.1706.03762"
        assert result.source == "openalex"
        assert len(result.authors) == 2
        assert result.authors[0]["name"] == "Ashish Vaswani"
        assert result.pdf_url == "https://arxiv.org/pdf/1706.03762"
        assert result.published_date is not None
        assert result.published_date.year == 2017
        assert len(result.categories) == 3
        assert "Transformer" in result.categories
        assert "https://openalex.org/I123" in result.institution_ids
        assert result.openalex_id == "https://openalex.org/W12345"

    def test_minimal_work(self, sample_openalex_work_minimal):
        result = normalize_openalex_work(sample_openalex_work_minimal)
        assert result is not None
        assert result.title == "Minimal Paper"
        assert result.doi is None
        assert result.abstract is None
        assert result.authors == []
        assert result.pdf_url is None
        assert result.published_date is None
        assert result.categories == []

    def test_no_title_returns_none(self, sample_openalex_work_no_title):
        result = normalize_openalex_work(sample_openalex_work_no_title)
        assert result is None

    def test_doi_prefix_stripped(self):
        work = {
            "id": "W1",
            "title": "Test",
            "doi": "https://doi.org/10.1234/test",
            "authorships": [],
            "concepts": [],
        }
        result = normalize_openalex_work(work)
        assert result.doi == "10.1234/test"

    def test_doi_without_prefix(self):
        work = {
            "id": "W1",
            "title": "Test",
            "doi": "10.1234/test",
            "authorships": [],
            "concepts": [],
        }
        result = normalize_openalex_work(work)
        assert result.doi == "10.1234/test"

    def test_oa_url_fallback(self):
        work = {
            "id": "W1",
            "title": "Test",
            "authorships": [],
            "concepts": [],
            "primary_location": {"pdf_url": None},
            "open_access": {"oa_url": "https://example.com/paper.pdf"},
        }
        result = normalize_openalex_work(work)
        assert result.pdf_url == "https://example.com/paper.pdf"

    def test_multiple_institutions_deduped(self):
        work = {
            "id": "W1",
            "title": "Test",
            "authorships": [
                {"author": {"display_name": "A"}, "institutions": [{"id": "I1"}]},
                {"author": {"display_name": "B"}, "institutions": [{"id": "I1"}, {"id": "I2"}]},
            ],
            "concepts": [],
        }
        result = normalize_openalex_work(work)
        assert len(result.institution_ids) == 2
        assert "I1" in result.institution_ids
        assert "I2" in result.institution_ids


class TestReconstructAbstract:
    def test_basic_reconstruction(self):
        inverted = {"Hello": [0], "world": [1], "test": [2]}
        result = _reconstruct_abstract(inverted)
        assert result == "Hello world test"

    def test_empty_index(self):
        assert _reconstruct_abstract({}) == ""
        assert _reconstruct_abstract(None) == ""

    def test_out_of_order(self):
        inverted = {"c": [2], "a": [0], "b": [1]}
        result = _reconstruct_abstract(inverted)
        assert result == "a b c"

    def test_repeated_word(self):
        inverted = {"the": [0, 2], "cat": [1]}
        result = _reconstruct_abstract(inverted)
        assert result == "the cat the"


class TestTitleHash:
    def test_same_title_same_hash(self):
        assert title_hash("Hello World") == title_hash("Hello World")

    def test_case_insensitive(self):
        assert title_hash("Hello World") == title_hash("hello world")

    def test_punctuation_ignored(self):
        assert title_hash("Hello, World!") == title_hash("Hello World")

    def test_whitespace_normalized(self):
        assert title_hash("Hello  World") == title_hash("Hello World")

    def test_different_titles_different_hash(self):
        assert title_hash("Paper A") != title_hash("Paper B")
