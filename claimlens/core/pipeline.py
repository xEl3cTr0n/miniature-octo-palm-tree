from __future__ import annotations

from claimlens.agents.checklists import find_missing_evidence
from claimlens.core.ingestion import chunk_evidence
from claimlens.core.models import ClaimAnswer, EvidenceItem
from claimlens.core.retrieval import HybridRetriever


def answer_claim(
    question: str,
    evidence: list[EvidenceItem],
    *,
    claim_type: str = "auto_collision",
    limit: int = 4,
) -> ClaimAnswer:
    chunks = [chunk for item in evidence for chunk in chunk_evidence(item)]
    hits = HybridRetriever(chunks).search(question, limit=limit)
    citations = [hit.chunk.citation for hit in hits]
    contexts = [hit.chunk.text for hit in hits]

    if not hits:
        return ClaimAnswer(
            answer="I could not find enough grounded evidence to answer this question.",
            confidence=0.2,
            citations=[],
            missing_evidence=find_missing_evidence(claim_type, evidence),
            contradictions=[],
        )

    answer = (
        "The available evidence is relevant but needs human review. "
        + " ".join(contexts[:2])
    ).strip()

    return ClaimAnswer(
        answer=answer,
        confidence=0.72,
        citations=citations,
        missing_evidence=find_missing_evidence(claim_type, evidence),
        contradictions=[],
    )
