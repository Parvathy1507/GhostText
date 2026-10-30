import pymupdf

from app.detectors.pdf_detector import detect_hidden_pdf_text


def test_detects_invisible_pdf_text():
    document = pymupdf.open()
    page = document.new_page()

    # Render text using PDF rendering mode 3 (invisible text).
    page.insert_text(
        (50, 50),
        "Hidden GhostText test",
        render_mode=3
    )

    pdf_bytes = document.tobytes()
    document.close()

    findings = detect_hidden_pdf_text(pdf_bytes)

    assert any(
        "invisible PDF rendering mode" in finding["reason"]
        for finding in findings
    )