"""
Decision Service — Claim state machine, notes, and workflow management.
Every claim must end at APPROVED or REJECTED.
"""

from services.snowflake_service import execute_query, get_connection

# Valid status transitions
VALID_TRANSITIONS = {
    "SUBMITTED": ["AUTO_APPROVED", "AUTO_REJECTED", "MANUAL_REVIEW"],
    "AUTO_APPROVED": ["APPROVED"],
    "AUTO_REJECTED": ["REJECTED"],
    "MANUAL_REVIEW": ["APPROVED", "REJECTED", "APPROVED_WITH_CONDITIONS", "PENDING_CLARIFICATION"],
    "PENDING_CLARIFICATION": ["MANUAL_REVIEW", "REJECTED"],
    "APPROVED_WITH_CONDITIONS": ["APPROVED", "REJECTED"],
    # Terminal states — no transitions out
    "APPROVED": [],
    "REJECTED": [],
}

TERMINAL_STATUSES = {"APPROVED", "REJECTED"}
INTERMEDIATE_STATUSES = {"MANUAL_REVIEW", "PENDING_CLARIFICATION", "APPROVED_WITH_CONDITIONS"}


def get_claim_status(claim_id: str) -> str | None:
    rows = execute_query(
        "SELECT status FROM CLARIFI.CLAIMS.CLAIM_SUBMISSIONS WHERE claim_id = %s",
        (claim_id,),
    )
    return rows[0]["STATUS"] if rows else None


def update_claim_status(claim_id: str, new_status: str, reason: str = "", changed_by: str = "SYSTEM"):
    """Update claim status with validation and history logging."""
    current = get_claim_status(claim_id)
    if current is None:
        raise ValueError(f"Claim {claim_id} not found")

    allowed = VALID_TRANSITIONS.get(current, [])
    if new_status not in allowed:
        raise ValueError(f"Cannot transition from {current} to {new_status}. Allowed: {allowed}")

    with get_connection() as conn:
        cur = conn.cursor()
        # Update status
        cur.execute(
            "UPDATE CLARIFI.CLAIMS.CLAIM_SUBMISSIONS SET status = %s, updated_at = CURRENT_TIMESTAMP() WHERE claim_id = %s",
            (new_status, claim_id),
        )
        # Log history
        cur.execute(
            """INSERT INTO CLARIFI.CLAIMS.CLAIM_STATUS_HISTORY 
               (claim_id, old_status, new_status, reason, changed_by)
               VALUES (%s, %s, %s, %s, %s)""",
            (claim_id, current, new_status, reason, changed_by),
        )


def make_decision(
    claim_id: str, decision: str, reason: str,
    conditions: list[str] | None = None,
    approved_amount: float | None = None,
    officer: str = "OFFICER",
) -> dict:
    """
    Petugas membuat keputusan pada klaim.
    decision: APPROVED, REJECTED, APPROVED_WITH_CONDITIONS, PENDING_CLARIFICATION
    approved_amount: Jumlah yang disetujui (untuk partial approval)
    """
    update_claim_status(claim_id, decision, reason, officer)

    # Store approved_amount if provided
    if approved_amount is not None and decision in ("APPROVED", "APPROVED_WITH_CONDITIONS", "AUTO_APPROVED"):
        _set_approved_amount(claim_id, approved_amount)

    # Create decision note
    amount_note = f" Jumlah disetujui: Rp {approved_amount:,.0f}." if approved_amount else ""
    add_note(claim_id, "decision", f"Keputusan: {decision}.{amount_note} {reason}", officer)

    # If approved with conditions, create condition notes
    if decision == "APPROVED_WITH_CONDITIONS" and conditions:
        for cond in conditions:
            add_note(claim_id, "condition", cond, officer)

    # If pending clarification, note stays open until resolved
    if decision == "PENDING_CLARIFICATION":
        add_note(claim_id, "clarification_request", reason, officer)

    return {"claim_id": claim_id, "new_status": decision, "reason": reason, "approved_amount": approved_amount}


def _set_approved_amount(claim_id: str, amount: float):
    """Store approved amount in the claim record."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE CLARIFI.CLAIMS.CLAIM_SUBMISSIONS SET approved_amount = %s WHERE claim_id = %s",
            (amount, claim_id),
        )


def auto_decide_after_scoring(claim_id: str, score: float, decision_label: str):
    """Called automatically after Fuzzy AHP scoring."""
    if decision_label == "Auto-Approve":
        update_claim_status(claim_id, "AUTO_APPROVED", f"Score {score} > 70", "SYSTEM")
        update_claim_status(claim_id, "APPROVED", f"Auto-approved with score {score}", "SYSTEM")
    elif decision_label == "Auto-Reject":
        update_claim_status(claim_id, "AUTO_REJECTED", f"Score {score} < 40", "SYSTEM")
        update_claim_status(claim_id, "REJECTED", f"Auto-rejected with score {score}", "SYSTEM")
    elif decision_label == "Manual Review":
        update_claim_status(claim_id, "MANUAL_REVIEW", f"Score {score} requires manual review", "SYSTEM")


def fulfill_conditions(claim_id: str, fulfilled: bool, evidence: str = "", officer: str = "OFFICER") -> dict:
    """Verify if conditions are met. If fulfilled → APPROVED, else → REJECTED."""
    current = get_claim_status(claim_id)
    if current != "APPROVED_WITH_CONDITIONS":
        raise ValueError(f"Claim is not in APPROVED_WITH_CONDITIONS status (current: {current})")

    if fulfilled:
        # Resolve all open condition notes
        _resolve_open_notes(claim_id, "condition", f"Fulfilled: {evidence}", officer)
        update_claim_status(claim_id, "APPROVED", f"Conditions fulfilled. {evidence}", officer)
        return {"claim_id": claim_id, "new_status": "APPROVED"}
    else:
        _resolve_open_notes(claim_id, "condition", f"Not fulfilled: {evidence}", officer)
        update_claim_status(claim_id, "REJECTED", f"Conditions not met. {evidence}", officer)
        return {"claim_id": claim_id, "new_status": "REJECTED"}


def respond_clarification(claim_id: str, response_content: str, officer: str = "OFFICER") -> dict:
    """Respond to pending clarification → move back to MANUAL_REVIEW."""
    current = get_claim_status(claim_id)
    if current != "PENDING_CLARIFICATION":
        raise ValueError(f"Claim is not in PENDING_CLARIFICATION status (current: {current})")

    # Add response note and resolve the request
    add_note(claim_id, "clarification_response", response_content, officer)
    _resolve_open_notes(claim_id, "clarification_request", f"Response received", officer)
    update_claim_status(claim_id, "MANUAL_REVIEW", "Clarification received, ready for re-review", officer)
    return {"claim_id": claim_id, "new_status": "MANUAL_REVIEW"}


# --- Notes ---

def add_note(claim_id: str, note_type: str, content: str, created_by: str = "OFFICER") -> dict:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO CLARIFI.CLAIMS.ADJUDICATION_NOTES 
               (claim_id, note_type, content, created_by)
               VALUES (%s, %s, %s, %s)""",
            (claim_id, note_type, content, created_by),
        )
    return {"claim_id": claim_id, "note_type": note_type, "content": content}


def resolve_note(note_id: str, resolution: str = "", resolved_by: str = "OFFICER"):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """UPDATE CLARIFI.CLAIMS.ADJUDICATION_NOTES 
               SET status = 'RESOLVED', resolved_by = %s, resolved_at = CURRENT_TIMESTAMP()
               WHERE note_id = %s""",
            (resolved_by, note_id),
        )


def _resolve_open_notes(claim_id: str, note_type: str, resolution: str, resolved_by: str):
    """Resolve all open notes of a given type for a claim."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """UPDATE CLARIFI.CLAIMS.ADJUDICATION_NOTES 
               SET status = 'RESOLVED', resolved_by = %s, resolved_at = CURRENT_TIMESTAMP()
               WHERE claim_id = %s AND note_type = %s AND status = 'OPEN'""",
            (resolved_by, claim_id, note_type),
        )


def get_notes(claim_id: str) -> list[dict]:
    rows = execute_query(
        """SELECT note_id, claim_id, note_type, content, status, created_by, resolved_by, resolved_at, created_at
           FROM CLARIFI.CLAIMS.ADJUDICATION_NOTES
           WHERE claim_id = %s ORDER BY created_at""",
        (claim_id,),
    )
    return [
        {
            "note_id": r["NOTE_ID"],
            "note_type": r["NOTE_TYPE"],
            "content": r["CONTENT"],
            "status": r["STATUS"],
            "created_by": r["CREATED_BY"],
            "resolved_by": r["RESOLVED_BY"],
            "resolved_at": str(r["RESOLVED_AT"]) if r["RESOLVED_AT"] else None,
            "created_at": str(r["CREATED_AT"]),
        }
        for r in rows
    ]


def get_claim_history(claim_id: str) -> list[dict]:
    rows = execute_query(
        """SELECT history_id, old_status, new_status, reason, changed_by, changed_at
           FROM CLARIFI.CLAIMS.CLAIM_STATUS_HISTORY
           WHERE claim_id = %s ORDER BY changed_at""",
        (claim_id,),
    )
    return [
        {
            "old_status": r["OLD_STATUS"],
            "new_status": r["NEW_STATUS"],
            "reason": r["REASON"],
            "changed_by": r["CHANGED_BY"],
            "changed_at": str(r["CHANGED_AT"]),
        }
        for r in rows
    ]
