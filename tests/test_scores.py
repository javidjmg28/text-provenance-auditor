from text_provenance_auditor.audit import audit_text


def test_scores_are_separate_not_combined():
    report = audit_text("hello\u200bworld")
    assert report.evidence_scores is not None
    assert report.evidence_scores.provider_evidence is None
    assert report.evidence_scores.observable_text_anomalies > 0
    assert "must not be added" in report.evidence_scores.note
