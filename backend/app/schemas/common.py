from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# --- Onboarding ---

class OnboardingAnswers(BaseModel):
    role: str = Field(..., pattern=r"^(student|builder|lab)$")
    topics: list[str] = Field(..., min_length=1)
    anchor_labels: dict[str, str] = Field(
        default_factory=dict,
        description="paper_id -> interested|neutral|not_interested",
    )
    pairwise_choices: list[dict] = Field(
        default_factory=list,
        description="List of {winner_id, loser_id}",
    )


# --- Papers ---

class PaperOut(BaseModel):
    id: UUID
    title: str
    abstract: Optional[str] = None
    authors: Optional[list[dict]] = None
    doi: Optional[str] = None
    arxiv_id: Optional[str] = None
    source: str
    pdf_url: Optional[str] = None
    published_date: Optional[datetime] = None
    categories: Optional[list] = None
    evidence: Optional[dict] = None
    why_matched: Optional[dict] = None

    model_config = {"from_attributes": True}


class PaperDetail(PaperOut):
    rigour_panel: Optional[dict] = None
    chunks_available: bool = False


# --- Feed ---

class FeedResponse(BaseModel):
    papers: list[PaperOut]
    has_more: bool = False


# --- Feedback ---

class FeedbackRequest(BaseModel):
    paper_id: UUID
    action: str = Field(..., pattern=r"^(like|save|skip|not_relevant|click)$")
    source: str = Field(default="web", pattern=r"^(web|email)$")


class FeedbackResponse(BaseModel):
    status: str = "ok"


# --- University ---

class InstitutionOut(BaseModel):
    id: UUID
    openalex_id: str
    name: str
    country: Optional[str] = None

    model_config = {"from_attributes": True}


class UniversitySearchResponse(BaseModel):
    institutions: list[InstitutionOut]


# --- Saved ---

class SavedPaperOut(BaseModel):
    id: UUID
    paper: PaperOut
    saved_at: datetime

    model_config = {"from_attributes": True}


# --- Chat ---

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)


class ChatCitation(BaseModel):
    chunk_index: int
    text: str
    score: float


class ChatResponse(BaseModel):
    answer: str
    citations: list[ChatCitation]


# --- Settings ---

class UserSettings(BaseModel):
    role: str
    topics: Optional[list[str]] = None
    digest_enabled: bool = True
    institutions: list[InstitutionOut] = []

    model_config = {"from_attributes": True}


class UpdateSettings(BaseModel):
    role: Optional[str] = Field(None, pattern=r"^(student|builder|lab)$")
    topics: Optional[list[str]] = None
    digest_enabled: Optional[bool] = None
    institution_ids: Optional[list[UUID]] = None


# --- Normalized paper from adapters ---

class NormalizedPaper(BaseModel):
    title: str
    abstract: Optional[str] = None
    authors: list[dict] = Field(default_factory=list)
    doi: Optional[str] = None
    arxiv_id: Optional[str] = None
    openalex_id: Optional[str] = None
    source: str
    pdf_url: Optional[str] = None
    published_date: Optional[datetime] = None
    categories: list[str] = Field(default_factory=list)
    institution_ids: list[str] = Field(default_factory=list)
