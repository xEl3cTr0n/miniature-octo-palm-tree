from __future__ import annotations

import re
from collections import Counter

from .models import Citation, EvidenceItem, Finding, MissingEvidenceResponse, QueryResponse, Report

REQUIRED_EVIDENCE: dict[str, set[str]] = {
    "auto_collision": {
        "policy document",
        "claim intake form",
        "photos of claimed damage",
        "repair estimate",
        "incident date",
        "signed claimant statement",
    }
}

KEYWORD_SYNONYMS = {
    "rear bumper": {"rear bumper", "bumper", "rear-end", "rear impact"},
    "policy": {"policy", "coverage", "deductible", "exclusion"},
    "damage": {"damage", "dent", "deformation", "repair", "replace"},
}


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def expanded_terms(question: str) -> set[str]:
    terms = set(tokenize(question))
    lower = question.lower()
    for phrase, synonyms in KEYWORD_SYNONYMS.items():
        if phrase in lower:
            terms.update(tokenize(" ".join(synonyms)))
    return terms


def score_evidence(question: str, item: EvidenceItem) -> float:
    q_terms = expanded_terms(question)
    if not q_terms:
        return 0.0
    content_terms = Counter(tokenize(f"{item.title} {item.content} {' '.join(item.metadata.values())}"))
    overlap = sum(content_terms[t] for t in q_terms)
    return min(1.0, overlap / max(4, len(q_terms)))


def retrieve(question: str, evidence: list[EvidenceItem], top_k: int = 5) -> list[Citation]:
    ranked = sorted(
        ((score_evidence(question, item), item) for item in evidence),
        key=lambda pair: pair[0],
        reverse=True,
    )
    citations: list[Citation] = []
    for score, item in ranked[:top_k]:
        if score <= 0:
            continue
        citations.append(
            Citation(
                evidence_id=item.id,
                title=item.title,
                snippet=item.content[:240].strip(),
                relevance_score=round(score, 2),
            )
        )
    return citations


def answer_question(question: str, evidence: list[EvidenceItem], top_k: int = 5) -> QueryResponse:
    citations = retrieve(question, evidence, top_k)
    if not citations:
        return QueryResponse(
            answer="I could not find enough grounded evidence to answer this question.",
            confidence="low",
            citations=[],
            recommended_action="Upload additional evidence or refine the question.",
        )

    confidence = "high" if len(citations) >= 3 and citations[0].relevance_score >= 0.7 else "medium"
    answer = (
        "The available evidence partially supports the claim. "
        "Review the cited artifacts together because ClaimLens found related details across the case packet."
    )
    return QueryResponse(
        answer=answer,
        confidence=confidence,
        citations=citations,
        recommended_action="Have a reviewer validate the cited sources and resolve any contradiction findings before final disposition.",
    )


def detect_contradictions(evidence: list[EvidenceItem]) -> list[Finding]:
    findings: list[Finding] = []
    date_mentions: dict[str, list[str]] = {}
    damage_mentions: dict[str, list[str]] = {}

    for item in evidence:
        for date in re.findall(r"\b(?:June|July|August|September)\s+\d{1,2}\b", item.content, flags=re.I):
            date_mentions.setdefault(date.lower(), []).append(item.id)
        lower = item.content.lower()
        if "front passenger" in lower:
            damage_mentions.setdefault("front passenger", []).append(item.id)
        if "rear bumper" in lower or "rear-end" in lower or "rear impact" in lower:
            damage_mentions.setdefault("rear bumper", []).append(item.id)

    if len(date_mentions) > 1:
        findings.append(
            Finding(
                severity="medium",
                summary=f"Multiple incident dates were found: {', '.join(sorted(date_mentions))}.",
                evidence_ids=sorted({eid for ids in date_mentions.values() for eid in ids}),
            )
        )
    if {"front passenger", "rear bumper"}.issubset(damage_mentions):
        findings.append(
            Finding(
                severity="high",
                summary="Damage location differs across evidence: front passenger-side damage and rear bumper damage are both mentioned.",
                evidence_ids=sorted({eid for ids in damage_mentions.values() for eid in ids}),
            )
        )
    return findings


def check_missing_evidence(claim_type: str, evidence: list[EvidenceItem]) -> MissingEvidenceResponse:
    required = REQUIRED_EVIDENCE.get(claim_type, set())
    text = "\n".join(f"{item.title} {item.content} {' '.join(item.metadata.values())}" for item in evidence).lower()
    present = sorted(req for req in required if all(token in text for token in tokenize(req)))
    missing = sorted(required - set(present))
    return MissingEvidenceResponse(claim_type=claim_type, missing_required=missing, present_required=present)


def build_report(case_id: str, title: str, claim_type: str, evidence: list[EvidenceItem]) -> Report:
    query = answer_question("Is the claimed rear bumper damage supported by the evidence?", evidence)
    contradictions = detect_contradictions(evidence)
    missing = check_missing_evidence(claim_type, evidence)
    return Report(
        case_id=case_id,
        title=title,
        executive_summary=(
            "ClaimLens found supporting evidence for the rear bumper claim, but the case should be reviewed "
            "because contradiction and missing-evidence checks may affect final disposition."
        ),
        key_evidence=query.citations,
        contradictions=contradictions,
        missing_evidence=missing,
        reviewer_next_steps=[
            "Resolve any conflicting incident dates or damage locations.",
            "Request missing required artifacts before final approval.",
            "Validate cited evidence snippets against the original source files.",
        ],
    )
