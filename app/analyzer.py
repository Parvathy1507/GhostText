from app.detectors.unicode_detector import detect_unicode
from app.detectors.instruction_detector import detect_instructions


def calculate_risk(findings: list[dict]) -> str:
    """Calculate overall risk based on finding types."""

    score = 0

    for finding in findings:
        finding_type = finding.get("type", "")

        if finding_type == "suspicious_instruction":
            score += 3
        elif finding_type == "suspicious_unicode":
            score += 1
        elif finding_type == "potentially_hidden_pdf_text":
            score += 3
        elif finding_type == "suspicious_pdf_metadata":
            score += 2

    if score >= 6:
        return "HIGH"
    elif score >= 3:
        return "MEDIUM"
    else:
        return "LOW"


def analyze_text(text: str) -> dict:
    """Analyze text and provide risk levels and recommendations."""

    unicode_findings = detect_unicode(text)
    instruction_findings = detect_instructions(text)

    findings = []

    for finding in unicode_findings:
        findings.append({
            "type": "suspicious_unicode",
            "risk": "LOW",
            "recommendation": (
                "Inspect this character and confirm whether it is "
                "needed for the document's language or formatting."
            ),
            **finding
        })

    for finding in instruction_findings:
        findings.append({
            "type": "suspicious_instruction",
            "risk": "MEDIUM",
            "recommendation": (
                "Review the surrounding text. If an AI system will "
                "process this document, verify that the instruction "
                "is intended and does not conflict with your task."
            ),
            **finding
        })

    risk_level = calculate_risk(findings)

    return {
        "status": (
            "findings_detected" if findings
            else "no_findings_detected"
        ),
        "risk_level": risk_level,
        "characters_analyzed": len(text),
        "findings_count": len(findings),
        "findings": findings,
        "message": (
            "Potentially suspicious indicators were detected."
            if findings
            else "No suspicious indicators were detected by the current checks."
        )
    }