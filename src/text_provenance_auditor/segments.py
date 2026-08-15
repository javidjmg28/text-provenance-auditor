from __future__ import annotations

import re

from .models import SegmentReport
from .stylometry import analyse_stylometry
from .unicode_forensics import scan_unicode


WORD_RE = re.compile(r"\b[\w'-]+\b", re.UNICODE)


def _word_spans(text: str):
    return list(WORD_RE.finditer(text))


def analyse_segments(text: str, target_words: int = 400) -> list[SegmentReport]:
    if target_words < 50:
        raise ValueError("target_words must be at least 50")
    spans = _word_spans(text)
    if not spans:
        return []

    reports: list[SegmentReport] = []
    for idx, start_word in enumerate(range(0, len(spans), target_words)):
        end_word = min(len(spans), start_word + target_words)
        char_start = spans[start_word].start()
        char_end = spans[end_word - 1].end()
        chunk = text[char_start:char_end]
        unicode_report = scan_unicode(chunk)
        stylometry = analyse_stylometry(chunk)
        reports.append(
            SegmentReport(
                index=idx,
                char_start=char_start,
                char_end=char_end,
                word_count=end_word - start_word,
                unicode_suspicious_count=unicode_report.suspicious_count,
                mixed_script_count=unicode_report.mixed_script_count,
                stylometry_flagged_signal_count=stylometry.flagged_signal_count,
            )
        )
    return reports
