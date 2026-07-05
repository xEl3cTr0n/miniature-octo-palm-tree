from claimlens.core.models import EvidenceType
from claimlens.core.pipeline import answer_claim
from claimlens.data_sources import nhtsa
from claimlens.data_sources.nhtsa import build_vehicle_evidence


def test_nhtsa_records_become_citable_text_evidence() -> None:
    evidence = build_vehicle_evidence(
        make="Honda",
        model="Accord",
        year=2020,
        complaints=[
            {
                "odiNumber": 11746974,
                "manufacturer": "Honda (American Honda Motor Co.)",
                "dateOfIncident": "06/26/2026",
                "dateComplaintFiled": "06/28/2026",
                "components": "ELECTRICAL SYSTEM",
                "summary": "Dashboard warning lights stay on and the rear camera intermittently fails.",
            }
        ],
        recalls=[
            {
                "NHTSACampaignNumber": "20V771000",
                "ReportReceivedDate": "10/12/2020",
                "Component": "ELECTRICAL SYSTEM:BODY CONTROL MODULE:SOFTWARE",
                "Summary": "A BCM software error may disrupt the rearview camera and exterior lights.",
                "Consequence": "Malfunctioning vehicle systems can increase crash risk.",
                "Remedy": "Dealers will update the BCM software.",
            }
        ],
    )

    assert [item.id for item in evidence] == [
        "nhtsa-complaint-11746974",
        "nhtsa-recall-20V771000",
    ]
    assert evidence[0].type is EvidenceType.TEXT
    assert "dashboard warning lights" in evidence[0].content.lower()
    assert evidence[0].metadata["source"] == "nhtsa_complaints"
    assert evidence[1].metadata["source"] == "nhtsa_recalls"


def test_claim_answer_uses_nhtsa_evidence_without_missing_data_penalty() -> None:
    evidence = build_vehicle_evidence(
        make="Honda",
        model="Accord",
        year=2020,
        complaints=[
            {
                "odiNumber": 11746974,
                "components": "ELECTRICAL SYSTEM",
                "summary": "Dashboard warning lights stay on and the rear camera intermittently fails.",
            }
        ],
        recalls=[
            {
                "NHTSACampaignNumber": "20V771000",
                "Component": "ELECTRICAL SYSTEM:BODY CONTROL MODULE:SOFTWARE",
                "Summary": "A BCM software error may disrupt the rearview camera and exterior lights.",
            }
        ],
    )

    answer = answer_claim(
        "Do any complaints or recalls mention warning lights or rear camera failure?",
        evidence,
        claim_type="vehicle_safety",
    )

    assert answer.confidence == 0.72
    assert answer.citations
    assert any("NHTSA recall 20V771000" in citation for citation in answer.citations)
    assert answer.missing_evidence == []


def test_nhtsa_fetch_uses_explicit_tls_context(monkeypatch) -> None:
    captured = {}

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self) -> bytes:
            return b'{"results": []}'

    def fake_urlopen(url, *, timeout, context):
        captured["url"] = url
        captured["timeout"] = timeout
        captured["context"] = context
        return FakeResponse()

    monkeypatch.setattr(nhtsa, "urlopen", fake_urlopen)

    results = nhtsa._fetch_results(
        nhtsa.NHTSA_COMPLAINTS_URL,
        {"make": "Honda", "model": "Accord", "modelYear": "2020"},
        timeout_seconds=3.0,
    )

    assert results == []
    assert captured["timeout"] == 3.0
    assert captured["context"] is not None
