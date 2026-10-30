from pathlib import Path
from io import BytesIO
from zipfile import is_zipfile

import pymupdf
from docx import Document


def extract_text(filename: str, content: bytes) -> str:
    extension = Path(filename).suffix.lower()

    # Validate and extract PDF
    if extension == ".pdf":
        if not content.startswith(b"%PDF-"):
            raise ValueError("Invalid PDF file.")

        with pymupdf.open(stream=content, filetype="pdf") as pdf:
            if pdf.is_encrypted:
                raise ValueError("Encrypted PDFs are not supported.")

            return "\n".join(
                page.get_text() for page in pdf
            )

    # Validate and extract DOCX
    elif extension == ".docx":
        file_data = BytesIO(content)

        # Check whether the file is a ZIP archive
        if not is_zipfile(file_data):
            raise ValueError("Invalid DOCX file.")

        file_data.seek(0)

        # Extract text from the Word document
        document = Document(file_data)

        return "\n".join(
            paragraph.text for paragraph in document.paragraphs
        )

    else:
        raise ValueError(
            "Unsupported file type. Use PDF or DOCX."
        )
