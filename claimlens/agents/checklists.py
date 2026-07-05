from __future__ import annotations

from claimlens.core.models import EvidenceItem, EvidenceType

CLAIM_REQUIREMENTS: dict[str, set[EvidenceType]] = {
    "auto_collision": {
        EvidenceType.PDF,
        EvidenceType.IMAGE,
        EvidenceType.TEXT,
    },
    "recorded_statement": {
        EvidenceType.AUDIO,
        EvidenceType.TEXT,
    },
    "vehicle_safety": {
        EvidenceType.TEXT,
    },
}


def find_missing_evidence(claim_type: str, evidence: list[EvidenceItem]) -> list[str]:
    required = CLAIM_REQUIREMENTS.get(claim_type, set())
    present = {item.type for item in evidence}
    missing = sorted(item.value for item in required - present)
    return [f"Missing required {item} evidence" for item in missing]
