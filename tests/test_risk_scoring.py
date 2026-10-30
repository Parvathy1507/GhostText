from app.analyzer import calculate_risk


def test_no_findings_low_risk():
    assert calculate_risk([]) == "LOW"


def test_unicode_finding_low_risk():
    findings = [
        {"type": "suspicious_unicode"}
    ]
    assert calculate_risk(findings) == "LOW"


def test_instruction_finding_medium_risk():
    findings = [
        {"type": "suspicious_instruction"}
    ]
    assert calculate_risk(findings) == "MEDIUM"


def test_multiple_instructions_high_risk():
    findings = [
        {"type": "suspicious_instruction"},
        {"type": "suspicious_instruction"}
    ]
    assert calculate_risk(findings) == "HIGH"


def test_metadata_and_unicode_medium_risk():
    findings = [
        {"type": "suspicious_pdf_metadata"},
        {"type": "suspicious_unicode"}
    ]
    assert calculate_risk(findings) == "MEDIUM"