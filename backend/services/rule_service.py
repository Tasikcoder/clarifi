import json
from services.snowflake_service import execute_query


def create_rule(data: dict) -> dict:
    seq_result = execute_query("SELECT CLARIFI.CLAIMS.RULE_ID_SEQ.NEXTVAL AS val")
    seq_val = seq_result[0]["VAL"]
    rule_id = f"RULE-{str(int(seq_val)).zfill(4)}"

    condition_json = json.dumps(data.get("condition_expression") or {})

    execute_query(
        """INSERT INTO CLARIFI.CLAIMS.CLAIM_RULES 
        (rule_id, rule_name, rule_category, condition_expression, action, priority, is_active, description)
        SELECT %s, %s, %s, PARSE_JSON(%s), %s, %s, %s, %s""",
        (
            rule_id,
            data["rule_name"],
            data["rule_category"],
            condition_json,
            data["action"],
            data.get("priority") or 0,
            data.get("is_active", True),
            data.get("description") or "",
        ),
    )
    return {"rule_id": rule_id}


def get_rules(limit: int = 50) -> list[dict]:
    return execute_query(
        "SELECT * FROM CLARIFI.CLAIMS.CLAIM_RULES ORDER BY priority, created_at DESC LIMIT %s",
        (limit,),
    )


def update_rule(rule_id: str, data: dict) -> dict | None:
    existing = execute_query(
        "SELECT * FROM CLARIFI.CLAIMS.CLAIM_RULES WHERE rule_id = %s", (rule_id,)
    )
    if not existing:
        return None

    updates = []
    params = []
    for field in ["rule_name", "rule_category", "action", "priority", "is_active", "description"]:
        if data.get(field) is not None:
            updates.append(f"{field} = %s")
            params.append(data[field])

    if data.get("condition_expression") is not None:
        updates.append("condition_expression = PARSE_JSON(%s)")
        params.append(json.dumps(data["condition_expression"]))

    if not updates:
        return existing[0]

    params.append(rule_id)
    execute_query(
        f"UPDATE CLARIFI.CLAIMS.CLAIM_RULES SET {', '.join(updates)} WHERE rule_id = %s",
        tuple(params),
    )

    rows = execute_query("SELECT * FROM CLARIFI.CLAIMS.CLAIM_RULES WHERE rule_id = %s", (rule_id,))
    return rows[0] if rows else None
