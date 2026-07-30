import os
import tempfile
from pathlib import Path
from services.snowflake_service import upload_file_to_stage, execute_procedure, execute_query, get_connection
from services.document_parser import parse_file
from services.document_screening_service import screen_document

# Local docs folder — documents saved here for analysis
DOCS_DIR = Path(__file__).parent.parent.parent / "docs"

SUPPORTED_PARSE_EXTENSIONS = {".pdf", ".docx"}


def upload_and_register_document(
    claim_id: str,
    document_type: str,
    file_name: str,
    file_content: bytes,
) -> dict:
    # Save to local docs/{claim_id}/ folder for analysis
    claim_docs_dir = DOCS_DIR / claim_id
    claim_docs_dir.mkdir(parents=True, exist_ok=True)
    local_path = str(claim_docs_dir / file_name)

    with open(local_path, "wb") as f:
        f.write(file_content)

    # Also upload to Snowflake stage for persistence
    stage_path = f"@CLARIFI.CLAIMS.CLAIM_DOCS_STAGE/{claim_id}/"
    try:
        upload_file_to_stage(local_path, stage_path)
    except Exception:
        pass  # Non-fatal: local copy is enough for MVP

    # Register in metadata table
    full_stage_path = f"@CLARIFI.CLAIMS.CLAIM_DOCS_STAGE/{claim_id}/{file_name}"
    result = execute_procedure(
        "CALL CLARIFI.CLAIMS.REGISTER_DOCUMENT(%s, %s, %s, %s)",
        (claim_id, document_type, file_name, full_stage_path),
    )

    # Auto-parse if supported format
    parse_result = _auto_parse_document(claim_id, file_name, local_path)

    return {
        "message": result,
        "stage_path": full_stage_path,
        "local_path": local_path,
        "parse_status": parse_result.get("status", "SKIPPED"),
        "detected_doc_type": parse_result.get("doc_type"),
        "screening": parse_result.get("screening"),
    }


def _auto_parse_document(claim_id: str, file_name: str, local_path: str) -> dict:
    """Auto-parse document after upload, then screen for relevancy."""
    ext = Path(file_name).suffix.lower()
    if ext not in SUPPORTED_PARSE_EXTENSIONS:
        return {"status": "SKIPPED", "doc_type": None}

    try:
        parsed = parse_file(local_path)
        if parsed.get("error"):
            _update_document_parse_status(claim_id, file_name, "FAILED", None, None)
            return {"status": "FAILED", "doc_type": None, "error": parsed["error"]}

        raw_text = parsed.get("raw_text", "")
        doc_type = parsed.get("doc_type", "unknown")

        # Screen document for relevancy before storing
        screening = screen_document(raw_text, file_name)

        if screening["passed"]:
            _update_document_parse_status(claim_id, file_name, "PARSED", doc_type, raw_text)
            return {"status": "PARSED", "doc_type": doc_type, "screening": screening}
        else:
            _update_document_parse_status(claim_id, file_name, "REJECTED", screening["category"], None)
            return {"status": "REJECTED", "doc_type": screening["category"], "screening": screening}
    except Exception as e:
        _update_document_parse_status(claim_id, file_name, "FAILED", None, None)
        return {"status": "FAILED", "doc_type": None, "error": str(e)}


def _update_document_parse_status(
    claim_id: str, file_name: str, status: str, doc_type: str | None, parsed_text: str | None
):
    """Update parse status in CLAIM_DOCUMENTS table."""
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """UPDATE CLARIFI.CLAIMS.CLAIM_DOCUMENTS 
                   SET parse_status = %s, detected_doc_type = %s, parsed_text = %s
                   WHERE claim_id = %s AND file_name = %s""",
                (status, doc_type, parsed_text, claim_id, file_name),
            )
    except Exception:
        pass  # Non-fatal for MVP
