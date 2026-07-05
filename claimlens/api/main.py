from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from claimlens.core.pipeline import answer_claim
from claimlens.core.models import ClaimAnswer, EvidenceItem, EvidenceType
from claimlens.data_sources.nhtsa import (
    NHTSADataSourceError,
    evidence_to_dict,
    fetch_vehicle_evidence,
)

app = FastAPI(title="ClaimLens", version="0.1.0")


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


class NHTSAAskRequest(BaseModel):
    make: str = "Honda"
    model: str = "Accord"
    year: int = 2020
    question: str = "Do complaints or recalls mention warning lights or rear camera failure?"
    max_complaints: int = Field(default=10, ge=1, le=50)
    max_recalls: int = Field(default=5, ge=1, le=20)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ask", response_model=ClaimAnswer)
def ask(request: AskRequest) -> ClaimAnswer:
    evidence = [EvidenceItem(**item.model_dump()) for item in request.evidence]
    return answer_claim(request.question, evidence, claim_type=request.claim_type)


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
