from fastapi.testclient import TestClient

from claimlens.api import main


def test_demo_eval_endpoint_returns_metrics() -> None:
    client = TestClient(main.app)

    response = client.get("/evals/demo")

    assert response.status_code == 200
    payload = response.json()
    assert payload["example_count"] >= 2
    assert 0 <= payload["pass_rate"] <= 1
    assert "average_citation_coverage" in payload
    assert payload["results"][0]["id"]
    assert payload["results"][0]["expected_citation_recall"] >= 0
