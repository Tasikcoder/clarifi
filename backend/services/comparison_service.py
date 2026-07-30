"""
Comparison Service — Compare form data vs extracted facts, generate suggestions.
"""

import json
from services.snowflake_service import execute_query, get_connection


def get_claim_form_data(claim_id: str) -> dict | None:
    """Fetch claim form data from CLAIM_SUBMISSIONS."""
    rows = execute_query(
        "SELECT * FROM CLARIFI.CLAIMS.CLAIM_SUBMISSIONS WHERE claim_id = %s",
        (claim_id,),
    )
    if not rows:
        return None
    return rows[0]


def compare_and_suggest(claim_id: str, extracted_facts: dict) -> list[dict]:
    """
    Compare form data with extracted facts. Generate suggestions for discrepancies.

    Returns list of suggestions:
    [
        {
            "field_name": str,
            "form_value": str,
            "extracted_value": str,
            "suggestion_type": "mismatch" | "enrichment" | "flag",
            "note": str,
            "severity": "info" | "warning" | "critical"
        }
    ]
    """
    form_data = get_claim_form_data(claim_id)
    if not form_data:
        return [{"field_name": "claim", "suggestion_type": "flag", "note": f"Claim {claim_id} not found in database", "severity": "critical"}]

    suggestions = []

    # Compare diagnosis
    diag_form = form_data.get("DIAGNOSIS_AWAL", "") or ""
    diag_extracted = extracted_facts.get("diagnosis_primary", {})
    if diag_extracted and isinstance(diag_extracted, dict):
        diag_doc = f"{diag_extracted.get('name', '')} ({diag_extracted.get('code', '')})"
        if diag_form.lower().replace(" ", "") != diag_extracted.get("name", "").lower().replace(" ", ""):
            suggestions.append({
                "field_name": "diagnosis_awal",
                "form_value": diag_form,
                "extracted_value": diag_doc,
                "suggestion_type": "mismatch" if diag_form else "enrichment",
                "note": f"Diagnosis di dokumen: {diag_doc}",
                "severity": "warning",
            })

    # Compare total amount
    total_form = float(form_data.get("TOTAL_AMOUNT", 0) or 0)
    total_extracted = extracted_facts.get("total_cost")
    if total_extracted and abs(total_form - total_extracted) > 1000:
        suggestions.append({
            "field_name": "total_amount",
            "form_value": f"Rp {total_form:,.0f}",
            "extracted_value": f"Rp {total_extracted:,.0f}",
            "suggestion_type": "mismatch",
            "note": f"Selisih Rp {abs(total_form - total_extracted):,.0f}",
            "severity": "warning",
        })

    # Compare length of stay
    los_extracted = extracted_facts.get("length_of_stay_days")
    if los_extracted:
        suggestions.append({
            "field_name": "length_of_stay",
            "form_value": "-",
            "extracted_value": f"{los_extracted} hari",
            "suggestion_type": "enrichment",
            "note": f"Lama rawat inap: {los_extracted} hari (dari dokumen)",
            "severity": "info",
        })

    # Compare provider/hospital
    provider_form = form_data.get("NAMA_PROVIDER", "") or ""
    hospital_extracted = extracted_facts.get("hospital", "")
    if hospital_extracted and provider_form.lower() != hospital_extracted.lower():
        if provider_form:
            suggestions.append({
                "field_name": "nama_provider",
                "form_value": provider_form,
                "extracted_value": hospital_extracted,
                "suggestion_type": "mismatch",
                "note": "Nama RS berbeda antara form dan dokumen",
                "severity": "warning",
            })

    # Correlation issues (flags from extraction)
    correlation_issues = extracted_facts.get("correlation_issues", [])
    for issue in correlation_issues:
        suggestions.append({
            "field_name": "correlation",
            "form_value": "-",
            "extracted_value": issue,
            "suggestion_type": "flag",
            "note": f"Ketidaksesuaian: {issue}",
            "severity": "critical",
        })

    # Pre-existing flags
    pre_existing = extracted_facts.get("pre_existing_flags", [])
    for flag in pre_existing:
        suggestions.append({
            "field_name": "pre_existing",
            "form_value": "-",
            "extracted_value": flag,
            "suggestion_type": "flag",
            "note": f"Pre-existing concern: {flag}",
            "severity": "critical",
        })

    # Procedures not medically indicated
    procedures = extracted_facts.get("procedures", [])
    for proc in procedures:
        if isinstance(proc, dict) and proc.get("medically_indicated") is False:
            suggestions.append({
                "field_name": "procedure_necessity",
                "form_value": "-",
                "extracted_value": f"{proc.get('name', 'Unknown')} ({proc.get('code', '')})",
                "suggestion_type": "flag",
                "note": f"Prosedur tidak medically indicated: {proc.get('reason', '')}",
                "severity": "critical",
            })

    # Risk indicators
    risk_indicators = extracted_facts.get("risk_indicators", [])
    for risk in risk_indicators:
        suggestions.append({
            "field_name": "risk",
            "form_value": "-",
            "extracted_value": risk,
            "suggestion_type": "flag",
            "note": risk,
            "severity": "warning",
        })

    return suggestions


def save_extraction_results(claim_id: str, extracted_facts: dict, suggestions: list[dict]):
    """Save extraction results and suggestions to Snowflake."""
    facts_json = json.dumps(extracted_facts, default=str)
    source_docs = json.dumps(extracted_facts.get("_metadata", {}).get("source_documents", []))
    method = extracted_facts.get("_metadata", {}).get("extraction_method", "cortex_llm")

    with get_connection() as conn:
        cur = conn.cursor()

        # Save extracted facts
        cur.execute(
            """INSERT INTO CLARIFI.CLAIMS.EXTRACTED_FACTS 
               (claim_id, extracted_data, source_documents, extraction_method)
               SELECT %s, PARSE_JSON(%s), PARSE_JSON(%s), %s""",
            (claim_id, facts_json, source_docs, method),
        )

        # Save suggestions
        for s in suggestions:
            cur.execute(
                """INSERT INTO CLARIFI.CLAIMS.EXTRACTION_SUGGESTIONS
                   (claim_id, field_name, form_value, extracted_value, suggestion_type, note)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (claim_id, s["field_name"], s.get("form_value", ""), s.get("extracted_value", ""), s["suggestion_type"], s.get("note", "")),
            )


def get_extraction_results(claim_id: str) -> dict | None:
    """Get saved extraction results for a claim."""
    rows = execute_query(
        """SELECT fact_id, claim_id, extracted_data, source_documents, 
                  extraction_method, extracted_at
           FROM CLARIFI.CLAIMS.EXTRACTED_FACTS
           WHERE claim_id = %s
           ORDER BY extracted_at DESC LIMIT 1""",
        (claim_id,),
    )
    if not rows:
        return None

    row = rows[0]
    extracted_data = row.get("EXTRACTED_DATA")
    if isinstance(extracted_data, str):
        extracted_data = json.loads(extracted_data)

    return {
        "fact_id": row["FACT_ID"],
        "claim_id": row["CLAIM_ID"],
        "extracted_data": extracted_data,
        "source_documents": row.get("SOURCE_DOCUMENTS"),
        "extraction_method": row["EXTRACTION_METHOD"],
        "extracted_at": str(row["EXTRACTED_AT"]),
    }


def get_suggestions(claim_id: str) -> list[dict]:
    """Get suggestions for a claim."""
    rows = execute_query(
        """SELECT suggestion_id, field_name, form_value, extracted_value,
                  suggestion_type, note, officer_decision, decided_at
           FROM CLARIFI.CLAIMS.EXTRACTION_SUGGESTIONS
           WHERE claim_id = %s
           ORDER BY created_at""",
        (claim_id,),
    )
    return [
        {
            "suggestion_id": r["SUGGESTION_ID"],
            "field_name": r["FIELD_NAME"],
            "form_value": r["FORM_VALUE"],
            "extracted_value": r["EXTRACTED_VALUE"],
            "suggestion_type": r["SUGGESTION_TYPE"],
            "note": r["NOTE"],
            "officer_decision": r["OFFICER_DECISION"],
            "decided_at": str(r["DECIDED_AT"]) if r["DECIDED_AT"] else None,
        }
        for r in rows
    ]


def update_suggestion_decision(suggestion_id: str, decision: str):
    """Update officer decision on a suggestion (accepted/rejected)."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """UPDATE CLARIFI.CLAIMS.EXTRACTION_SUGGESTIONS
               SET officer_decision = %s, decided_at = CURRENT_TIMESTAMP()
               WHERE suggestion_id = %s""",
            (decision, suggestion_id),
        )
