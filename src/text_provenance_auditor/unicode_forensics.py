from __future__ import annotations

import re
import unicodedata
from collections import Counter

from .models import MixedScriptFinding, NormalisationReport, UnicodeFinding, UnicodeReport


ZERO_WIDTH = {
    "\u200b",  # ZERO WIDTH SPACE
    "\u200c",  # ZERO WIDTH NON-JOINER
    "\u200d",  # ZERO WIDTH JOINER
    "\u2060",  # WORD JOINER
    "\ufeff",  # ZERO WIDTH NO-BREAK SPACE / BOM
}

BIDI_CONTROLS = {
    "\u061c",  # ARABIC LETTER MARK
    "\u200e", "\u200f",  # LRM / RLM
    "\u202a", "\u202b", "\u202c", "\u202d", "\u202e",
    "\u2066", "\u2067", "\u2068", "\u2069",
}

INVISIBLE_OPERATORS = {"\u2061", "\u2062", "\u2063", "\u2064"}
UNUSUAL_SPACES = {
    "\u00a0", "\u1680", "\u180e", "\u2000", "\u2001", "\u2002", "\u2003",
    "\u2004", "\u2005", "\u2006", "\u2007", "\u2008", "\u2009", "\u200a",
    "\u202f", "\u205f", "\u3000",
}

TOKEN_RE = re.compile(r"[^\W\d_]+", re.UNICODE)


def _context(text: str, index: int, radius: int = 14) -> str:
    start = max(0, index - radius)
    end = min(len(text), index + radius + 1)
    return text[start:end].encode("unicode_escape").decode("ascii")


def _char_family(char: str) -> tuple[str | None, str]:
    cp = ord(char)
    category = unicodedata.category(char)

    if char in ZERO_WIDTH:
        return "zero_width", "high"
    if char in BIDI_CONTROLS:
        return "bidi_control", "high"
    if char in INVISIBLE_OPERATORS:
        return "invisible_operator", "high"
    if char == "\u00ad":
        return "soft_hyphen", "medium"
    if 0xFE00 <= cp <= 0xFE0F or 0xE0100 <= cp <= 0xE01EF:
        return "variation_selector", "medium"
    if 0xE0000 <= cp <= 0xE007F:
        return "unicode_tag", "high"
    if char in UNUSUAL_SPACES:
        return "unusual_space", "notice"
    if category == "Cf":
        return "format_control", "medium"
    return None, "notice"


def _script(char: str) -> str | None:
    if not char.isalpha():
        return None
    name = unicodedata.name(char, "")
    for script in ("LATIN", "CYRILLIC", "GREEK", "ARABIC", "HEBREW", "DEVANAGARI"):
        if script in name:
            return script.title()
    return "Other"


def _normalisation_delta(text: str, form: str) -> tuple[bool, int]:
    normalised = unicodedata.normalize(form, text)
    if normalised == text:
        return False, 0
    max_len = max(len(text), len(normalised))
    delta = sum(
        1
        for i in range(max_len)
        if (text[i] if i < len(text) else None) != (normalised[i] if i < len(normalised) else None)
    )
    return True, delta


def scan_unicode(text: str) -> UnicodeReport:
    findings: list[UnicodeFinding] = []
    family_counts: Counter[str] = Counter()

    for i, char in enumerate(text):
        family, severity = _char_family(char)
        if family is None:
            continue
        family_counts[family] += 1
        findings.append(
            UnicodeFinding(
                index=i,
                codepoint=f"U+{ord(char):04X}",
                name=unicodedata.name(char, "UNKNOWN"),
                category=unicodedata.category(char),
                escaped=char.encode("unicode_escape").decode("ascii"),
                context=_context(text, i),
                family=family,
                severity=severity,
            )
        )

    mixed: list[MixedScriptFinding] = []
    for match in TOKEN_RE.finditer(text):
        token = match.group(0)
        scripts = sorted({s for c in token if (s := _script(c)) not in {None, "Other"}})
        if len(scripts) >= 2:
            mixed.append(
                MixedScriptFinding(
                    token=token,
                    scripts=scripts,
                    index=match.start(),
                    context=_context(text, match.start()),
                )
            )

    nfc_changes, nfc_delta = _normalisation_delta(text, "NFC")
    nfkc_changes, nfkc_delta = _normalisation_delta(text, "NFKC")

    return UnicodeReport(
        suspicious_count=len(findings),
        findings=findings,
        mixed_script_count=len(mixed),
        mixed_script_findings=mixed,
        families=dict(family_counts),
        normalisation=NormalisationReport(
            nfc_changes=nfc_changes,
            nfkc_changes=nfkc_changes,
            nfc_delta_chars=nfc_delta,
            nfkc_delta_chars=nfkc_delta,
        ),
    )
