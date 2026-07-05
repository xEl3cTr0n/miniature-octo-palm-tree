from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from claimlens.core.ingestion import chunk_evidence
from claimlens.core.models import ClaimAnswer, EvidenceItem, EvidenceType
from claimlens.core.pipeline import answer_claim
from claimlens.evaluators.faithfulness import citation_coverage

DEFAULT_EVAL_DATASET = (
    Path(__file__).resolve().parents[2]
    / "datasets"
    / "evals"
    / "vehicle_safety_cases.json"
)


@dataclass(frozen=True)
class EvaluationExample:
    id: str
    question: str
    claim_type: str
    evidence: list[EvidenceItem]
    expected_citations: list[str]
    min_citation_coverage: float = 0.5


@dataclass(frozen=True)
class EvaluationResult:
    id: str
    question: str
    answer: ClaimAnswer
    citation_coverage: float
    expected_citation_recall: float
    passed: bool


@dataclass(frozen=True)
class EvaluationSummary:
    example_count: int
    passed_count: int
    pass_rate: float
    average_citation_coverage: float
    average_expected_citation_recall: float
    results: list[EvaluationResult]


def load_evaluation_dataset(path: Path = DEFAULT_EVAL_DATASET) -> list[EvaluationExample]:
    payload: list[dict[str, Any]] = json.loads(path.read_text())
    return [_example_from_dict(item) for item in payload]


def run_evaluation(examples: Iterable[EvaluationExample]) -> EvaluationSummary:
    results = [_evaluate_example(example) for example in examples]
    example_count = len(results)
    passed_count = sum(1 for result in results if result.passed)
    return EvaluationSummary(
        example_count=example_count,
        passed_count=passed_count,
        pass_rate=_average([1.0 if result.passed else 0.0 for result in results]),
        average_citation_coverage=_average(
            [result.citation_coverage for result in results]
        ),
        average_expected_citation_recall=_average(
            [result.expected_citation_recall for result in results]
        ),
        results=results,
    )


def _evaluate_example(example: EvaluationExample) -> EvaluationResult:
    answer = answer_claim(
        example.question,
        example.evidence,
        claim_type=example.claim_type,
    )
    cited_contexts = _contexts_for_citations(answer.citations, example.evidence)
    coverage = citation_coverage(answer.answer, cited_contexts)
    citation_recall = _expected_citation_recall(
        expected=example.expected_citations,
        actual=answer.citations,
    )
    return EvaluationResult(
        id=example.id,
        question=example.question,
        answer=answer,
        citation_coverage=coverage,
        expected_citation_recall=citation_recall,
        passed=(
            coverage >= example.min_citation_coverage
            and citation_recall == 1.0
            and answer.confidence >= 0.5
        ),
    )


def _contexts_for_citations(
    citations: list[str], evidence: list[EvidenceItem]
) -> list[str]:
    chunks_by_citation = {
        chunk.citation: chunk.text
        for item in evidence
        for chunk in chunk_evidence(item)
    }
    return [
        chunks_by_citation[citation]
        for citation in citations
        if citation in chunks_by_citation
    ]


def _expected_citation_recall(expected: list[str], actual: list[str]) -> float:
    if not expected:
        return 1.0
    expected_set = set(expected)
    actual_set = set(actual)
    return round(len(expected_set & actual_set) / len(expected_set), 3)


def _average(values: list[float]) -> float:
    if not values:
        return 0.0
    return round(sum(values) / len(values), 3)


def _example_from_dict(payload: dict[str, Any]) -> EvaluationExample:
    return EvaluationExample(
        id=payload["id"],
        question=payload["question"],
        claim_type=payload["claim_type"],
        evidence=[
            EvidenceItem(
                id=item["id"],
                type=EvidenceType(item["type"]),
                title=item["title"],
                content=item["content"],
                metadata=item.get("metadata", {}),
            )
            for item in payload["evidence"]
        ],
        expected_citations=list(payload["expected_citations"]),
        min_citation_coverage=float(payload.get("min_citation_coverage", 0.5)),
    )
