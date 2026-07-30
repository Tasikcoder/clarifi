from fastapi import APIRouter, HTTPException
from models.claim import ClaimSubmitRequest, ApiResponse
from services.claim_service import submit_claim, get_claims, get_claim_by_id
from typing import Optional

router = APIRouter()


@router.post("", response_model=ApiResponse)
def create_claim(request: ClaimSubmitRequest):
    data = request.model_dump()
    data["line_items"] = [item.model_dump() for item in request.line_items]
    
    result = submit_claim(data)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return ApiResponse(status="success", data=result)


@router.get("", response_model=ApiResponse)
def list_claims(status: Optional[str] = None, limit: int = 50):
    claims = get_claims(status=status, limit=limit)
    return ApiResponse(status="success", data=claims)


@router.get("/{claim_id}", response_model=ApiResponse)
def get_claim(claim_id: str):
    result = get_claim_by_id(claim_id)
    
    if not result:
        raise HTTPException(status_code=404, detail=f"Claim {claim_id} not found")
    
    return ApiResponse(status="success", data=result)
