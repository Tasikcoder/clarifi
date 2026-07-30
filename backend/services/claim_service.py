import json
from services.snowflake_service import execute_query, execute_procedure


def submit_claim(data: dict) -> dict:
    line_items_json = json.dumps(data["line_items"])
    
    result = execute_procedure(
        """CALL CLARIFI.CLAIMS.SUBMIT_CLAIM(
            %s, %s, %s, %s, %s, %s, %s, %s, %s
        )""",
        (
            data["policy_id"],
            data["patient_id"],
            data["patient_name"],
            str(data["tanggal_kejadian"]),
            str(data["tanggal_pengajuan"]),
            data["jenis_layanan"],
            data["nama_provider"],
            data["diagnosis_awal"] or "",
            line_items_json,
        ),
    )
    
    # Parse claim_id from result string
    claim_id = result.split("Claim ID: ")[-1] if "Claim ID:" in result else None
    
    if claim_id:
        claim = get_claim_by_id(claim_id)
        return claim
    
    return {"error": result}


def get_claims(status: str = None, limit: int = 50) -> list[dict]:
    sql = "SELECT * FROM CLARIFI.CLAIMS.CLAIM_SUBMISSIONS"
    params = []
    
    if status:
        sql += " WHERE status = %s"
        params.append(status)
    
    sql += " ORDER BY created_at DESC LIMIT %s"
    params.append(limit)
    
    return execute_query(sql, tuple(params))


def get_claim_by_id(claim_id: str) -> dict:
    claims = execute_query(
        "SELECT * FROM CLARIFI.CLAIMS.CLAIM_SUBMISSIONS WHERE claim_id = %s",
        (claim_id,),
    )
    if not claims:
        return None
    
    line_items = execute_query(
        "SELECT * FROM CLARIFI.CLAIMS.CLAIM_LINE_ITEMS WHERE claim_id = %s ORDER BY item_no",
        (claim_id,),
    )
    
    documents = execute_query(
        "SELECT * FROM CLARIFI.CLAIMS.CLAIM_DOCUMENTS WHERE claim_id = %s ORDER BY uploaded_at",
        (claim_id,),
    )
    
    return {
        "claim": claims[0],
        "line_items": line_items,
        "documents": documents,
    }
