"""Tests for evidence extraction."""

import pytest

from app.services.evidence import extract_evidence, build_rigour_panel


class TestExtractEvidence:
    def test_full_extraction(self, sample_paper_text):
        evidence = extract_evidence(sample_paper_text)

        assert evidence["datasets"]["status"] == "found"
        assert evidence["datasets"]["indicator"] == "✅"
        assert len(evidence["datasets"]["items"]) > 0

        assert evidence["metrics"]["status"] == "found"
        assert len(evidence["metrics"]["items"]) > 0

        assert evidence["baselines"]["status"] == "found"
        assert len(evidence["baselines"]["items"]) > 0

        assert evidence["code_link"]["status"] == "found"
        assert "github.com" in evidence["code_link"]["url"]

        assert evidence["limitations"]["status"] == "found"

    def test_empty_text(self):
        evidence = extract_evidence("")
        for key in ["datasets", "metrics", "baselines", "limitations"]:
            assert evidence[key]["status"] == "not_found"
            assert evidence[key]["indicator"] == "❌"
        assert evidence["code_link"]["status"] == "not_found"

    def test_none_text(self):
        evidence = extract_evidence(None)
        assert evidence["datasets"]["status"] == "not_found"

    def test_no_datasets(self):
        text = "We trained the model and it worked well."
        evidence = extract_evidence(text)
        assert evidence["datasets"]["status"] == "not_found"

    def test_code_link_github(self):
        text = "Code available at https://github.com/user/repo for reproduction."
        evidence = extract_evidence(text)
        assert evidence["code_link"]["url"] == "https://github.com/user/repo"

    def test_code_link_gitlab(self):
        text = "Implementation: https://gitlab.com/user/repo"
        evidence = extract_evidence(text)
        assert evidence["code_link"]["url"] == "https://gitlab.com/user/repo"

    def test_metrics_extraction(self):
        text = "Our model achieves accuracy of 97.5% and BLEU of 42.3"
        evidence = extract_evidence(text)
        assert evidence["metrics"]["status"] == "found"
        items = evidence["metrics"]["items"]
        metric_names = [m["name"].lower() for m in items]
        assert "accuracy" in metric_names


class TestBuildRigourPanel:
    def test_full_panel(self, sample_paper_text):
        evidence = extract_evidence(sample_paper_text)
        panel = build_rigour_panel(evidence)

        assert "datasets" in panel
        assert "metrics" in panel
        assert "baselines" in panel
        assert "limitations" in panel
        assert "code_link" in panel

        assert panel["datasets"]["indicator"] == "✅"
        assert panel["code_link"]["url"] is not None

    def test_empty_evidence(self):
        evidence = extract_evidence("")
        panel = build_rigour_panel(evidence)
        for key in ["datasets", "metrics", "baselines", "limitations"]:
            assert panel[key]["indicator"] == "❌"
            assert panel[key]["count"] == 0
