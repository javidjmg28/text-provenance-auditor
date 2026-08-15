from __future__ import annotations

import math
import re
from collections import Counter

from .models import StylometryReport, StylometrySignal


WORD_RE = re.compile(r"\b[\w'-]+\b", re.UNICODE)
SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")

# These patterns are intentionally generic. They are not fingerprints of any model.
PATTERNS = {
    "contrast_formula": re.compile(r"\bthis (?:isn't|is not)\b.{0,80}\bit(?:'s| is)\b", re.I | re.S),
    "not_just_but": re.compile(r"\bnot just\b.{0,100}\bbut\b", re.I | re.S),
    "in_other_words": re.compile(r"\bin other words\b", re.I),
}


def _safe_cv(values: list[int]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    if mean == 0:
        return 0.0
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    return math.sqrt(variance) / mean


def analyse_stylometry(text: str) -> StylometryReport:
    words = WORD_RE.findall(text)
    sentences = [s.strip() for s in SENTENCE_RE.split(text.strip()) if s.strip()]
    lower_words = [w.lower() for w in words]

    signals: list[StylometrySignal] = []
    flagged = 0

    if words:
        type_token_ratio = len(set(lower_words)) / len(lower_words)
        signals.append(
            StylometrySignal(
                name="type_token_ratio",
                value=round(type_token_ratio, 4),
                interpretation="Vocabulary diversity metric only; not an AI or watermark test.",
                kind="metric",
            )
        )

    sentence_lengths = [len(WORD_RE.findall(s)) for s in sentences]
    if sentence_lengths:
        cv = _safe_cv(sentence_lengths)
        signals.append(
            StylometrySignal(
                name="sentence_length_cv",
                value=round(cv, 4),
                interpretation="Variation in sentence length; both human and AI writing span the full range.",
                kind="metric",
            )
        )
        if len(sentences) >= 8 and cv < 0.18:
            flagged += 1
            signals.append(
                StylometrySignal(
                    name="unusually_uniform_sentence_lengths",
                    value=round(cv, 4),
                    interpretation="Weak regularity signal only. Highly edited human prose can look equally uniform.",
                    kind="weak_flag",
                )
            )

    for name, pattern in PATTERNS.items():
        count = len(pattern.findall(text))
        if count >= 2:
            flagged += 1
            signals.append(
                StylometrySignal(
                    name=name,
                    value=count,
                    interpretation="Repeated rhetorical construction. This is a weak style observation, not provenance evidence.",
                    kind="weak_flag",
                )
            )

    if len(lower_words) >= 3:
        trigrams = Counter(zip(lower_words, lower_words[1:], lower_words[2:]))
        repeated_types = sum(1 for _, c in trigrams.items() if c >= 2)
        signals.append(
            StylometrySignal(
                name="repeated_trigram_types",
                value=repeated_types,
                interpretation="Counts repeated three-word sequences; repetition alone does not identify authorship.",
                kind="metric",
            )
        )
        trigram_total = max(1, len(lower_words) - 2)
        repeated_ratio = sum(c - 1 for c in trigrams.values() if c >= 2) / trigram_total
        if len(lower_words) >= 120 and repeated_ratio > 0.08:
            flagged += 1
            signals.append(
                StylometrySignal(
                    name="elevated_repeated_trigram_ratio",
                    value=round(repeated_ratio, 4),
                    interpretation="Weak repetition signal. Templates, legal writing and technical documents can trigger it.",
                    kind="weak_flag",
                )
            )

    return StylometryReport(
        token_count=len(words),
        sentence_count=len(sentences),
        signals=signals,
        flagged_signal_count=flagged,
    )
