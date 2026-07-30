from fastapi import APIRouter, HTTPException
from models.rule import RuleCreateRequest, RuleUpdateRequest
from models.claim import ApiResponse
from services.rule_service import create_rule, get_rules, update_rule

router = APIRouter()


@router.post("", response_model=ApiResponse)
def create(request: RuleCreateRequest):
    result = create_rule(request.model_dump())
    return ApiResponse(status="success", data=result)


@router.get("", response_model=ApiResponse)
def list_all(limit: int = 50):
    rows = get_rules(limit=limit)
    return ApiResponse(status="success", data=rows)


@router.put("/{rule_id}", response_model=ApiResponse)
def update(rule_id: str, request: RuleUpdateRequest):
    result = update_rule(rule_id, request.model_dump(exclude_none=True))
    if not result:
        raise HTTPException(status_code=404, detail=f"Rule {rule_id} not found")
    return ApiResponse(status="success", data=result)
