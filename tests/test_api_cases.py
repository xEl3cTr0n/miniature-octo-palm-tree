from fastapi.testclient import TestClient

from claimlens.api import main
from claimlens.core.models import EvidenceItem, EvidenceType


def fresh_client() -> TestClient:
    main.case_store = main.CaseStore()
    return TestClient(main.app)


def test_case_api_creates_lists_asks_and_reports() -> None:
    client = fresh_client()

    create_response = client.post(
        "/cases",
        json={
            "title": "2020 Honda Accord warning lights",
            "claim_type": "vehicle_safety",
            "source": "manual",
            "evidence": [
                {
                    "id": "recall-1",
                    "type": "text",
                    "title": "NHTSA recall 20V771000",
                    "content": "A BCM software issue may affect rear camera behavior.",
                    "metadata": {"source": "nhtsa_recalls"},
                }
            ],
        },
    )

    assert create_response.status_code == 200
    created = create_response.json()
    assert created["case_id"].startswith("case-")
    assert created["evidence_count"] == 1

    list_response = client.get("/cases")
    assert list_response.status_code == 200
    assert list_response.json()[0]["case_id"] == created["case_id"]

    ask_response = client.post(
        f"/cases/{created['case_id']}/ask",
        json={"question": "Does the evidence mention rear camera behavior?"},
    )
    assert ask_response.status_code == 200
    assert ask_response.json()["citations"] == ["NHTSA recall 20V771000#chunk-1"]

    report_response = client.get(f"/cases/{created['case_id']}/report")
    assert report_response.status_code == 200
    report = report_response.json()
    assert report["case_id"] == created["case_id"]
    assert report["answer"]["confidence"] == 0.72

    markdown_response = client.get(f"/cases/{created['case_id']}/report.md")
    assert markdown_response.status_code == 200
    assert markdown_response.headers["content-type"].startswith("text/markdown")
    assert "# 2020 Honda Accord warning lights" in markdown_response.text
    assert "## Citation-Backed Answer" in markdown_response.text


def test_case_api_deletes_case() -> None:
    client = fresh_client()
    create_response = client.post(
        "/cases",
        json={
            "title": "Delete me",
            "claim_type": "vehicle_safety",
            "source": "manual",
            "evidence": [
                {
                    "id": "recall-1",
                    "type": "text",
                    "title": "NHTSA recall 20V771000",
                    "content": "A BCM software issue may affect rear camera behavior.",
                    "metadata": {"source": "nhtsa_recalls"},
                }
            ],
        },
    )
    case_id = create_response.json()["case_id"]

    delete_response = client.delete(f"/cases/{case_id}")

    assert delete_response.status_code == 200
    assert delete_response.json() == {"case_id": case_id, "deleted": True}
    assert client.get(f"/cases/{case_id}").status_code == 404
    assert client.get("/cases").json() == []


def test_case_api_uses_configured_database_between_store_instances(
    monkeypatch, tmp_path
) -> None:
    monkeypatch.setenv("CLAIMLENS_CASE_DB", str(tmp_path / "api-cases.sqlite3"))
    main.case_store = main.build_case_store()
    client = TestClient(main.app)

    create_response = client.post(
        "/cases",
        json={
            "title": "Persistent Honda Accord review",
            "claim_type": "vehicle_safety",
            "source": "manual",
            "evidence": [
                {
                    "id": "recall-1",
                    "type": "text",
                    "title": "NHTSA recall 20V771000",
                    "content": "A BCM software issue may affect rear camera behavior.",
                    "metadata": {"source": "nhtsa_recalls"},
                }
            ],
        },
    )
    created = create_response.json()

    main.case_store = main.build_case_store()
    reopened_client = TestClient(main.app)
    list_response = reopened_client.get("/cases")

    assert list_response.status_code == 200
    assert list_response.json()[0]["case_id"] == created["case_id"]


def test_case_api_imports_nhtsa_case_with_mocked_evidence(monkeypatch) -> None:
    client = fresh_client()

    def fake_fetch_vehicle_evidence(**kwargs):
        assert kwargs["make"] == "Honda"
        assert kwargs["model"] == "Accord"
        assert kwargs["year"] == 2020
        return [
            EvidenceItem(
                id="nhtsa-recall-20V771000",
                type=EvidenceType.TEXT,
                title="NHTSA recall 20V771000",
                content="A BCM software issue may affect rear camera behavior.",
                metadata={"source": "nhtsa_recalls"},
            )
        ]

    monkeypatch.setattr(main, "fetch_vehicle_evidence", fake_fetch_vehicle_evidence)

    response = client.post(
        "/cases/import/nhtsa",
        json={
            "make": "Honda",
            "model": "Accord",
            "year": 2020,
            "max_complaints": 2,
            "max_recalls": 1,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["title"] == "2020 Honda Accord NHTSA safety review"
    assert payload["claim_type"] == "vehicle_safety"
    assert payload["source"] == "nhtsa"
    assert payload["evidence_count"] == 1


def test_case_api_seeds_deterministic_demo_case() -> None:
    client = fresh_client()

    response = client.post("/cases/demo")

    assert response.status_code == 200
    payload = response.json()
    assert payload["title"] == "Demo: 2020 Honda Accord evidence review"
    assert payload["claim_type"] == "vehicle_safety"
    assert payload["source"] == "demo_fixture"
    assert payload["evidence_count"] == 3
    assert [item["id"] for item in payload["evidence"]] == [
        "demo-adjuster-note",
        "demo-nhtsa-recall-20v771000",
        "demo-owner-complaint",
    ]

    list_response = client.get("/cases")

    assert list_response.status_code == 200
    assert list_response.json()[0]["case_id"] == payload["case_id"]


def test_case_api_exports_and_imports_json_case_bundle() -> None:
    client = fresh_client()
    created = client.post("/cases/demo").json()

    export_response = client.get(f"/cases/{created['case_id']}/bundle.json")

    assert export_response.status_code == 200
    bundle = export_response.json()
    assert bundle["schema_version"] == "claimlens.case_bundle.v1"
    assert bundle["exported_case_id"] == created["case_id"]
    assert bundle["title"] == created["title"]
    assert bundle["claim_type"] == "vehicle_safety"
    assert bundle["source"] == "demo_fixture"
    assert [item["id"] for item in bundle["evidence"]] == [
        "demo-adjuster-note",
        "demo-nhtsa-recall-20v771000",
        "demo-owner-complaint",
    ]

    import_response = client.post("/cases/import/bundle", json=bundle)

    assert import_response.status_code == 200
    imported = import_response.json()
    assert imported["case_id"] != created["case_id"]
    assert imported["title"] == created["title"]
    assert imported["source"] == "demo_fixture"
    assert imported["evidence_count"] == 3
    assert [case["case_id"] for case in client.get("/cases").json()] == [
        imported["case_id"],
        created["case_id"],
    ]
