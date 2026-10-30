from app.detectors.unicode_detector import detect_unicode


def test_detects_zero_width_space():
    findings = detect_unicode("Hello\u200bWorld")
    assert len(findings) == 1
    assert findings[0]["character"] == "U+200B"


def test_normal_text_has_no_findings():
    findings = detect_unicode("Hello World")
    assert findings == []


def test_detects_bidi_control():
    findings = detect_unicode("Hello\u202eWorld")
    assert len(findings) == 1
    assert findings[0]["character"] == "U+202E"


def test_allows_newline_and_tab():
    findings = detect_unicode("Hello\nWorld\t!")
    assert findings == []