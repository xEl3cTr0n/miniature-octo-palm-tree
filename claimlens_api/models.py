from __future__ import annotations

from enum import Enum
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field


class EvidenceType(str, Enum):
    DOCUMENT = "document"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    EMAIL = "email"
    STRUCTURED = "structured"


class EvidenceItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    case_id: str
    title: str
    type: EvidenceType
    content: str
    source_uri: str | None = None
    metadata: dict[str, str] = Field(default_factory=dict)


class CaseCreate(BaseModel):
    case_id: str
    title: str
    claim_type: str = "auto_collision"
    evidence: list[EvidenceItem]


class Citation(BaseModel):
    evidence_id: str
    title: str
    snippet: str
    relevance_score: float = Field(ge=0.0, le=1.0)


class QueryRequest(BaseModel):
    question: str
    top_k: int = Field(default=5, ge=1, le=20)


class QueryResponse(BaseModel):
    answer: str
    confidence: Literal["low", "medium", "high"]
    citations: list[Citation]
    recommended_action: str


class Finding(BaseModel):
    severity: Literal["low", "medium", "high"]
    summary: str
    evidence_ids: list[str]


class MissingEvidenceResponse(BaseModel):
    claim_type: str
    missing_required: list[str]
    present_required: list[str]


class Report(BaseModel):
    case_id: str
    title: str
    executive_summary: str
    key_evidence: list[Citation]
    contradictions: list[Finding]
    missing_evidence: MissingEvidenceResponse
    reviewer_next_steps: list[str]
