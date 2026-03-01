"""Tests for chat-with-paper service."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.chat import _answer_from_abstract, _generate_answer


class TestAnswerFromAbstract:
    def test_with_abstract(self):
        """When abstract is present, answer should include it."""
        paper = MagicMock()
        paper.title = "Test Paper"
        paper.abstract = "This paper proposes a novel method."
        result = _answer_from_abstract(paper, "What is this about?")
        assert "Test Paper" in result
        assert "novel method" in result
        assert "Full text has not been extracted" in result

    def test_without_abstract(self):
        """When no abstract, should say it cannot answer."""
        paper = MagicMock()
        paper.title = "Test Paper"
        paper.abstract = None
        result = _answer_from_abstract(paper, "What is this about?")
        assert "not been extracted" in result
        assert "cannot answer" in result

    def test_empty_abstract(self):
        """Empty string abstract should be treated as missing."""
        paper = MagicMock()
        paper.title = "Test Paper"
        paper.abstract = ""
        result = _answer_from_abstract(paper, "What is this about?")
        # Empty string is falsy, so it should say cannot answer
        assert "not been extracted" in result


class TestGenerateAnswer:
    @pytest.mark.asyncio
    async def test_generate_answer_success(self):
        """Should return LLM answer when API works."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "The paper discusses attention mechanisms."

        with patch("app.services.chat.OpenAI") as MockOpenAI:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            MockOpenAI.return_value = mock_client

            result = await _generate_answer("Test Title", "Some context", "What is it about?")
            assert "attention mechanisms" in result

    @pytest.mark.asyncio
    async def test_generate_answer_api_error(self):
        """Should return error message when API fails."""
        with patch("app.services.chat.OpenAI") as MockOpenAI:
            mock_client = MagicMock()
            mock_client.chat.completions.create.side_effect = Exception("API down")
            MockOpenAI.return_value = mock_client

            result = await _generate_answer("Test Title", "Some context", "What is it about?")
            assert "Error" in result or "error" in result
            assert "citations" in result.lower() or "chunks" in result.lower()

    @pytest.mark.asyncio
    async def test_generate_answer_empty_response(self):
        """Should handle None content from LLM."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = None

        with patch("app.services.chat.OpenAI") as MockOpenAI:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            MockOpenAI.return_value = mock_client

            result = await _generate_answer("Test Title", "Context", "Question?")
            assert result == "No answer generated."
