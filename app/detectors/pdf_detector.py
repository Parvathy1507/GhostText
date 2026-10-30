import pymupdf


def detect_hidden_pdf_text(content: bytes) -> list[dict]:
    """Detect PDF text with potentially hidden rendering properties."""

    findings = []

    try:
       with pymupdf.open(stream=content, filetype="pdf") as pdf:
            for page_number, page in enumerate(pdf, start=1):

                # Check text rendering properties.
                for span in page.get_texttrace():
                    characters = span.get("chars", [])
                    text = "".join(
                        chr(char[0])
                        for char in characters
                        if char[0] > 0
                    )

                    if not text.strip():
                        continue

                    render_type = span.get("type", -1)
                    opacity = span.get("opacity", 1.0)

                    if render_type == 3:
                        findings.append({
                            "type": "potentially_hidden_pdf_text",
                            "page": page_number,
                            "matched_text": text,
                            "reason": (
                                "Text uses invisible PDF rendering mode."
                            ),
                            "recommendation": (
                                "Inspect this text and confirm whether "
                                "it is an intentional OCR or accessibility layer."
                            )
                        })

                    elif opacity <= 0.05:
                        findings.append({
                            "type": "potentially_hidden_pdf_text",
                            "page": page_number,
                            "matched_text": text,
                            "reason": (
                                "Text has very low rendering opacity."
                            ),
                            "recommendation": (
                                "Inspect the text's visibility and "
                                "confirm whether the opacity is intentional."
                            )
                        })

                # Check for unusually small text.
                page_data = page.get_text("dict")

                for block in page_data.get("blocks", []):
                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            text = span.get("text", "").strip()
                            size = span.get("size", 0)

                            if text and 0 < size < 3:
                                findings.append({
                                    "type": "potentially_hidden_pdf_text",
                                    "page": page_number,
                                    "matched_text": text,
                                    "font_size": round(size, 2),
                                    "reason": (
                                        "Text uses an unusually small "
                                        "font size below 3 points."
                                    ),
                                    "recommendation": (
                                        "Inspect the text at high zoom "
                                        "to determine whether it is "
                                        "legitimate small print or suspicious."
                                    )
                                })

    except Exception as exc:
        raise ValueError("Could not inspect PDF rendering properties.") from exc

    return findings