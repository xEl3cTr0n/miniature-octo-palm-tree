from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from claimlens.core.models import ClaimAnswer, EvidenceItem, EvidenceType
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
    def __init__(self, database_path: str | Path = ":memory:") -> None:
        self.database_path = self._prepare_database_path(database_path)
        self._connection = sqlite3.connect(self.database_path, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._ensure_schema()

    def _prepare_database_path(self, database_path: str | Path) -> str:
        if str(database_path) == ":memory:":
            return ":memory:"
        path = Path(database_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        return str(path)

    def _ensure_schema(self) -> None:
        with self._connection:
            self._connection.execute(
                """
                CREATE TABLE IF NOT EXISTS cases (
                    case_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    claim_type TEXT NOT NULL,
                    source TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    evidence_json TEXT NOT NULL
                )
                """
            )

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
        with self._connection:
            self._connection.execute(
                """
                INSERT INTO cases (
                    case_id,
                    title,
                    claim_type,
                    source,
                    created_at,
                    evidence_json
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    record.case_id,
                    record.title,
                    record.claim_type,
                    record.source,
                    record.created_at,
                    self._serialize_evidence(record.evidence),
                ),
            )
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
            for record in self._list_records()
        ]

    def get_case(self, case_id: str) -> CaseRecord:
        row = self._connection.execute(
            """
            SELECT case_id, title, claim_type, source, created_at, evidence_json
            FROM cases
            WHERE case_id = ?
            """,
            (case_id,),
        ).fetchone()
        if row is None:
            raise KeyError(f"Case not found: {case_id}")
        return self._record_from_row(row)

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

    def _list_records(self) -> list[CaseRecord]:
        rows = self._connection.execute(
            """
            SELECT case_id, title, claim_type, source, created_at, evidence_json
            FROM cases
            ORDER BY created_at DESC
            """
        ).fetchall()
        return [self._record_from_row(row) for row in rows]

    def _record_from_row(self, row: sqlite3.Row) -> CaseRecord:
        evidence = self._deserialize_evidence(row["evidence_json"])
        return CaseRecord(
            case_id=row["case_id"],
            title=row["title"],
            claim_type=row["claim_type"],
            evidence=evidence,
            evidence_count=len(evidence),
            source=row["source"],
            created_at=row["created_at"],
        )

    def _serialize_evidence(self, evidence: list[EvidenceItem]) -> str:
        payload = [
            {
                "id": item.id,
                "type": item.type.value,
                "title": item.title,
                "content": item.content,
                "metadata": item.metadata,
            }
            for item in evidence
        ]
        return json.dumps(payload, sort_keys=True)

    def _deserialize_evidence(self, payload: str) -> list[EvidenceItem]:
        items: list[dict[str, Any]] = json.loads(payload)
        return [
            EvidenceItem(
                id=item["id"],
                type=EvidenceType(item["type"]),
                title=item["title"],
                content=item["content"],
                metadata=item.get("metadata", {}),
            )
            for item in items
        ]
