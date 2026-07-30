import json
from services.snowflake_service import execute_query


def create_policy(data: dict) -> dict:
    seq_result = execute_query("SELECT CLARIFI.CLAIMS.POLICY_ID_SEQ.NEXTVAL AS val")
    seq_val = seq_result[0]["VAL"]
    pol_id = f"POL-{str(int(seq_val)).zfill(4)}"

    exclusions_json = json.dumps(data.get("exclusions") or [])

    execute_query(
        """INSERT INTO CLARIFI.CLAIMS.POLICIES 
        (policy_id, policyholder_id, plan_type, coverage_limit, effective_date, expiry_date, exclusions, premi_bulanan, status)
        SELECT %s, %s, %s, %s, %s, %s, PARSE_JSON(%s), %s, %s""",
        (
            pol_id,
            data["policyholder_id"],
            data["plan_type"],
            data["coverage_limit"],
            str(data["effective_date"]),
            str(data["expiry_date"]),
            exclusions_json,
            data.get("premi_bulanan") or 0,
            data.get("status") or "ACTIVE",
        ),
    )
    return {"policy_id": pol_id}


def get_policies(limit: int = 50) -> list[dict]:
    return execute_query(
        """SELECT p.*, ph.NAMA_LENGKAP AS policyholder_name 
        FROM CLARIFI.CLAIMS.POLICIES p 
        LEFT JOIN CLARIFI.CLAIMS.POLICYHOLDERS ph ON p.policyholder_id = ph.policyholder_id
        ORDER BY p.created_at DESC LIMIT %s""",
        (limit,),
    )


def get_policy_by_id(pol_id: str) -> dict | None:
    rows = execute_query(
        "SELECT * FROM CLARIFI.CLAIMS.POLICIES WHERE policy_id = %s",
        (pol_id,),
    )
    return rows[0] if rows else None
