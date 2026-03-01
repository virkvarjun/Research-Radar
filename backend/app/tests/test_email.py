"""Tests for email rendering and signature verification."""

import uuid

import pytest

from app.services.email import (
    generate_feedback_url,
    render_digest_html,
    verify_feedback_signature,
)


class TestFeedbackSignature:
    def test_generate_and_verify(self):
        user_id = uuid.uuid4()
        paper_id = uuid.uuid4()
        url = generate_feedback_url(user_id, paper_id, "save")
        # Extract sig from URL
        assert "sig=" in url
        sig = url.split("sig=")[1]
        assert verify_feedback_signature(str(user_id), str(paper_id), "save", sig)

    def test_url_points_to_backend(self):
        """Feedback URLs must point to backend_url, not app_url."""
        user_id = uuid.uuid4()
        paper_id = uuid.uuid4()
        url = generate_feedback_url(user_id, paper_id, "save")
        # Should contain the backend URL (port 8000 by default), not frontend (3000)
        assert "localhost:8000" in url or "backend" in url

    def test_wrong_action_fails(self):
        user_id = uuid.uuid4()
        paper_id = uuid.uuid4()
        url = generate_feedback_url(user_id, paper_id, "save")
        sig = url.split("sig=")[1]
        assert not verify_feedback_signature(str(user_id), str(paper_id), "skip", sig)

    def test_wrong_user_fails(self):
        user_id = uuid.uuid4()
        paper_id = uuid.uuid4()
        url = generate_feedback_url(user_id, paper_id, "save")
        sig = url.split("sig=")[1]
        assert not verify_feedback_signature(str(uuid.uuid4()), str(paper_id), "save", sig)


class TestRenderDigestHtml:
    def test_renders_papers(self):
        user_id = uuid.uuid4()
        papers = [
            {
                "id": str(uuid.uuid4()),
                "title": "Test Paper One",
                "abstract": "This is a test abstract for paper one.",
                "authors": [{"name": "Alice"}, {"name": "Bob"}],
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Test Paper Two",
                "abstract": "Another abstract.",
                "authors": [{"name": "Charlie"}],
            },
        ]
        html = render_digest_html(papers, user_id)
        assert "Research Radar" in html
        assert "Test Paper One" in html
        assert "Test Paper Two" in html
        assert "Alice" in html
        assert "Save" in html
        assert "Not interested" in html
        assert "View feed" in html

    def test_renders_empty(self):
        user_id = uuid.uuid4()
        html = render_digest_html([], user_id)
        assert "Research Radar" in html
        assert "No new papers" in html

    def test_five_papers(self):
        user_id = uuid.uuid4()
        papers = [
            {
                "id": str(uuid.uuid4()),
                "title": f"Paper {i}",
                "abstract": f"Abstract {i}",
                "authors": [{"name": f"Author {i}"}],
            }
            for i in range(5)
        ]
        html = render_digest_html(papers, user_id)
        assert "Paper 0" in html
        assert "Paper 4" in html

    def test_long_title_escaped(self):
        user_id = uuid.uuid4()
        papers = [{
            "id": str(uuid.uuid4()),
            "title": 'Paper with "quotes" & <tags>',
            "abstract": "Test",
            "authors": [],
        }]
        html = render_digest_html(papers, user_id)
        assert "&amp;" in html
        assert "&lt;" in html
        assert "&gt;" in html
        assert "&quot;" in html

    def test_many_authors_truncated(self):
        user_id = uuid.uuid4()
        papers = [{
            "id": str(uuid.uuid4()),
            "title": "Test",
            "abstract": "",
            "authors": [{"name": f"Author {i}"} for i in range(10)],
        }]
        html = render_digest_html(papers, user_id)
        assert "et al." in html

    def test_long_abstract_truncated(self):
        user_id = uuid.uuid4()
        papers = [{
            "id": str(uuid.uuid4()),
            "title": "Test",
            "abstract": "x" * 500,
            "authors": [],
        }]
        html = render_digest_html(papers, user_id)
        assert "..." in html
