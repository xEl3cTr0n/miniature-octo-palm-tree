from fastapi.testclient import TestClient

from claimlens.api import main


def test_dashboard_root_serves_reviewer_console() -> None:
    client = TestClient(main.app)

    response = client.get("/")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    html = response.text
    assert "ClaimLens" in html
    assert "Import NHTSA Case" in html
    assert "Case Queue" in html
    assert "Ask Reviewer Question" in html
    assert "Reviewer Report" in html


def test_dashboard_targets_case_workspace_endpoints() -> None:
    client = TestClient(main.app)

    html = client.get("/").text

    assert 'requestJson("/cases/import/nhtsa"' in html
    assert 'requestJson("/cases")' in html
    assert 'requestJson(`/cases/${selectedCaseId}/ask`' in html
    assert 'requestJson(`/cases/${selectedCaseId}/report`' in html
