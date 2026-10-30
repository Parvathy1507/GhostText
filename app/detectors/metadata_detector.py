import re
import pymupdf


SUSPICIOUS_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"disregard\s+(all\s+)?(previous\s+)?instructions",
    r"reveal\s+(the\s+)?(confidential|secret|hidden)\s+information",
    r"ignore\s+your\s+system\s+instructions",
    r"reveal\s+your\s+system\s+prompt",
]

MAX_METADATA_LENGTH = 500


def detect_pdf_metadata(content: bytes) -> list[dict]:
    """Inspect PDF metadata for potentially suspicious indicators."""

    findings = []

    try:
        with pymupdf.open(stream=content, filetype="pdf") as pdf:
            metadata = pdf.metadata or {}

            for field in ["author", "title", "creator", "producer"]:
                value = metadata.get(field)

                if not isinstance(value, str) or not value:
                    continue

                # Check for unexpected control characters.
                if any(
                    ord(char) < 32 and char not in "\t\n\r"
                    for char in value
                ):
                    findings.append({
                        "type": "suspicious_pdf_metadata",
                        "field": field,
                        "matched_text": value[:200],
                        "reason": (
                            f"PDF {field} metadata contains "
                            "unexpected control characters."
                        ),
                        "recommendation": (
                            "Inspect this metadata and verify "
                            "whether the characters are intentional."
                        )
                    })

                # Check for unusually long metadata.
                if len(value) > MAX_METADATA_LENGTH:
                    findings.append({
                        "type": "suspicious_pdf_metadata",
                        "field": field,
                        "matched_text": value[:200],
                        "reason": (
                            f"PDF {field} metadata exceeds "
                            f"{MAX_METADATA_LENGTH} characters."
                        ),
                        "recommendation": (
                            "Review this unusually long metadata value. "
                            "Length alone does not prove malicious intent."
                        )
                    })

                # Check for instruction-like text.
                for pattern in SUSPICIOUS_PATTERNS:
                    match = re.search(pattern, value, re.IGNORECASE)

                    if match:
                        findings.append({
                            "type": "suspicious_pdf_metadata",
                            "field": field,
                            "matched_text": match.group(),
                            "reason": (
                                "PDF metadata contains text matching "
                                "a potentially suspicious instruction."
                            ),
                            "recommendation": (
                                "Review the metadata and surrounding "
                                "document context before using the file "
                                "with an AI system."
                            )
                        })

    except Exception as exc:
        raise ValueError(
            "Could not inspect PDF metadata."
        ) from exc

    return findings