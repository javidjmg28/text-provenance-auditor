from __future__ import annotations

from .models import C2PAReport, EvidenceScores, EvidenceSummary, StylometryReport, UnicodeReport, WatermarkVerification


def build_evidence_summary(
    verification: WatermarkVerification,
    c2pa: C2PAReport,
    unicode_report: UnicodeReport,
    stylometry: StylometryReport,
) -> EvidenceSummary:
    provider_status = (
        "verified" if verification.verified is True else
        "not_verified" if verification.verified is False else
        verification.status
    )

    signed_status = c2pa.status
    forensic_count = unicode_report.suspicious_count + unicode_report.mixed_script_count
    forensic_status = "observed" if forensic_count else "none_observed"
    style_status = "weak_flags_present" if stylometry.flagged_signal_count else "metrics_only"

    if verification.verified is True:
        overall = "provider_verified"
        interpretation = "An authorised provider verifier returned a positive result. Treat this as strong provider-specific evidence, subject to the provider's stated limitations."
    elif c2pa.manifest_present and c2pa.validation_ok and c2pa.provider_hints:
        overall = "signed_provenance_with_provider_hint"
        interpretation = "A valid signed C2PA manifest is present and contains provider-related metadata. Inspect the manifest details before attributing authorship."
    elif c2pa.manifest_present and c2pa.validation_ok:
        overall = "signed_provenance_present"
        interpretation = "A valid signed C2PA manifest is present, but it does not by itself establish which model authored the extracted text."
    elif forensic_count:
        overall = "observable_forensics_only"
        interpretation = "Observable text anomalies were found. They may reflect formatting, steganography, copy/paste artefacts or legitimate typography and are not provider-watermark proof."
    elif stylometry.flagged_signal_count:
        overall = "heuristic_only"
        interpretation = "Only weak style regularities were observed. No provider-verifiable or signed provenance evidence was established."
    else:
        overall = "no_positive_evidence"
        interpretation = "No positive provenance evidence was established by the configured checks. Absence of evidence is not evidence of human authorship."

    return EvidenceSummary(
        overall_level=overall,
        provider_verification=provider_status,
        signed_file_provenance=signed_status,
        observable_text_forensics=forensic_status,
        style_heuristics=style_status,
        interpretation=interpretation,
    )


def build_evidence_scores(
    verification: WatermarkVerification,
    c2pa: C2PAReport,
    unicode_report: UnicodeReport,
    stylometry: StylometryReport,
) -> EvidenceScores:
    if verification.verified is True:
        provider_score: int | None = 100
    elif verification.verified is False:
        provider_score = 0
    else:
        provider_score = None

    if c2pa.status == "present_valid":
        signed_score: int | None = 100
    elif c2pa.status == "present_with_validation_warnings":
        signed_score = 55
    elif c2pa.status == "not_present":
        signed_score = 0
    else:
        signed_score = None

    severity_weights = {"high": 20, "medium": 8, "notice": 2}
    anomaly_score = sum(severity_weights.get(f.severity, 2) for f in unicode_report.findings)
    anomaly_score += unicode_report.mixed_script_count * 15
    if unicode_report.normalisation.nfc_changes:
        anomaly_score += 3
    if unicode_report.normalisation.nfkc_changes:
        anomaly_score += 5
    anomaly_score = min(100, anomaly_score)

    style_score = min(60, stylometry.flagged_signal_count * 15)

    return EvidenceScores(
        provider_evidence=provider_score,
        signed_provenance=signed_score,
        observable_text_anomalies=anomaly_score,
        style_heuristics=style_score,
    )
