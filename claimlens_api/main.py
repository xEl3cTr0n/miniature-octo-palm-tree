from __future__ import annotations

from fastapi import FastAPI, HTTPException

from .models import CaseCreate, MissingEvidenceResponse, QueryRequest, QueryResponse, Report
from .pipeline import answer_question, build_report, check_missing_evidence, detect_contradictions

app = FastAPI(
    title="ClaimLens API",
    version="0.1.0",
    description="Multimodal evidence intelligence API for claim and compliance review.",
)

CASES: dict[str, CaseCreate] = {}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/cases", response_model=CaseCreate)
def create_case(case: CaseCreate) -> CaseCreate:
    for item in case.evidence:
        item.case_id = case.case_id
    CASES[case.case_id] = case
    return case


@app.post("/cases/{case_id}/query", response_model=QueryResponse)
def query_case(case_id: str, request: QueryRequest) -> QueryResponse:
    case = CASES.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return answer_question(request.question, case.evidence, request.top_k)


@app.get("/cases/{case_id}/contradictions")
def contradictions(case_id: str):
    case = CASES.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return {"findings": detect_contradictions(case.evidence)}


@app.get("/cases/{case_id}/missing-evidence", response_model=MissingEvidenceResponse)
def missing_evidence(case_id: str) -> MissingEvidenceResponse:
    case = CASES.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return check_missing_evidence(case.claim_type, case.evidence)


@app.get("/cases/{case_id}/report", response_model=Report)
def report(case_id: str) -> Report:
    case = CASES.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return build_report(case.case_id, case.title, case.claim_type, case.evidence)
