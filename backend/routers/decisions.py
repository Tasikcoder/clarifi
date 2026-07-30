"""Router for claim decisions, notes, and workflow actions."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from models.claim import ApiResponse
from services.decision_service import (
    make_decision,
    add_note,
    resolve_note,
    fulfill_conditions,
    respond_clarification,
    get_notes,
    get_claim_history,
    get_claim_status,
)

router = APIRouter()


class DecisionRequest(BaseModel):
    decision: str  # APPROVED, REJECTED, APPROVED_WITH_CONDITIONS, PENDING_CLARIFICATION
    reason: str
    conditions: Optional[list[str]] = None
    approved_amount: Optional[float] = None


class NoteRequest(BaseModel):
    note_type: str  # general, clarification_request, clarification_response
    content: str


class FulfillRequest(BaseModel):
    fulfilled: bool
    evidence: Optional[str] = ""


class ClarificationResponse(BaseModel):
    content: str


@router.post("/{claim_id}/decide", response_model=ApiResponse)
def decide_claim(claim_id: str, req: DecisionRequest):
    """Make a decision on a claim (officer action)."""
    valid_decisions = {"APPROVED", "REJECTED", "APPROVED_WITH_CONDITIONS", "PENDING_CLARIFICATION"}
    if req.decision not in valid_decisions:
        raise HTTPException(status_code=400, detail=f"Invalid decision. Must be one of: {valid_decisions}")
    try:
        result = make_decision(claim_id, req.decision, req.reason, req.conditions, req.approved_amount)
        return ApiResponse(status="success", data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{claim_id}/notes", response_model=ApiResponse)
def create_note(claim_id: str, req: NoteRequest):
    """Add a note to a claim."""
    result = add_note(claim_id, req.note_type, req.content)
    return ApiResponse(status="success", data=result)


@router.put("/notes/{note_id}/resolve", response_model=ApiResponse)
def resolve_claim_note(note_id: str, resolution: Optional[str] = ""):
    """Mark a note as resolved."""
    resolve_note(note_id, resolution)
    return ApiResponse(status="success", data={"note_id": note_id, "status": "RESOLVED"})


@router.post("/{claim_id}/fulfill-conditions", response_model=ApiResponse)
def fulfill_claim_conditions(claim_id: str, req: FulfillRequest):
    """Verify conditions are met → move to APPROVED or REJECTED."""
    try:
        result = fulfill_conditions(claim_id, req.fulfilled, req.evidence or "")
        return ApiResponse(status="success", data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{claim_id}/respond-clarification", response_model=ApiResponse)
def respond_to_clarification(claim_id: str, req: ClarificationResponse):
    """Respond to pending clarification → move back to MANUAL_REVIEW."""
    try:
        result = respond_clarification(claim_id, req.content)
        return ApiResponse(status="success", data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{claim_id}/history", response_model=ApiResponse)
def claim_history(claim_id: str):
    """Get full status change history + notes timeline."""
    history = get_claim_history(claim_id)
    notes = get_notes(claim_id)
    status = get_claim_status(claim_id)
    return ApiResponse(status="success", data={
        "current_status": status,
        "history": history,
        "notes": notes,
    })
