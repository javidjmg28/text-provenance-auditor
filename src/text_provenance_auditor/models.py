from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class UnicodeFinding:
    index: int
    codepoint: str
    name: str
    category: str
    escaped: str
    context: str
    family: str = "format_control"
    severity: str = "notice"


@dataclass
class MixedScriptFinding:
    token: str
    scripts: list[str]
    index: int
    context: str


@dataclass
class NormalisationReport:
    nfc_changes: bool = False
    nfkc_changes: bool = False
    nfc_delta_chars: int = 0
    nfkc_delta_chars: int = 0
    note: str = (
        "Unicode normalisation differences can be legitimate typography. They are reported as forensic observations, not provenance proof."
    )


@dataclass
class UnicodeReport:
    suspicious_count: int
    findings: list[UnicodeFinding] = field(default_factory=list)
    mixed_script_count: int = 0
    mixed_script_findings: list[MixedScriptFinding] = field(default_factory=list)
    families: dict[str, int] = field(default_factory=dict)
    normalisation: NormalisationReport = field(default_factory=NormalisationReport)
    note: str = (
        "Observable Unicode artefacts can reveal hidden or unusual text channels, but they are not equivalent to provider watermarks."
    )


@dataclass
class StylometrySignal:
    name: str
    value: Any
    interpretation: str
    kind: str = "metric"


@dataclass
class StylometryReport:
    classification: str = "heuristic_only"
    token_count: int = 0
    sentence_count: int = 0
    signals: list[StylometrySignal] = field(default_factory=list)
    flagged_signal_count: int = 0
    note: str = (
        "Stylometry describes writing patterns. It is not a provider watermark detector and cannot prove AI authorship."
    )


@dataclass
class WatermarkVerification:
    provider: str
    status: str
    verified: bool | None
    score: float | None = None
    reason: str | None = None
    method: str | None = None
    evidence_level: str = "unavailable"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class C2PAReport:
    status: str = "not_checked"
    manifest_present: bool | None = None
    validation_ok: bool | None = None
    active_manifest: str | None = None
    claim_generator: str | None = None
    digital_source_types: list[str] = field(default_factory=list)
    assertion_labels: list[str] = field(default_factory=list)
    provider_hints: list[str] = field(default_factory=list)
    validation_status: list[Any] = field(default_factory=list)
    backend: str | None = None
    reason: str | None = None
    note: str = (
        "C2PA can provide signed, tamper-evident provenance for supported assets. A valid manifest is evidence about an asset history, not proof that every word was originally authored by a named model."
    )


@dataclass
class SegmentReport:
    index: int
    char_start: int
    char_end: int
    word_count: int
    unicode_suspicious_count: int
    mixed_script_count: int
    stylometry_flagged_signal_count: int


@dataclass
class EvidenceScores:
    provider_evidence: int | None
    signed_provenance: int | None
    observable_text_anomalies: int
    style_heuristics: int
    note: str = (
        "Scores describe strength within separate evidence channels. They must not be added together or interpreted as an AI-authorship probability."
    )


@dataclass
class EvidenceSummary:
    overall_level: str
    provider_verification: str
    signed_file_provenance: str
    observable_text_forensics: str
    style_heuristics: str
    interpretation: str
    note: str = (
        "This is an evidence-strength classification, not a probability that text was AI-generated."
    )


@dataclass
class AuditReport:
    source: str
    chars: int
    words: int
    watermark_verification: WatermarkVerification
    unicode_forensics: UnicodeReport
    stylometry: StylometryReport
    c2pa: C2PAReport = field(default_factory=C2PAReport)
    segments: list[SegmentReport] = field(default_factory=list)
    evidence_summary: EvidenceSummary | None = None
    evidence_scores: EvidenceScores | None = None
    limitations: list[str] = field(default_factory=list)
    version: str = "0.3.0"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
