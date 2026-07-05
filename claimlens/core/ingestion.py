from __future__ import annotations

from pathlib import Path

from claimlens.core.models import EvidenceChunk, EvidenceItem, EvidenceType

_EXTENSION_MAP = {
    ".pdf": EvidenceType.PDF,
    ".png": EvidenceType.IMAGE,
    ".jpg": EvidenceType.IMAGE,
    ".jpeg": EvidenceType.IMAGE,
    ".wav": EvidenceType.AUDIO,
    ".mp3": EvidenceType.AUDIO,
    ".mp4": EvidenceType.VIDEO,
    ".mov": EvidenceType.VIDEO,
    ".csv": EvidenceType.TABULAR,
    ".txt": EvidenceType.TEXT,
    ".md": EvidenceType.TEXT,
}


def detect_evidence_type(path: Path) -> EvidenceType:
    return _EXTENSION_MAP.get(path.suffix.lower(), EvidenceType.TEXT)


def chunk_evidence(item: EvidenceItem, *, max_chars: int = 700) -> list[EvidenceChunk]:
    """Create deterministic chunks suitable for tests and local demos.

    Production adapters can replace this with OCR, ASR, video frame sampling,
    layout-aware parsing, and multimodal embedding jobs.
    """
    text = " ".join(item.content.split())
    if not text:
        return []

    chunks: list[EvidenceChunk] = []
    for index, start in enumerate(range(0, len(text), max_chars), start=1):
        part = text[start : start + max_chars]
        chunks.append(
            EvidenceChunk(
                id=f"{item.id}:chunk-{index}",
                evidence_id=item.id,
                text=part,
                citation=f"{item.title}#chunk-{index}",
                metadata={**item.metadata, "evidence_type": item.type.value},
            )
        )
    return chunks
