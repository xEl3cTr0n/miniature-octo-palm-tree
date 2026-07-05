from fastapi.testclient import TestClient

from claimlens.api import main
from claimlens.core.models import EvidenceItem, EvidenceType


def test_ask_nhtsa_endpoint_answers_with_mocked_evidence(monkeypatch) -> None:
    def fake_fetch_vehicle_evidence(**kwargs):
        assert kwargs["make"] == "Honda"
        assert kwargs["model"] == "Accord"
        assert kwargs["year"] == 2020
        return [
            EvidenceItem(
                id="nhtsa-recall-20V771000",
                type=EvidenceType.TEXT,
                title="NHTSA recall 20V771000: electrical system",
                content="NHTSA recall 20V771000 says a BCM issue may affect rear camera behavior.",
                metadata={"source": "nhtsa_recalls"},
            )
        ]

    monkeypatch.setattr(main, "fetch_vehicle_evidence", fake_fetch_vehicle_evidence)
    client = TestClient(main.app)

    response = client.post(
        "/ask/nhtsa",
        json={
            "make": "Honda",
            "model": "Accord",
            "year": 2020,
            "question": "Does a recall mention rear camera behavior?",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["confidence"] == 0.72
    assert payload["citations"] == ["NHTSA recall 20V771000: electrical system#chunk-1"]
