from text_provenance_auditor.audit import audit_text


def test_anthropic_is_explicitly_unavailable_without_authorised_verifier(monkeypatch):
    monkeypatch.delenv("PROVENANCE_ANTHROPIC_VERIFIER_CMD", raising=False)
    report = audit_text("A sufficiently ordinary paragraph for testing purposes.")
    assert report.watermark_verification.provider == "anthropic"
    assert report.watermark_verification.status == "unavailable"
    assert report.watermark_verification.verified is None


def test_google_is_explicitly_unavailable_without_authorised_verifier(monkeypatch):
    monkeypatch.delenv("PROVENANCE_GOOGLE_SYNTHID_VERIFIER_CMD", raising=False)
    report = audit_text("A sufficiently ordinary paragraph for testing purposes.", provider="google")
    assert report.watermark_verification.provider == "google"
    assert report.watermark_verification.status == "unavailable"


def test_heuristics_are_labelled_non_proof():
    report = audit_text("This isn't just a test, it's a deliberately patterned sentence.")
    assert report.stylometry.classification == "heuristic_only"


def test_raw_text_has_no_c2pa_claim():
    report = audit_text("Plain pasted text.")
    assert report.c2pa.status == "not_applicable"
