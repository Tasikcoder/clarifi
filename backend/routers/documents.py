from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from models.claim import ApiResponse
from services.document_service import upload_and_register_document
from services.snowflake_service import execute_query

router = APIRouter()


@router.post("/{claim_id}/documents", response_model=ApiResponse)
async def upload_document(
    claim_id: str,
    document_type: str = Form(..., description="MEDICAL_REPORT, INVOICE, CLAIM_FORM, or OTHER"),
    file: UploadFile = File(...),
):
    valid_types = ["MEDICAL_REPORT", "INVOICE", "CLAIM_FORM", "OTHER"]
    if document_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid document_type. Must be one of: {valid_types}",
        )
    
    content = await file.read()
    result = upload_and_register_document(
        claim_id=claim_id,
        document_type=document_type,
        file_name=file.filename,
        file_content=content,
    )
    
    return ApiResponse(status="success", data=result)


@router.get("/{claim_id}/documents", response_model=ApiResponse)
def list_documents(claim_id: str):
    docs = execute_query(
        "SELECT * FROM CLARIFI.CLAIMS.CLAIM_DOCUMENTS WHERE claim_id = %s ORDER BY uploaded_at",
        (claim_id,),
    )
    return ApiResponse(status="success", data=docs)
