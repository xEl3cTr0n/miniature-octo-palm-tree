from claimlens.agents.checklists import find_missing_evidence
from claimlens.core.ingestion import chunk_evidence
from claimlens.core.models import EvidenceItem, EvidenceType
from claimlens.core.retrieval import HybridRetriever
from claimlens.evaluators.faithfulness import citation_coverage


def test_retriever_returns_relevant_damage_evidence() -> None:
    item = EvidenceItem(
        id="photo-note-1",
        type=EvidenceType.TEXT,
        title="Adjuster note",
        content="Rear bumper damage is visible and the repair estimate lists replacement.",
    )
    chunks = chunk_evidence(item)

    hits = HybridRetriever(chunks).search("rear bumper repair")

    assert hits
    assert hits[0].chunk.citation == "Adjuster note#chunk-1"


def test_missing_evidence_for_auto_collision() -> None:
    evidence = [
        EvidenceItem(
            id="claim-form",
            type=EvidenceType.PDF,
            title="Claim form",
            content="Loss date and claimant statement.",
        )
    ]

    assert find_missing_evidence("auto_collision", evidence) == [
        "Missing required image evidence",
        "Missing required text evidence",
    ]


def test_citation_coverage_is_deterministic() -> None:
    score = citation_coverage(
        "rear bumper damage supported",
        ["photo shows rear bumper damage"],
    )

    assert score == 0.75
