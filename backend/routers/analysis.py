"""Router for document analysis — parse, extract, compare, suggest."""

from pathlib import Path
from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Optional
from models.claim import ApiResponse
from services.document_parser import parse_multiple_docs, parse_file, combine_docs_text
from services.extraction_service import extract_facts_from_text, extract_facts_for_claim
from services.snowflake_service import execute_query
from services.comparison_service import (
    compare_and_suggest,
    save_extraction_results,
    get_extraction_results,
    get_suggestions,
    update_suggestion_decision,
)

router = APIRouter()

# Local docs folder for testing
DOCS_DIR = Path(__file__).parent.parent.parent / "docs"


@router.post("/{claim_id}/analyze-documents", response_model=ApiResponse)
def analyze_documents(claim_id: str, doc_folder: Optional[str] = None):
    """
    Parse and extract facts from documents for a claim.
    Strategy:
    1. First try: use parsed_text from database (from auto-parse on upload)
    2. Fallback: read physical files from docs/{claim_id}/ folder
    """
    # Strategy 1: Use already-parsed text from database
    db_docs = execute_query(
        """SELECT file_name, parsed_text, detected_doc_type 
           FROM CLARIFI.CLAIMS.CLAIM_DOCUMENTS 
           WHERE claim_id = %s AND parse_status = 'PARSED' AND parsed_text IS NOT NULL""",
        (claim_id,),
    )

    if db_docs:
        # Build combined text from database parsed content
        sections = []
        doc_names = []
        for doc in db_docs:
            fname = doc["FILE_NAME"]
            dtype = doc.get("DETECTED_DOC_TYPE", "unknown")
            text = doc["PARSED_TEXT"]
            if text:
                sections.append(f"--- DOKUMEN: {fname} (Tipe: {dtype}) ---")
                sections.append(text)
                sections.append("")
                doc_names.append(fname)

        combined_text = "\n".join(sections)
        if combined_text.strip():
            try:
                extracted_facts = extract_facts_from_text(combined_text)
                extracted_facts["_metadata"] = {
                    "source_documents": doc_names,
                    "extraction_method": "cortex_llm",
                    "source": "database_parsed_text",
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")

            if "error" in extracted_facts and not extracted_facts.get("patient_name"):
                raise HTTPException(status_code=500, detail=f"Extraction error: {extracted_facts['error']}")

            suggestions = compare_and_suggest(claim_id, extracted_facts)
            try:
                save_extraction_results(claim_id, extracted_facts, suggestions)
            except Exception:
                pass

            return ApiResponse(
                status="success",
                data={
                    "claim_id": claim_id,
                    "extracted_facts": extracted_facts,
                    "suggestions": suggestions,
                    "documents_parsed": doc_names,
                },
            )

    # Strategy 2: Fallback to physical files (PDF + DOCX)
    claim_folder = DOCS_DIR / claim_id
    if doc_folder:
        folder = Path(doc_folder) if Path(doc_folder).is_absolute() else DOCS_DIR / doc_folder
    elif claim_folder.exists():
        folder = claim_folder
    else:
        folder = DOCS_DIR

    if not folder.exists():
        raise HTTPException(status_code=400, detail="No documents found for this claim. Upload documents first.")

    doc_files = list(folder.glob("*.docx")) + list(folder.glob("*.pdf"))
    if not doc_files:
        raise HTTPException(status_code=400, detail="No parseable documents found. Upload PDF or DOCX files.")

    parsed_docs = parse_multiple_docs(doc_files)

    try:
        extracted_facts = extract_facts_for_claim(parsed_docs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")

    if "error" in extracted_facts and not extracted_facts.get("patient_name"):
        raise HTTPException(status_code=500, detail=f"Extraction error: {extracted_facts['error']}")

    suggestions = compare_and_suggest(claim_id, extracted_facts)
    try:
        save_extraction_results(claim_id, extracted_facts, suggestions)
    except Exception:
        pass

    return ApiResponse(
        status="success",
        data={
            "claim_id": claim_id,
            "extracted_facts": extracted_facts,
            "suggestions": suggestions,
            "documents_parsed": [d["file_name"] for d in parsed_docs if not d.get("error")],
        },
    )


@router.get("/{claim_id}/analysis", response_model=ApiResponse)
def get_analysis(claim_id: str):
    """Get saved extraction results and suggestions for a claim."""
    facts = get_extraction_results(claim_id)
    suggestions = get_suggestions(claim_id)

    if not facts:
        raise HTTPException(status_code=404, detail="No analysis found. Run analyze-documents first.")

    return ApiResponse(
        status="success",
        data={
            "extraction": facts,
            "suggestions": suggestions,
        },
    )


@router.put("/suggestions/{suggestion_id}", response_model=ApiResponse)
def decide_suggestion(suggestion_id: str, decision: str):
    """
    Accept or reject a suggestion.
    decision: 'accepted' or 'rejected'
    """
    if decision not in ("accepted", "rejected"):
        raise HTTPException(status_code=400, detail="Decision must be 'accepted' or 'rejected'")

    try:
        update_suggestion_decision(suggestion_id, decision)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return ApiResponse(status="success", data={"suggestion_id": suggestion_id, "decision": decision})


@router.post("/suggestions/{suggestion_id}", response_model=ApiResponse)
def decide_suggestion_post(suggestion_id: str, decision: str):
    """Same as PUT but via POST for frontend compatibility."""
    return decide_suggestion(suggestion_id, decision)


@router.post("/{claim_id}/analyze-upload", response_model=ApiResponse)
async def analyze_uploaded_files(claim_id: str, files: list[UploadFile] = File(...)):
    """
    Upload and analyze documents in one step.
    Accepts multiple .docx and .pdf files, parses and extracts facts.
    """
    import tempfile
    import os

    temp_paths = []
    supported_exts = (".docx", ".pdf")
    try:
        temp_dir = tempfile.mkdtemp()
        for file in files:
            if not file.filename.lower().endswith(supported_exts):
                continue
            path = os.path.join(temp_dir, file.filename)
            content = await file.read()
            with open(path, "wb") as f:
                f.write(content)
            temp_paths.append(path)

        if not temp_paths:
            raise HTTPException(status_code=400, detail="No supported files uploaded (PDF or DOCX)")

        parsed_docs = parse_multiple_docs(temp_paths)
        extracted_facts = extract_facts_for_claim(parsed_docs)

        if "error" in extracted_facts and not extracted_facts.get("patient_name"):
            raise HTTPException(status_code=500, detail=f"Extraction error: {extracted_facts.get('error')}")

        suggestions = compare_and_suggest(claim_id, extracted_facts)
        save_extraction_results(claim_id, extracted_facts, suggestions)

        return ApiResponse(
            status="success",
            data={
                "claim_id": claim_id,
                "extracted_facts": extracted_facts,
                "suggestions": suggestions,
                "documents_parsed": [d["file_name"] for d in parsed_docs if not d.get("error")],
            },
        )
    finally:
        for p in temp_paths:
            try:
                os.remove(p)
            except OSError:
                pass
