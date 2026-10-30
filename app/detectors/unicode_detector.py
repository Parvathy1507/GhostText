import unicodedata


ZERO_WIDTH_CHARACTERS = {
    "\u200b": "Zero-width space",
    "\u200c": "Zero-width non-joiner",
    "\u200d": "Zero-width joiner",
    "\u2060": "Word joiner",
    "\ufeff": "Zero-width no-break space / BOM",
}

BIDI_CONTROLS = {
    "\u061c",
    "\u200e",
    "\u200f",
    "\u202a",
    "\u202b",
    "\u202c",
    "\u202d",
    "\u202e",
    "\u2066",
    "\u2067",
    "\u2068",
    "\u2069",
}


def detect_unicode(text: str) -> list[dict]:
    findings = []

    for position, char in enumerate(text):
        name = ZERO_WIDTH_CHARACTERS.get(char)

        if name:
            findings.append({
                "position": position,
                "character": f"U+{ord(char):04X}",
                "name": name,
                "reason": "Invisible or formatting character detected."
            })

        elif char in BIDI_CONTROLS:
            findings.append({
                "position": position,
                "character": f"U+{ord(char):04X}",
                "name": unicodedata.name(char, "Unknown Unicode character"),
                "reason": "Bidirectional control character detected."
            })

        elif unicodedata.category(char) == "Cc" and char not in "\n\r\t":
            findings.append({
                "position": position,
                "character": f"U+{ord(char):04X}",
                "name": unicodedata.name(char, "Control character"),
                "reason": "Unexpected control character detected."
            })

    return findings