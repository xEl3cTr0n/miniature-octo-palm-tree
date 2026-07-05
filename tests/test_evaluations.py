from pathlib import Path

from claimlens.core.models import EvidenceItem, EvidenceType
from claimlens.evaluators.harness import (
    EvaluationExample,
    load_evaluation_dataset,
    run_evaluation,
)


def test_run_evaluation_reports_citation_recall_and_pass_rate() -> None:
    example = EvaluationExample(
        id="rear-camera-recall",
        question="Does the evidence mention rear camera failure?",
        claim_type="vehicle_safety",
        evidence=[
            EvidenceItem(
                id="nhtsa-recall-20V771000",
                type=EvidenceType.TEXT,
                title="NHTSA recall 20V771000",
                content="A BCM software error may disable the rearview camera.",
                metadata={"source": "nhtsa_recalls"},
            )
        ],
        expected_citations=["NHTSA recall 20V771000#chunk-1"],
        min_citation_coverage=0.45,
    )

    summary = run_evaluation([example])

    assert summary.example_count == 1
    assert summary.pass_rate == 1.0
    assert summary.average_expected_citation_recall == 1.0
    assert summary.results[0].passed is True
    assert summary.results[0].expected_citation_recall == 1.0


def test_load_evaluation_dataset_from_json() -> None:
    examples = load_evaluation_dataset(
        Path("datasets/evals/vehicle_safety_cases.json")
    )

    assert len(examples) >= 2
    assert examples[0].id
    assert examples[0].evidence
    assert examples[0].expected_citations
