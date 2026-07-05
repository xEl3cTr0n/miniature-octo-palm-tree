from claimlens.core.cases import CaseStore
from claimlens.core.models import EvidenceItem, EvidenceType


def sample_evidence() -> list[EvidenceItem]:
    return [
        EvidenceItem(
            id="recall-1",
            type=EvidenceType.TEXT,
            title="NHTSA recall 20V771000",
            content="A BCM software issue may affect rear camera behavior and exterior lights.",
            metadata={"source": "nhtsa_recalls"},
        ),
        EvidenceItem(
            id="complaint-1",
            type=EvidenceType.TEXT,
            title="NHTSA complaint 11746974",
            content="Driver reports warning lights and intermittent rear camera failure.",
            metadata={"source": "nhtsa_complaints"},
        ),
    ]


def test_case_store_creates_and_lists_case_summaries() -> None:
    store = CaseStore()

    record = store.create_case(
        title="2020 Honda Accord warning lights",
        claim_type="vehicle_safety",
        evidence=sample_evidence(),
        source="nhtsa",
    )

    assert record.case_id.startswith("case-")
    assert record.evidence_count == 2
    assert record.source == "nhtsa"

    summaries = store.list_cases()
    assert len(summaries) == 1
    assert summaries[0].case_id == record.case_id
    assert summaries[0].title == "2020 Honda Accord warning lights"
    assert summaries[0].evidence_count == 2


def test_case_store_persists_cases_between_instances(tmp_path) -> None:
    database_path = tmp_path / "cases.sqlite3"
    first_store = CaseStore(database_path=database_path)
    record = first_store.create_case(
        title="2020 Honda Accord warning lights",
        claim_type="vehicle_safety",
        evidence=sample_evidence(),
        source="nhtsa",
    )

    reopened_store = CaseStore(database_path=database_path)
    reopened_record = reopened_store.get_case(record.case_id)

    assert reopened_record == record
    assert reopened_store.list_cases()[0].case_id == record.case_id


def test_case_store_deletes_case_from_persistent_store(tmp_path) -> None:
    database_path = tmp_path / "cases.sqlite3"
    store = CaseStore(database_path=database_path)
    record = store.create_case(
        title="2020 Honda Accord warning lights",
        claim_type="vehicle_safety",
        evidence=sample_evidence(),
        source="nhtsa",
    )

    store.delete_case(record.case_id)
    reopened_store = CaseStore(database_path=database_path)

    assert reopened_store.list_cases() == []


def test_case_store_answers_questions_from_stored_evidence() -> None:
    store = CaseStore()
    record = store.create_case(
        title="2020 Honda Accord warning lights",
        claim_type="vehicle_safety",
        evidence=sample_evidence(),
        source="nhtsa",
    )

    answer = store.ask_case(record.case_id, "Does evidence mention rear camera failure?")

    assert answer.confidence == 0.72
    assert answer.citations
    assert answer.missing_evidence == []


def test_case_store_builds_reviewer_report() -> None:
    store = CaseStore()
    record = store.create_case(
        title="2020 Honda Accord warning lights",
        claim_type="vehicle_safety",
        evidence=sample_evidence(),
        source="nhtsa",
    )

    report = store.build_report(record.case_id)

    assert report.case_id == record.case_id
    assert report.title == "2020 Honda Accord warning lights"
    assert report.summary.startswith("ClaimLens reviewed 2 evidence items")
    assert report.answer.confidence == 0.72
    assert report.next_steps == [
        "Review cited evidence before disposition.",
        "Request missing evidence if required items are absent.",
        "Escalate low-confidence or contradiction-heavy cases to a human reviewer.",
    ]


def test_case_store_exports_reviewer_report_markdown() -> None:
    store = CaseStore()
    record = store.create_case(
        title="2020 Honda Accord warning lights",
        claim_type="vehicle_safety",
        evidence=sample_evidence(),
        source="nhtsa",
    )

    markdown = store.build_report_markdown(record.case_id)

    assert markdown.startswith("# 2020 Honda Accord warning lights")
    assert f"Case ID: `{record.case_id}`" in markdown
    assert "## Citation-Backed Answer" in markdown
    assert "- NHTSA recall 20V771000#chunk-1" in markdown
    assert "## Reviewer Next Steps" in markdown
