"""Router for importing master data from .docx and .pdf documents."""

import os
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException
from models.claim import ApiResponse
from services.import_extraction_service import (
    extract_policyholder_from_file,
    extract_policy_from_file,
    extract_rules_from_file,
)
from services.document_parser import parse_file
from services.document_screening_service import screen_document

router = APIRouter()

SUPPORTED_EXTENSIONS = (".docx", ".pdf")


@router.post("/policyholder/extract", response_model=ApiResponse)
async def extract_policyholder(file: UploadFile = File(...)):
    """Upload document and extract policyholder data for preview."""
    _validate_file(file.filename)
    temp_path = await _save_temp(file)
    try:
        screening = _screen_file(temp_path, file.filename)
        if not screening["passed"]:
            return ApiResponse(status="rejected", data={"screening": screening}, message=screening["reason"])
        result = extract_policyholder_from_file(temp_path)
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        result["_screening"] = screening
        return ApiResponse(status="success", data=result)
    finally:
        os.remove(temp_path)


@router.post("/policy/extract", response_model=ApiResponse)
async def extract_policy(file: UploadFile = File(...)):
    """Upload document and extract policy contract data for preview."""
    _validate_file(file.filename)
    temp_path = await _save_temp(file)
    try:
        screening = _screen_file(temp_path, file.filename)
        if not screening["passed"]:
            return ApiResponse(status="rejected", data={"screening": screening}, message=screening["reason"])
        result = extract_policy_from_file(temp_path)
        if "error" in result:
            raise HTTPException(status_code=500, detail=result.get("raw", result["error"]))
        result["_screening"] = screening
        return ApiResponse(status="success", data=result)
    finally:
        os.remove(temp_path)


@router.post("/rules/extract", response_model=ApiResponse)
async def extract_rules(file: UploadFile = File(...)):
    """Upload document and extract claim rules for preview."""
    _validate_file(file.filename)
    temp_path = await _save_temp(file)
    try:
        screening = _screen_file(temp_path, file.filename)
        if not screening["passed"]:
            return ApiResponse(status="rejected", data={"screening": screening}, message=screening["reason"])
        result = extract_rules_from_file(temp_path)
        if isinstance(result, list) and result and "error" in result[0]:
            raise HTTPException(status_code=500, detail=result[0]["error"])
        return ApiResponse(status="success", data={"rules": result, "_screening": screening})
    finally:
        os.remove(temp_path)


def _validate_file(filename: str):
    """Check file extension is supported."""
    if not filename.lower().endswith(SUPPORTED_EXTENSIONS):
        raise HTTPException(status_code=400, detail=f"Supported formats: {', '.join(SUPPORTED_EXTENSIONS)}")


def _screen_file(file_path: str, file_name: str) -> dict:
    """Parse and screen a file for relevancy before extraction."""
    parsed = parse_file(file_path)
    raw_text = parsed.get("raw_text", "")
    return screen_document(raw_text, file_name)


async def _save_temp(file: UploadFile) -> str:
    """Save uploaded file to temp location and return path."""
    temp_dir = tempfile.mkdtemp()
    path = os.path.join(temp_dir, file.filename)
    content = await file.read()
    with open(path, "wb") as f:
        f.write(content)
    return path
