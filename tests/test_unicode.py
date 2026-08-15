from text_provenance_auditor.unicode_forensics import scan_unicode


def test_zero_width_space_is_reported():
    report = scan_unicode("hello\u200bworld")
    assert report.suspicious_count == 1
    assert report.findings[0].codepoint == "U+200B"
    assert report.findings[0].family == "zero_width"


def test_bidi_override_is_high_severity():
    report = scan_unicode("abc\u202edef")
    assert report.findings[0].family == "bidi_control"
    assert report.findings[0].severity == "high"


def test_variation_selector_is_reported():
    report = scan_unicode("A\ufe0f")
    assert report.suspicious_count == 1
    assert report.findings[0].family == "variation_selector"


def test_mixed_latin_cyrillic_token_is_reported():
    report = scan_unicode("pаypal")  # second character is Cyrillic small a
    assert report.mixed_script_count == 1
    assert set(report.mixed_script_findings[0].scripts) == {"Cyrillic", "Latin"}


def test_plain_text_has_no_unicode_findings():
    report = scan_unicode("hello world")
    assert report.suspicious_count == 0
    assert report.mixed_script_count == 0
