from fastapi import APIRouter, HTTPException
from models.policyholder import PolicyholderCreateRequest
from models.claim import ApiResponse
from services.policyholder_service import create_policyholder, get_policyholders, get_policyholder_by_id

router = APIRouter()


@router.post("", response_model=ApiResponse)
def create(request: PolicyholderCreateRequest):
    result = create_policyholder(request.model_dump())
    return ApiResponse(status="success", data=result)


@router.get("", response_model=ApiResponse)
def list_all(limit: int = 50):
    rows = get_policyholders(limit=limit)
    return ApiResponse(status="success", data=rows)


@router.get("/{policyholder_id}", response_model=ApiResponse)
def get_detail(policyholder_id: str):
    result = get_policyholder_by_id(policyholder_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Policyholder {policyholder_id} not found")
    return ApiResponse(status="success", data=result)
