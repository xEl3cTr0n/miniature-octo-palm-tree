from pathlib import Path

from claimlens_api.models import CaseCreate
from claimlens_api.pipeline import answer_question, check_missing_evidence, detect_contradictions


def load_case() -> CaseCreate:
    return CaseCreate.model_validate_json(Path("datasets/synthetic_claims/rear_end_collision_case_001/case.json").read_text())


def test_query_returns_citations_for_rear_bumper_damage():
    case = load_case()
    response = answer_question("Is rear bumper damage supported?", case.evidence)
    assert response.citations
    assert any("rear bumper" in citation.snippet.lower() for citation in response.citations)


def test_detects_date_and_damage_location_contradictions():
    case = load_case()
    findings = detect_contradictions(case.evidence)
    summaries = " ".join(f.summary for f in findings).lower()
    assert "multiple incident dates" in summaries
    assert "damage location differs" in summaries


def test_missing_evidence_lists_unmet_requirements():
    case = load_case()
    missing = check_missing_evidence(case.claim_type, case.evidence)
    assert "signed claimant statement" in missing.missing_required
    assert "repair estimate" in missing.present_required
