import re


SUSPICIOUS_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"disregard\s+(all\s+)?(previous\s+)?instructions",
    r"reveal\s+(the\s+)?(confidential|secret|hidden)\s+information",
    r"ignore\s+your\s+system\s+instructions",
    r"do\s+not\s+tell\s+the\s+user",
    r"reveal\s+your\s+system\s+prompt",
]


def detect_instructions(text: str) -> list[dict]:
    findings = []

    for pattern in SUSPICIOUS_PATTERNS:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            findings.append({
                "position": match.start(),
                "matched_text": match.group(),
                "reason": "Text matches a potentially suspicious AI-directed instruction."
            })

    return findings