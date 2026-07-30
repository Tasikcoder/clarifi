"""Adjudication service — orchestrates Fuzzy AHP scoring for a claim."""

import json
from services.snowflake_service import execute_query, get_connection
from services.fuzzy_ahp_service import (
    evaluate_claim,
    mock_assess_claim,
    DEFAULT_WEIGHTS,
)


def get_weights_from_db() -> dict[str, float]:
    """Fetch criteria weights from Snowflake."""
    try:
        rows = execute_query("SELECT criteria_id, weight FROM CLARIFI.CLAIMS.FUZZY_AHP_WEIGHTS")
        if rows:
            return {row["CRITERIA_ID"]: float(row["WEIGHT"]) for row in rows}
    except Exception:
        pass
    return DEFAULT_WEIGHTS


def assess_from_extracted_facts(claim_id: str) -> list[dict] | None:
    """
    Generate linguistic assessments from extracted facts (if available).
    Returns None if no extraction exists — falls back to mock.
    """
    rows = execute_query(
        """SELECT extracted_data FROM CLARIFI.CLAIMS.EXTRACTED_FACTS
           WHERE claim_id = %s ORDER BY extracted_at DESC LIMIT 1""",
        (claim_id,),
    )
    if not rows:
        return None

    facts = rows[0].get("EXTRACTED_DATA")
    if isinstance(facts, str):
        facts = json.loads(facts)
    if not facts or not isinstance(facts, dict):
        return None

    assessments = []

    # C1: Medical Necessity
    correlation_issues = facts.get("correlation_issues", [])
    procedures = facts.get("procedures", [])
    unindicated = [p for p in procedures if isinstance(p, dict) and p.get("medically_indicated") is False]

    if correlation_issues or unindicated:
        if len(correlation_issues) > 1 or len(unindicated) > 1:
            label = "Not Justified"
        else:
            label = "Poorly Justified"
        reason = "; ".join(correlation_issues) if correlation_issues else "; ".join(p.get("reason", "") for p in unindicated)
    else:
        label = "Justified"
        reason = "Prosedur berkorelasi dengan diagnosis"
    assessments.append({"criteria_id": "C1", "criteria_name": "Medical Necessity", "label": label, "reason": reason})

    # C2: Policy Compliance
    pre_existing = facts.get("pre_existing_flags", [])
    if pre_existing:
        if len(pre_existing) >= 2:
            label = "Poorly Justified"
        else:
            label = "Partially Justified"
        reason = "; ".join(pre_existing)
    else:
        label = "Highly Consistent"
        reason = "Tidak ada flag pre-existing atau exclusion"
    assessments.append({"criteria_id": "C2", "criteria_name": "Policy Compliance", "label": label, "reason": reason})

    # C3: Documentation Completeness
    completeness = facts.get("document_completeness", "partial")
    if completeness == "complete":
        label = "Highly Consistent"
        reason = "Semua dokumen pendukung lengkap"
    elif completeness == "partial":
        label = "Partially Justified"
        reason = "Beberapa dokumen masih kurang"
    else:
        label = "Poorly Justified"
        reason = "Dokumentasi tidak lengkap"
    assessments.append({"criteria_id": "C3", "criteria_name": "Documentation Completeness", "label": label, "reason": reason})

    # C4: Cost Reasonableness
    risk_indicators = facts.get("risk_indicators", [])
    cost_risks = [r for r in risk_indicators if "biaya" in r.lower() or "cost" in r.lower() or "mahal" in r.lower()]
    if cost_risks:
        label = "Partially Justified"
        reason = "; ".join(cost_risks)
    elif unindicated:
        # If there are unindicated procedures, cost is partially questionable
        label = "Partially Justified"
        reason = f"Prosedur tanpa indikasi medis termasuk dalam tagihan"
    else:
        label = "Justified"
        reason = "Biaya dalam rentang wajar"
    assessments.append({"criteria_id": "C4", "criteria_name": "Cost Reasonableness", "label": label, "reason": reason})

    return assessments


def run_adjudication(claim_id: str) -> dict:
    """Run Fuzzy AHP scoring for a claim and store the result."""
    weights = get_weights_from_db()

    # Try fact-based assessment first, fall back to mock
    assessments = assess_from_extracted_facts(claim_id)
    if assessments is None:
        assessments = mock_assess_claim(claim_id)

    result = evaluate_claim(assessments, weights)
    result.claim_id = claim_id

    # Store result in Snowflake
    breakdown_json = json.dumps(result.criteria_breakdown)
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO CLARIFI.CLAIMS.ADJUDICATION_RESULTS 
               (claim_id, final_score, decision, decision_reason, criteria_breakdown)
               SELECT %s, %s, %s, %s, PARSE_JSON(%s)""",
            (claim_id, result.final_score, result.decision, result.decision_reason, breakdown_json),
        )

    # Auto-update claim status based on score
    try:
        from services.decision_service import auto_decide_after_scoring
        auto_decide_after_scoring(claim_id, result.final_score, result.decision)
    except Exception:
        pass  # Non-fatal if status update fails

    return {
        "claim_id": result.claim_id,
        "final_score": result.final_score,
        "decision": result.decision,
        "decision_reason": result.decision_reason,
        "criteria_breakdown": result.criteria_breakdown,
    }


def get_adjudication(claim_id: str) -> dict | None:
    """Get the latest adjudication result for a claim."""
    rows = execute_query(
        """SELECT adjudication_id, claim_id, final_score, decision, decision_reason,
                  criteria_breakdown, assessed_at, assessed_by
           FROM CLARIFI.CLAIMS.ADJUDICATION_RESULTS
           WHERE claim_id = %s
           ORDER BY assessed_at DESC
           LIMIT 1""",
        (claim_id,),
    )
    if not rows:
        return None

    row = rows[0]
    breakdown = row.get("CRITERIA_BREAKDOWN")
    if isinstance(breakdown, str):
        breakdown = json.loads(breakdown)

    return {
        "adjudication_id": row["ADJUDICATION_ID"],
        "claim_id": row["CLAIM_ID"],
        "final_score": float(row["FINAL_SCORE"]),
        "decision": row["DECISION"],
        "decision_reason": row["DECISION_REASON"],
        "criteria_breakdown": breakdown,
        "assessed_at": str(row["ASSESSED_AT"]),
        "assessed_by": row["ASSESSED_BY"],
    }


def get_similar_claims(claim_id: str, limit: int = 5) -> list[dict]:
    """Find similar claims using Cortex Search Service."""
    # Get the current claim's diagnosis and procedures as search query
    rows = execute_query(
        """SELECT diagnosis_awal, jenis_layanan, nama_provider
           FROM CLARIFI.CLAIMS.CLAIM_SUBMISSIONS WHERE claim_id = %s""",
        (claim_id,),
    )
    if not rows:
        return []

    row = rows[0]
    query_text = f"{row['DIAGNOSIS_AWAL']} {row['JENIS_LAYANAN']} {row['NAMA_PROVIDER']}"

    # Also get procedures
    procs = execute_query(
        "SELECT LISTAGG(deskripsi_tindakan, '; ') as procs FROM CLARIFI.CLAIMS.CLAIM_LINE_ITEMS WHERE claim_id = %s",
        (claim_id,),
    )
    if procs and procs[0].get("PROCS"):
        query_text += " " + procs[0]["PROCS"][:200]

    # Query Cortex Search Service
    try:
        escaped_query = query_text.replace("\\", "\\\\").replace('"', '\\"').replace("'", "''")
        search_json = json.dumps({
            "query": query_text[:500],
            "columns": ["claim_id", "patient_name", "diagnosis_awal", "jenis_layanan", "total_amount", "status", "final_score", "decision"],
            "limit": limit + 1,
        })
        escaped_json = search_json.replace("'", "''")

        results = execute_query(
            f"""SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
                'CLARIFI.CLAIMS.SIMILAR_CLAIMS_SEARCH',
                '{escaped_json}'
            ) as results"""
        )
        if not results:
            return []

        raw = results[0].get("RESULTS")
        if isinstance(raw, str):
            parsed = json.loads(raw)
        else:
            parsed = raw

        similar = []
        if isinstance(parsed, dict) and "results" in parsed:
            for item in parsed["results"]:
                if item.get("claim_id") != claim_id:
                    similar.append({
                        "claim_id": item.get("claim_id"),
                        "patient_name": item.get("patient_name"),
                        "diagnosis_awal": item.get("diagnosis_awal"),
                        "jenis_layanan": item.get("jenis_layanan"),
                        "total_amount": float(item.get("total_amount", 0)),
                        "status": item.get("status"),
                        "final_score": float(item["final_score"]) if item.get("final_score") else None,
                        "decision": item.get("decision"),
                    })
        return similar[:limit]
    except Exception as e:
        # Fallback: return recent claims
        fallback_rows = execute_query(
            """SELECT claim_id, patient_name, diagnosis_awal, jenis_layanan, total_amount, status
               FROM CLARIFI.CLAIMS.CLAIM_SUBMISSIONS
               WHERE claim_id != %s ORDER BY created_at DESC LIMIT %s""",
            (claim_id, limit),
        )
        return [
            {
                "claim_id": r["CLAIM_ID"],
                "patient_name": r["PATIENT_NAME"],
                "diagnosis_awal": r["DIAGNOSIS_AWAL"],
                "jenis_layanan": r["JENIS_LAYANAN"],
                "total_amount": float(r["TOTAL_AMOUNT"]),
                "status": r["STATUS"],
                "final_score": None,
                "decision": None,
            }
            for r in fallback_rows
        ]


def get_adjudication_summary() -> dict:
    """Get aggregated adjudication statistics for dashboard."""
    rows = execute_query(
        """SELECT 
             COUNT(*) AS total,
             COUNT_IF(decision = 'Auto-Approve') AS approved,
             COUNT_IF(decision = 'Manual Review') AS review,
             COUNT_IF(decision = 'Auto-Reject') AS rejected,
             AVG(final_score) AS avg_score
           FROM CLARIFI.CLAIMS.ADJUDICATION_RESULTS"""
    )
    if not rows:
        return {"total": 0, "approved": 0, "review": 0, "rejected": 0, "avg_score": 0}

    row = rows[0]
    return {
        "total": int(row["TOTAL"]),
        "approved": int(row["APPROVED"]),
        "review": int(row["REVIEW"]),
        "rejected": int(row["REJECTED"]),
        "avg_score": round(float(row["AVG_SCORE"] or 0), 2),
    }
