from claimlens.core.cases import CaseStore
from claimlens.demo_cases import build_demo_case


def test_build_demo_case_returns_portfolio_safe_fixture() -> None:
    demo_case = build_demo_case()

    assert demo_case.title == "Demo: 2020 Honda Accord evidence review"
    assert demo_case.claim_type == "vehicle_safety"
    assert demo_case.source == "demo_fixture"
    assert [item.id for item in demo_case.evidence] == [
        "demo-adjuster-note",
        "demo-nhtsa-recall-20v771000",
        "demo-owner-complaint",
    ]
    assert all(item.metadata["source"] == "demo_fixture" for item in demo_case.evidence)


def test_demo_case_can_generate_citation_backed_report() -> None:
    demo_case = build_demo_case()
    store = CaseStore()
    record = store.create_case(
        title=demo_case.title,
        claim_type=demo_case.claim_type,
        evidence=demo_case.evidence,
        source=demo_case.source,
    )

    report = store.build_report(record.case_id)

    assert report.title == demo_case.title
    assert report.evidence_count == 3
    assert report.answer.citations
