from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile, Depends

from app.analyzer import analyze_text, calculate_risk
from app.config import MAX_FILE_SIZE
from app.database import save_analysis, get_history, clear_history
from app.document_extractor import extract_text
from app.detectors.pdf_detector import detect_hidden_pdf_text
from app.detectors.metadata_detector import detect_pdf_metadata
from app.auth import get_current_user


router = APIRouter()

ALLOWED_EXTENSIONS = {".pdf", ".docx"}


@router.post("/analyze")
async def analyze_document(
    file: UploadFile = File(...),
    user=Depends(get_current_user)
):
    filename = Path(file.filename or "").name
    extension = Path(filename).suffix.lower()

    # Check file extension
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Upload a PDF or DOCX."
        )

    # Read and validate file size
    content = await file.read(MAX_FILE_SIZE + 1)

    if not content:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty."
        )

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File exceeds the configured size limit."
        )

    # Extract document text
    try:
        extracted_text = extract_text(filename, content)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Could not read this document. Check that it is valid."
        )

    # Analyze extracted text
    analysis = analyze_text(extracted_text)

    # Run additional PDF detectors
    if extension == ".pdf":
        try:
            pdf_findings = detect_hidden_pdf_text(content)
            metadata_findings = detect_pdf_metadata(content)
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Could not inspect PDF properties."
            )

        for finding in pdf_findings:
            analysis["findings"].append({
                **finding,
                "risk": "MEDIUM"
            })

        for finding in metadata_findings:
            analysis["findings"].append({
                **finding,
                "risk": "LOW"
            })

    # Calculate final risk
    findings = analysis["findings"]
    analysis["findings_count"] = len(findings)
    analysis["risk_level"] = calculate_risk(findings)

    analysis["status"] = (
        "findings_detected" if findings
        else "no_findings_detected"
    )

    analysis["message"] = (
        "Potentially suspicious indicators were detected."
        if findings
        else "No suspicious indicators were detected by the current checks."
    )

    # Save this analysis under the logged-in user's account
    save_analysis(
        user_id=user["id"],
        filename=filename,
        file_size=len(content),
        risk_level=analysis["risk_level"],
        findings_count=analysis["findings_count"],
        characters_analyzed=len(extracted_text)
    )

    return {
        "filename": filename,
        "size_bytes": len(content),
        "characters_extracted": len(extracted_text),
        "analysis": analysis
    }


@router.get("/history")
def analysis_history(user=Depends(get_current_user)):
    return {
        "history": get_history(user["id"])
    }


@router.delete("/history")
def delete_analysis_history(user=Depends(get_current_user)):
    clear_history(user["id"])

    return {
        "message": "Your analysis history has been cleared successfully."
    }