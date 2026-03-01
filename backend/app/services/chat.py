"""RAG chat service for saved papers."""

import logging
from typing import Optional
from uuid import UUID

import numpy as np
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import Paper, PaperChunk, SavedPaper
from app.schemas.common import ChatCitation, ChatResponse
from app.services.embeddings import cosine_similarity, embed_text

logger = logging.getLogger(__name__)


async def chat_with_paper(
    db: AsyncSession,
    user_id: UUID,
    paper_id: UUID,
    question: str,
) -> ChatResponse:
    """Answer a question about a saved paper using RAG with citations."""
    # Verify paper is saved by user
    result = await db.execute(
        select(SavedPaper).where(
            SavedPaper.user_id == user_id,
            SavedPaper.paper_id == paper_id,
        )
    )
    if not result.scalar_one_or_none():
        raise ValueError("Paper must be saved before chatting. Save it first.")

    # Get paper and chunks
    result = await db.execute(select(Paper).where(Paper.id == paper_id))
    paper = result.scalar_one_or_none()
    if not paper:
        raise ValueError("Paper not found")

    result = await db.execute(
        select(PaperChunk)
        .where(PaperChunk.paper_id == paper_id)
        .order_by(PaperChunk.chunk_index)
    )
    chunks = result.scalars().all()

    if not chunks:
        # Fall back to abstract-only answer
        return ChatResponse(
            answer=_answer_from_abstract(paper, question),
            citations=[],
        )

    # Embed question
    q_embedding = await embed_text(question)
    if q_embedding is None:
        return ChatResponse(
            answer="Unable to process question.",
            citations=[],
        )

    # Rank chunks by similarity
    scored_chunks = []
    for chunk in chunks:
        if chunk.embedding is not None:
            sim = cosine_similarity(q_embedding, chunk.embedding)
            scored_chunks.append((chunk, sim))

    scored_chunks.sort(key=lambda x: x[1], reverse=True)
    top_chunks = scored_chunks[:5]

    if not top_chunks:
        return ChatResponse(
            answer=_answer_from_abstract(paper, question),
            citations=[],
        )

    # Build context for LLM
    context_parts = []
    citations = []
    for chunk, score in top_chunks:
        context_parts.append(f"[Chunk {chunk.chunk_index}]: {chunk.text}")
        citations.append(
            ChatCitation(
                chunk_index=chunk.chunk_index,
                text=chunk.text[:300],
                score=round(score, 4),
            )
        )

    context = "\n\n".join(context_parts)
    answer = await _generate_answer(paper.title, context, question)

    return ChatResponse(answer=answer, citations=citations)


def _answer_from_abstract(paper: Paper, question: str) -> str:
    """Generate a basic answer from just the abstract."""
    if not paper.abstract:
        return (
            "This paper's full text has not been extracted yet, and no abstract is available. "
            "I cannot answer your question without source text."
        )
    return (
        f"Based on the abstract of '{paper.title}':\n\n"
        f"{paper.abstract}\n\n"
        f"Note: Full text has not been extracted. For more detailed answers, "
        f"the PDF needs to be processed first."
    )


async def _generate_answer(title: str, context: str, question: str) -> str:
    """Generate an answer using the LLM with provided context."""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=settings.openai_api_key)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"You are a research assistant answering questions about the paper '{title}'. "
                        "Use ONLY the provided text chunks to answer. "
                        "Cite chunks using [Chunk N] notation. "
                        "If the answer cannot be found in the chunks, say so explicitly."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Context from the paper:\n{context}\n\nQuestion: {question}",
                },
            ],
            max_tokens=1000,
            temperature=0.2,
        )
        return response.choices[0].message.content or "No answer generated."
    except Exception as e:
        logger.error(f"LLM answer generation error: {e}")
        return f"Error generating answer: {e}. The relevant chunks have been retrieved — see citations."
