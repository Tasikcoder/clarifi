from fastapi import APIRouter, HTTPException
from models.claim import ApiResponse
from services.adjudication_service import (
    run_adjudication,
    get_adjudication,
    get_adjudication_summary,
    get_similar_claims,
)

router = APIRouter()


@router.post("/{claim_id}/adjudicate", response_model=ApiResponse)
def adjudicate_claim(claim_id: str):
    """Run Fuzzy AHP scoring on a claim."""
    try:
        result = run_adjudication(claim_id)
        return ApiResponse(status="success", data=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{claim_id}/adjudication", response_model=ApiResponse)
def get_claim_adjudication(claim_id: str):
    """Get the latest adjudication result for a claim."""
    result = get_adjudication(claim_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"No adjudication found for {claim_id}")
    return ApiResponse(status="success", data=result)


@router.get("/summary/adjudications", response_model=ApiResponse)
def adjudication_dashboard_summary():
    """Get aggregated stats for the dashboard."""
    summary = get_adjudication_summary()
    return ApiResponse(status="success", data=summary)


@router.get("/{claim_id}/similar", response_model=ApiResponse)
def similar_claims(claim_id: str):
    """Find similar claims using Cortex Search."""
    results = get_similar_claims(claim_id)
    return ApiResponse(status="success", data=results)
