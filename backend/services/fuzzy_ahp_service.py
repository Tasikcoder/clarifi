"""
ClariFi Fuzzy AHP Scoring Engine
Skill 3: Linguistic assessment -> TFN -> defuzzification -> score 0-100
"""

from dataclasses import dataclass


# Triangular Fuzzy Number mapping (linguistic label -> (l, m, u))
TFN_SCALE: dict[str, tuple[float, float, float]] = {
    "Not Justified": (0, 0, 25),
    "Poorly Justified": (10, 25, 40),
    "Partially Justified": (25, 40, 60),
    "Justified": (50, 65, 80),
    "Highly Consistent": (75, 90, 100),
}

# Decision thresholds
THRESHOLD_REJECT = 40
THRESHOLD_APPROVE = 70


@dataclass
class CriteriaResult:
    criteria_id: str
    criteria_name: str
    weight: float
    linguistic_label: str
    tfn: tuple[float, float, float]
    defuzzified: float
    weighted_contribution: float
    reason: str


@dataclass
class AdjudicationResult:
    claim_id: str
    final_score: float
    decision: str
    decision_reason: str
    criteria_breakdown: list[dict]


def defuzzify_centroid(tfn: tuple[float, float, float]) -> float:
    """Centroid defuzzification: (l + m + u) / 3"""
    return round(sum(tfn) / 3, 2)


def get_decision(score: float) -> str:
    if score < THRESHOLD_REJECT:
        return "Auto-Reject"
    elif score > THRESHOLD_APPROVE:
        return "Auto-Approve"
    return "Manual Review"


def build_decision_reason(score: float, decision: str, breakdown: list[CriteriaResult]) -> str:
    """Generate explainable decision reason string."""
    top_criteria = max(breakdown, key=lambda c: c.weight)
    reason = (
        f"Score {score:.1f}: {decision}. "
        f"{top_criteria.criteria_name} (weight: {top_criteria.weight*100:.0f}%) "
        f"scored '{top_criteria.linguistic_label}' "
        f"— {top_criteria.reason}."
    )
    return reason


def evaluate_claim(
    assessments: list[dict],
    weights: dict[str, float],
) -> AdjudicationResult:
    """
    Run Fuzzy AHP scoring.

    Args:
        assessments: List of dicts with keys:
            criteria_id, criteria_name, label, reason
        weights: Dict mapping criteria_id -> weight (0-1, sum should be 1.0)

    Returns:
        AdjudicationResult with score, decision, and breakdown
    """
    breakdown: list[CriteriaResult] = []
    total_score = 0.0

    for assessment in assessments:
        criteria_id = assessment["criteria_id"]
        label = assessment["label"]
        weight = weights.get(criteria_id, 0.0)

        tfn = TFN_SCALE.get(label, (0, 0, 0))
        defuzzified = defuzzify_centroid(tfn)
        contribution = round(defuzzified * weight, 2)
        total_score += contribution

        breakdown.append(CriteriaResult(
            criteria_id=criteria_id,
            criteria_name=assessment["criteria_name"],
            weight=weight,
            linguistic_label=label,
            tfn=tfn,
            defuzzified=defuzzified,
            weighted_contribution=contribution,
            reason=assessment["reason"],
        ))

    final_score = round(total_score, 2)
    decision = get_decision(final_score)
    decision_reason = build_decision_reason(final_score, decision, breakdown)

    return AdjudicationResult(
        claim_id="",  # set by caller
        final_score=final_score,
        decision=decision,
        decision_reason=decision_reason,
        criteria_breakdown=[
            {
                "criteria_id": c.criteria_id,
                "criteria_name": c.criteria_name,
                "weight": c.weight,
                "linguistic_label": c.linguistic_label,
                "tfn": list(c.tfn),
                "defuzzified": c.defuzzified,
                "weighted_contribution": c.weighted_contribution,
                "reason": c.reason,
            }
            for c in breakdown
        ],
    )


# --- Mock Assessment (will be replaced by LLM + Fact Extraction) ---

# Claim-specific mock scenarios for varied adjudication results
_MOCK_SCENARIOS: dict[str, list[dict]] = {
    # CLM-2026-0001: Appendicitis — moderately justified (Manual Review ~66)
    "CLM-2026-0001": [
        {"criteria_id": "C1", "criteria_name": "Medical Necessity", "label": "Justified", "reason": "Diagnosis correlates with prescribed treatment"},
        {"criteria_id": "C2", "criteria_name": "Policy Compliance", "label": "Highly Consistent", "reason": "Treatment within coverage limits and not excluded"},
        {"criteria_id": "C3", "criteria_name": "Documentation Completeness", "label": "Partially Justified", "reason": "Missing lab results attachment"},
        {"criteria_id": "C4", "criteria_name": "Cost Reasonableness", "label": "Justified", "reason": "Charges within regional average for procedure"},
    ],
    # CLM-2026-0002: Common Cold outpatient — clearly justified (Auto-Approve ~85)
    "CLM-2026-0002": [
        {"criteria_id": "C1", "criteria_name": "Medical Necessity", "label": "Highly Consistent", "reason": "Standard treatment for common cold diagnosis"},
        {"criteria_id": "C2", "criteria_name": "Policy Compliance", "label": "Highly Consistent", "reason": "Outpatient visit fully covered under SILVER plan"},
        {"criteria_id": "C3", "criteria_name": "Documentation Completeness", "label": "Justified", "reason": "Prescription and lab results attached"},
        {"criteria_id": "C4", "criteria_name": "Cost Reasonableness", "label": "Highly Consistent", "reason": "Total Rp750K well below average outpatient cost"},
    ],
    # CLM-2026-0003: Spine surgery — justified but complex (Manual Review ~62)
    "CLM-2026-0003": [
        {"criteria_id": "C1", "criteria_name": "Medical Necessity", "label": "Justified", "reason": "MRI confirms disc herniation requiring surgical intervention"},
        {"criteria_id": "C2", "criteria_name": "Policy Compliance", "label": "Justified", "reason": "Within GOLD plan limits, procedure not excluded"},
        {"criteria_id": "C3", "criteria_name": "Documentation Completeness", "label": "Partially Justified", "reason": "Pre-op MRI present but second opinion not documented"},
        {"criteria_id": "C4", "criteria_name": "Cost Reasonableness", "label": "Partially Justified", "reason": "Rp45M slightly above regional average for laminectomy"},
    ],
    # CLM-2026-0004: Cosmetic rhinoplasty — excluded (Auto-Reject ~18)
    "CLM-2026-0004": [
        {"criteria_id": "C1", "criteria_name": "Medical Necessity", "label": "Not Justified", "reason": "Rhinoplasty is cosmetic, no medical indication documented"},
        {"criteria_id": "C2", "criteria_name": "Policy Compliance", "label": "Not Justified", "reason": "Cosmetic surgery explicitly excluded in SILVER policy"},
        {"criteria_id": "C3", "criteria_name": "Documentation Completeness", "label": "Poorly Justified", "reason": "No referral letter or medical necessity justification"},
        {"criteria_id": "C4", "criteria_name": "Cost Reasonableness", "label": "Partially Justified", "reason": "Cost within market range for rhinoplasty procedure"},
    ],
    # CLM-2026-0005: Cardiac emergency — fully justified (Auto-Approve ~88)
    "CLM-2026-0005": [
        {"criteria_id": "C1", "criteria_name": "Medical Necessity", "label": "Highly Consistent", "reason": "STEMI requires immediate PCI intervention per ACC/AHA guidelines"},
        {"criteria_id": "C2", "criteria_name": "Policy Compliance", "label": "Highly Consistent", "reason": "Emergency cardiac care fully covered under PLATINUM plan"},
        {"criteria_id": "C3", "criteria_name": "Documentation Completeness", "label": "Highly Consistent", "reason": "ECG, troponin, cath report, and discharge summary all present"},
        {"criteria_id": "C4", "criteria_name": "Cost Reasonableness", "label": "Justified", "reason": "Rp85M within expected range for PCI with dual stenting and 7-day ICU"},
    ],
}


def mock_assess_claim(claim_id: str) -> list[dict]:
    """
    Simulate LLM linguistic assessment for a claim.
    Returns different labels per claim to produce varied adjudication results.
    In production, this will call Snowflake Cortex LLM.
    """
    if claim_id in _MOCK_SCENARIOS:
        return _MOCK_SCENARIOS[claim_id]

    # Default fallback for unknown claims
    return [
        {"criteria_id": "C1", "criteria_name": "Medical Necessity", "label": "Justified", "reason": "Assessment pending detailed review"},
        {"criteria_id": "C2", "criteria_name": "Policy Compliance", "label": "Justified", "reason": "Preliminary check passed"},
        {"criteria_id": "C3", "criteria_name": "Documentation Completeness", "label": "Partially Justified", "reason": "Some documents may be missing"},
        {"criteria_id": "C4", "criteria_name": "Cost Reasonableness", "label": "Justified", "reason": "Cost appears within acceptable range"},
    ]


# Default weights (fallback if DB not available)
DEFAULT_WEIGHTS = {
    "C1": 0.40,  # Medical Necessity
    "C2": 0.25,  # Policy Compliance
    "C3": 0.20,  # Documentation Completeness
    "C4": 0.15,  # Cost Reasonableness
}
