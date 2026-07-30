from fastapi import APIRouter, HTTPException
from models.policy import PolicyCreateRequest
from models.claim import ApiResponse
from services.policy_service import create_policy, get_policies, get_policy_by_id

router = APIRouter()


@router.post("", response_model=ApiResponse)
def create(request: PolicyCreateRequest):
    result = create_policy(request.model_dump())
    return ApiResponse(status="success", data=result)


@router.get("", response_model=ApiResponse)
def list_all(limit: int = 50):
    rows = get_policies(limit=limit)
    return ApiResponse(status="success", data=rows)


@router.get("/{policy_id}", response_model=ApiResponse)
def get_detail(policy_id: str):
    result = get_policy_by_id(policy_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Policy {policy_id} not found")
    return ApiResponse(status="success", data=result)
