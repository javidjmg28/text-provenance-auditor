import json
import sys

from text_provenance_auditor.audit import audit_text


def test_authorised_external_verifier_contract(tmp_path, monkeypatch):
    verifier = tmp_path / "verifier.py"
    verifier.write_text(
        "import json,sys\n"
        "_ = sys.stdin.read()\n"
        "print(json.dumps({'verified': True, 'score': 0.91, 'reason': 'test verifier'}))\n",
        encoding="utf-8",
    )
    monkeypatch.setenv(
        "PROVENANCE_ANTHROPIC_VERIFIER_CMD",
        f'"{sys.executable}" "{verifier}"',
    )
    report = audit_text("Candidate text for authorised verification.", provider="anthropic")
    assert report.watermark_verification.verified is True
    assert report.watermark_verification.score == 0.91
    assert report.evidence_summary.overall_level == "provider_verified"
    assert report.evidence_scores.provider_evidence == 100
