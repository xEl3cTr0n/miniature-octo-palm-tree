from __future__ import annotations

import os
from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel, Field

from claimlens.api.dashboard import render_dashboard
from claimlens.core.cases import (
    CaseActivityEvent,
    CaseRecord,
    CaseReport,
    CaseStore,
    CaseSummary,
)
from claimlens.core.models import ClaimAnswer, EvidenceItem, EvidenceType
from claimlens.core.pipeline import answer_claim
from claimlens.data_sources.nhtsa import (
    NHTSADataSourceError,
    evidence_to_dict,
    fetch_vehicle_evidence,
)
from claimlens.demo_cases import build_demo_case
from claimlens.evaluators.harness import load_evaluation_dataset, run_evaluation

DEFAULT_CASE_DB_PATH = Path("var/claimlens_cases.sqlite3")
CASE_BUNDLE_SCHEMA_VERSION = "claimlens.case_bundle.v1"

app = FastAPI(title="ClaimLens", version="0.1.0")


def build_case_store() -> CaseStore:
    database_path = os.getenv("CLAIMLENS_CASE_DB")
    return CaseStore(database_path=database_path or DEFAULT_CASE_DB_PATH)


case_store = build_case_store()


class EvidencePayload(BaseModel):
    id: str
    type: EvidenceType
    title: str
    content: str
    metadata: dict[str, str] = Field(default_factory=dict)


class AskRequest(BaseModel):
    claim_type: str = "auto_collision"
    question: str
    evidence: list[EvidencePayload]


class CaseCreateRequest(BaseModel):
    title: str
    claim_type: str = "auto_collision"
    source: str = "manual"
    evidence: list[EvidencePayload]


class CaseBundlePayload(BaseModel):
    schema_version: str = CASE_BUNDLE_SCHEMA_VERSION
    exported_case_id: str | None = None
    title: str
    claim_type: str
    source: str
    evidence: list[EvidencePayload]


class StoredCaseAskRequest(BaseModel):
    question: str


class NHTSAAskRequest(BaseModel):
    make: str = "Honda"
    model: str = "Accord"
    year: int = 2020
    question: str = "Do complaints or recalls mention warning lights or rear camera failure?"
    max_complaints: int = Field(default=10, ge=1, le=50)
    max_recalls: int = Field(default=5, ge=1, le=20)


class NHTSACaseImportRequest(BaseModel):
    make: str = "Honda"
    model: str = "Accord"
    year: int = 2020
    max_complaints: int = Field(default=10, ge=1, le=50)
    max_recalls: int = Field(default=5, ge=1, le=20)


class CaseDeleteResponse(BaseModel):
    case_id: str
    deleted: bool


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def dashboard() -> str:
    return render_dashboard()


@app.post("/ask", response_model=ClaimAnswer)
def ask(request: AskRequest) -> ClaimAnswer:
    evidence = [EvidenceItem(**item.model_dump()) for item in request.evidence]
    return answer_claim(request.question, evidence, claim_type=request.claim_type)


@app.post("/cases", response_model=CaseRecord)
def create_case(request: CaseCreateRequest) -> CaseRecord:
    evidence = [EvidenceItem(**item.model_dump()) for item in request.evidence]
    record = case_store.create_case(
        title=request.title,
        claim_type=request.claim_type,
        evidence=evidence,
        source=request.source,
    )
    case_store.record_activity(
        case_id=record.case_id,
        event_type="manual_case_created",
        summary=f"Created {record.title} from {record.source} evidence.",
    )
    return record


@app.post("/cases/demo", response_model=CaseRecord)
def seed_demo_case() -> CaseRecord:
    demo_case = build_demo_case()
    record = case_store.create_case(
        title=demo_case.title,
        claim_type=demo_case.claim_type,
        evidence=demo_case.evidence,
        source=demo_case.source,
    )
    case_store.record_activity(
        case_id=record.case_id,
        event_type="demo_case_seeded",
        summary=f"Seeded deterministic demo case {record.title}.",
    )
    return record


@app.get("/cases", response_model=list[CaseSummary])
def list_cases() -> list[CaseSummary]:
    return case_store.list_cases()


@app.get("/activity", response_model=list[CaseActivityEvent])
def list_activity() -> list[CaseActivityEvent]:
    return case_store.list_activity()


@app.get("/cases/{case_id}", response_model=CaseRecord)
def get_case(case_id: str) -> CaseRecord:
    try:
        return case_store.get_case(case_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/cases/{case_id}/bundle.json", response_model=CaseBundlePayload)
def export_case_bundle(case_id: str) -> CaseBundlePayload:
    try:
        record = case_store.get_case(case_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    case_store.record_activity(
        case_id=record.case_id,
        event_type="bundle_exported",
        summary=f"Exported portable JSON bundle for {record.title}.",
    )
    return CaseBundlePayload(
        exported_case_id=record.case_id,
        title=record.title,
        claim_type=record.claim_type,
        source=record.source,
        evidence=[
            EvidencePayload(
                id=item.id,
                type=item.type,
                title=item.title,
                content=item.content,
                metadata=item.metadata,
            )
            for item in record.evidence
        ],
    )


@app.post("/cases/import/bundle", response_model=CaseRecord)
def import_case_bundle(request: CaseBundlePayload) -> CaseRecord:
    if request.schema_version != CASE_BUNDLE_SCHEMA_VERSION:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported case bundle schema: {request.schema_version}",
        )
    evidence = [EvidenceItem(**item.model_dump()) for item in request.evidence]
    record = case_store.create_case(
        title=request.title,
        claim_type=request.claim_type,
        evidence=evidence,
        source=request.source,
    )
    case_store.record_activity(
        case_id=record.case_id,
        event_type="bundle_imported",
        summary=f"Imported portable JSON bundle for {record.title}.",
    )
    return record


@app.get("/cases/{case_id}/activity", response_model=list[CaseActivityEvent])
def case_activity(case_id: str) -> list[CaseActivityEvent]:
    return case_store.list_activity(case_id=case_id)


@app.delete("/cases/{case_id}", response_model=CaseDeleteResponse)
def delete_case(case_id: str) -> CaseDeleteResponse:
    try:
        record = case_store.get_case(case_id)
        case_store.delete_case(case_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    case_store.record_activity(
        case_id=case_id,
        event_type="case_deleted",
        summary=f"Deleted {record.title}.",
    )
    return CaseDeleteResponse(case_id=case_id, deleted=True)


@app.post("/cases/{case_id}/ask", response_model=ClaimAnswer)
def ask_case(case_id: str, request: StoredCaseAskRequest) -> ClaimAnswer:
    try:
        answer = case_store.ask_case(case_id, request.question)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    case_store.record_activity(
        case_id=case_id,
        event_type="question_answered",
        summary="Answered reviewer question against stored evidence.",
    )
    return answer


@app.get("/cases/{case_id}/report", response_model=CaseReport)
def case_report(case_id: str) -> CaseReport:
    try:
        report = case_store.build_report(case_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    case_store.record_activity(
        case_id=case_id,
        event_type="report_generated",
        summary=f"Generated reviewer report for {report.title}.",
    )
    return report


@app.get("/cases/{case_id}/report.md")
def case_report_markdown(case_id: str) -> Response:
    try:
        markdown = case_store.build_report_markdown(case_id)
        record = case_store.get_case(case_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    case_store.record_activity(
        case_id=case_id,
        event_type="report_markdown_exported",
        summary=f"Exported Markdown report for {record.title}.",
    )
    return Response(content=markdown, media_type="text/markdown")


@app.get("/data-sources/nhtsa/vehicle-evidence")
def nhtsa_vehicle_evidence(
    make: str = "Honda",
    model: str = "Accord",
    year: int = 2020,
    max_complaints: int = 10,
    max_recalls: int = 5,
) -> dict[str, object]:
    try:
        evidence = fetch_vehicle_evidence(
            make=make,
            model=model,
            year=year,
            max_complaints=max_complaints,
            max_recalls=max_recalls,
        )
    except NHTSADataSourceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {
        "source": "nhtsa",
        "vehicle": {"make": make, "model": model, "year": year},
        "evidence_count": len(evidence),
        "evidence": [evidence_to_dict(item) for item in evidence],
    }


@app.post("/ask/nhtsa", response_model=ClaimAnswer)
def ask_nhtsa(request: NHTSAAskRequest) -> ClaimAnswer:
    try:
        evidence = fetch_vehicle_evidence(
            make=request.make,
            model=request.model,
            year=request.year,
            max_complaints=request.max_complaints,
            max_recalls=request.max_recalls,
        )
    except NHTSADataSourceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return answer_claim(request.question, evidence, claim_type="vehicle_safety")


@app.get("/evals/demo")
def demo_evaluation() -> dict[str, object]:
    summary = run_evaluation(load_evaluation_dataset())
    return asdict(summary)


@app.post("/cases/import/nhtsa", response_model=CaseRecord)
def import_nhtsa_case(request: NHTSACaseImportRequest) -> CaseRecord:
    try:
        evidence = fetch_vehicle_evidence(
            make=request.make,
            model=request.model,
            year=request.year,
            max_complaints=request.max_complaints,
            max_recalls=request.max_recalls,
        )
    except NHTSADataSourceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    record = case_store.create_case(
        title=f"{request.year} {request.make} {request.model} NHTSA safety review",
        claim_type="vehicle_safety",
        evidence=evidence,
        source="nhtsa",
    )
    case_store.record_activity(
        case_id=record.case_id,
        event_type="nhtsa_case_imported",
        summary=f"Imported NHTSA evidence for {record.title}.",
    )
    return record
