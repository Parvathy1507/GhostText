from app.analyzer import analyze_text


def test_normal_text():
    result = analyze_text("Hello GhostText")

    assert result["status"] == "no_findings_detected"
    assert result["findings_count"] == 0


def test_suspicious_unicode():
    result = analyze_text("Hello\u200bWorld")

    assert result["status"] == "findings_detected"
    assert result["findings_count"] == 1
    assert result["findings"][0]["character"] == "U+200B"


def test_empty_text():
    result = analyze_text("")

    assert result["status"] == "no_findings_detected"
    assert result["characters_analyzed"] == 0