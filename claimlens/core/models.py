from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class EvidenceType(str, Enum):
    PDF = "pdf"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    TEXT = "text"
    TABULAR = "tabular"


@dataclass(frozen=True)
class EvidenceItem:
    id: str
    type: EvidenceType
    title: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class EvidenceChunk:
    id: str
    evidence_id: str
    text: str
    citation: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RetrievalHit:
    chunk: EvidenceChunk
    score: float


@dataclass(frozen=True)
class ClaimAnswer:
    answer: str
    confidence: float
    citations: list[str]
    missing_evidence: list[str]
    contradictions: list[str]
