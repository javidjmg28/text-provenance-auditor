from fastapi.testclient import TestClient

from text_provenance_auditor.web import create_app


def test_web_home_loads():
    client = TestClient(create_app())
    response = client.get("/")
    assert response.status_code == 200
    assert "Text Provenance Auditor V3" in response.text
    assert "Evidence, not guesses." in response.text


def test_web_text_scan_returns_v3_report(monkeypatch):
    monkeypatch.delenv("PROVENANCE_ANTHROPIC_VERIFIER_CMD", raising=False)
    client = TestClient(create_app())
    response = client.post(
        "/api/scan-text",
        json={"text": "hello\u200bworld", "provider": "anthropic", "include_segments": True},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["version"] == "0.3.0"
    assert payload["unicode_forensics"]["suspicious_count"] == 1
    assert payload["watermark_verification"]["status"] == "unavailable"


def test_web_rejects_empty_text():
    client = TestClient(create_app())
    response = client.post("/api/scan-text", json={"text": "   "})
    assert response.status_code == 400


def test_web_file_scan_uses_display_filename():
    client = TestClient(create_app())
    response = client.post(
        "/api/scan-file",
        files={"file": ("sample.txt", b"A plain local test document.", "text/plain")},
        data={"provider": "none", "include_segments": "true", "inspect_c2pa": "false"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["source"] == "sample.txt"
    assert payload["words"] == 5


def test_capabilities_advertise_web_ui():
    client = TestClient(create_app())
    payload = client.get("/api/capabilities").json()
    assert payload["version"] == "0.3.0"
    assert "local_web_ui" in payload["interfaces"]
