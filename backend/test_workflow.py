"""Quick test script for decision workflow."""
import sys
sys.path.insert(0, ".")

from services.decision_service import (
    get_claim_status, update_claim_status, make_decision,
    fulfill_conditions, get_claim_history, get_notes
)

claim_id = "CLM-2026-0003"

print(f"=== Testing workflow for {claim_id} ===")
status = get_claim_status(claim_id)
print(f"1. Current status: {status}")

if status == "SUBMITTED":
    # Step: Move to MANUAL_REVIEW (simulates adjudication)
    update_claim_status(claim_id, "MANUAL_REVIEW", "Score 56.83 requires manual review", "SYSTEM")
    print(f"2. Moved to: {get_claim_status(claim_id)}")

    # Step: Officer decides Approved with Conditions
    r = make_decision(claim_id, "APPROVED_WITH_CONDITIONS", "MRI tidak justified, approve sisanya", ["Biaya MRI Rp4.2jt tidak ditanggung"])
    print(f"3. Decision made: {r}")
    print(f"   Status now: {get_claim_status(claim_id)}")

    # Step: Fulfill conditions
    r2 = fulfill_conditions(claim_id, True, "Nasabah setuju potongan MRI")
    print(f"4. Conditions fulfilled: {r2}")
    print(f"   Final status: {get_claim_status(claim_id)}")

    # Show history
    history = get_claim_history(claim_id)
    print(f"\n=== History ({len(history)} entries) ===")
    for h in history:
        print(f"  {h['old_status']} -> {h['new_status']}: {h['reason']}")

    notes = get_notes(claim_id)
    print(f"\n=== Notes ({len(notes)}) ===")
    for n in notes:
        print(f"  [{n['note_type']}] {n['content']} ({n['status']})")
else:
    print(f"  Status is {status}, already processed.")
