from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

from claimlens.core.models import ClaimAnswer, EvidenceItem
from claimlens.core.pipeline import answer_claim

DEFAULT_REVIEWER_STEPS = [
    "Review cited evidence before disposition.",
    "Request missing evidence if required items are absent.",
    "Escalate low-confidence or contradiction-heavy cases to a human reviewer.",
]


@dataclass(frozen=True)
class CaseRecord:
    case_id: str
    title: str
    claim_type: str
    evidence: list[EvidenceItem]
    evidence_count: int
    source: str = "manual"
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass(frozen=True)
class CaseSummary:
    case_id: str
    title: str
    claim_type: str
    evidence_count: int
    source: str
    created_at: str


@dataclass(frozen=True)
class CaseReport:
    case_id: str
    title: str
    summary: str
    answer: ClaimAnswer
    evidence_count: int
    next_steps: list[str]


class CaseStore:
    def __init__(self) -> None:
        self._cases: dict[str, CaseRecord] = {}

    def create_case(
        self,
        *,
        title: str,
        claim_type: str,
        evidence: list[EvidenceItem],
        source: str = "manual",
        case_id: str | None = None,
    ) -> CaseRecord:
        record = CaseRecord(
            case_id=case_id or f"case-{uuid4().hex[:12]}",
            title=title,
            claim_type=claim_type,
            evidence=evidence,
            evidence_count=len(evidence),
            source=source,
        )
        self._cases[record.case_id] = record
        return record

    def list_cases(self) -> list[CaseSummary]:
        return [
            CaseSummary(
                case_id=record.case_id,
                title=record.title,
                claim_type=record.claim_type,
                evidence_count=record.evidence_count,
                source=record.source,
                created_at=record.created_at,
            )
            for record in sorted(
                self._cases.values(), key=lambda item: item.created_at, reverse=True
            )
        ]

    def get_case(self, case_id: str) -> CaseRecord:
        try:
            return self._cases[case_id]
        except KeyError as exc:
            raise KeyError(f"Case not found: {case_id}") from exc

    def ask_case(self, case_id: str, question: str) -> ClaimAnswer:
        record = self.get_case(case_id)
        return answer_claim(question, record.evidence, claim_type=record.claim_type)

    def build_report(self, case_id: str) -> CaseReport:
        record = self.get_case(case_id)
        report_query = " ".join(
            [record.title, *(item.content for item in record.evidence[:3])]
        )
        answer = self.ask_case(
            case_id,
            report_query,
        )
        summary = (
            f"ClaimLens reviewed {record.evidence_count} evidence items for "
            f"{record.title} and generated a citation-backed reviewer summary."
        )
        return CaseReport(
            case_id=record.case_id,
            title=record.title,
            summary=summary,
            answer=answer,
            evidence_count=record.evidence_count,
            next_steps=list(DEFAULT_REVIEWER_STEPS),
        )
