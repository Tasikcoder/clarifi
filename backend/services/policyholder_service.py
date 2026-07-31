from services.snowflake_service import execute_query


def create_policyholder(data: dict) -> dict:
    seq_result = execute_query("SELECT CLARIFI.CLAIMS.POLICYHOLDER_ID_SEQ.NEXTVAL AS val")
    seq_val = seq_result[0]["VAL"]
    ph_id = f"PH-{str(int(seq_val)).zfill(4)}"

    execute_query(
        """INSERT INTO CLARIFI.CLAIMS.POLICYHOLDERS 
        (policyholder_id, nama_lengkap, no_ktp, tanggal_lahir, jenis_kelamin, alamat, no_telepon, email, tanggal_daftar)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (
            ph_id,
            data["nama_lengkap"],
            data["no_ktp"],
            data.get("tanggal_lahir") or None,
            data.get("jenis_kelamin") or None,
            data.get("alamat") or None,
            data.get("no_telepon") or None,
            data.get("email") or None,
            data.get("tanggal_daftar") or None,
        ),
    )
    return {"policyholder_id": ph_id}


def get_policyholders(limit: int = 50) -> list[dict]:
    return execute_query(
        "SELECT * FROM CLARIFI.CLAIMS.POLICYHOLDERS ORDER BY created_at DESC LIMIT %s",
        (limit,),
    )


def get_policyholder_by_id(ph_id: str) -> dict | None:
    rows = execute_query(
        "SELECT * FROM CLARIFI.CLAIMS.POLICYHOLDERS WHERE policyholder_id = %s",
        (ph_id,),
    )
    if not rows:
        return None

    policies = execute_query(
        "SELECT * FROM CLARIFI.CLAIMS.POLICIES WHERE policyholder_id = %s ORDER BY effective_date DESC",
        (ph_id,),
    )
    return {"policyholder": rows[0], "policies": policies}
