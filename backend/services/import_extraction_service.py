"""
Import Extraction Service — Extract master data (policyholder, policy, rules)
from .docx and .pdf documents using Snowflake Cortex LLM.
"""

import json
from pathlib import Path
from services.snowflake_service import execute_query
from services.document_parser import parse_file, combine_docs_text


POLICYHOLDER_PROMPT = """Extract data pemegang polis/nasabah dari dokumen berikut. Output JSON ketat:
{{
  "nama_lengkap": "string",
  "no_ktp": "string (NIK 16 digit)",
  "tanggal_lahir": "YYYY-MM-DD",
  "jenis_kelamin": "L atau P",
  "alamat": "string",
  "no_telepon": "string",
  "email": "string"
}}

DOKUMEN:
{text}

Output HANYA JSON valid tanpa teks tambahan."""


POLICY_PROMPT = """Extract data kontrak polis asuransi dari dokumen berikut. Output JSON ketat:
{{
  "policyholder_name": "string (nama pemegang polis)",
  "plan_type": "GOLD/SILVER/PLATINUM/BRONZE",
  "coverage_limit": angka (tanpa Rp, titik, atau koma),
  "effective_date": "YYYY-MM-DD",
  "expiry_date": "YYYY-MM-DD",
  "exclusions": ["list", "of", "exclusion strings"],
  "premi_bulanan": angka (tanpa Rp)
}}

DOKUMEN:
{text}

Output HANYA JSON valid tanpa teks tambahan."""


RULES_PROMPT = """Extract semua aturan klaim dari dokumen berikut. Output JSON array:
[
  {{
    "rule_name": "string",
    "rule_category": "ELIGIBILITY/COVERAGE_LIMIT/WAITING_PERIOD/EXCLUSION/DOCUMENTATION",
    "condition_expression": "string (deskripsi kondisi)",
    "action": "APPROVE/REJECT/FLAG",
    "priority": angka (0=tertinggi),
    "description": "string"
  }}
]

Bisa ada lebih dari 1 aturan. Output HANYA JSON array valid tanpa teks tambahan.

DOKUMEN:
{text}"""


def _call_cortex(prompt: str) -> str:
    """Call Cortex LLM and return raw response."""
    escaped = prompt.replace("'", "''")
    sql = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('mistral-large2', '{escaped}') AS result"
    rows = execute_query(sql)
    if not rows:
        return ""
    return rows[0]["RESULT"]


def _parse_json_response(raw: str) -> dict | list | None:
    """Parse JSON from LLM response, handling extra text and markdown code blocks."""
    cleaned = raw.strip()
    # Strip markdown code blocks (```json ... ``` or ``` ... ```)
    if "```json" in cleaned:
        cleaned = cleaned.split("```json")[1]
        if "```" in cleaned:
            cleaned = cleaned.split("```")[0]
        cleaned = cleaned.strip()
    elif "```" in cleaned:
        parts = cleaned.split("```")
        for part in parts:
            stripped = part.strip()
            if stripped.startswith("{") or stripped.startswith("["):
                cleaned = stripped
                break

    # Try array first
    arr_start = cleaned.find("[")
    arr_end = cleaned.rfind("]") + 1
    if arr_start >= 0 and arr_end > arr_start:
        try:
            return json.loads(cleaned[arr_start:arr_end])
        except json.JSONDecodeError:
            pass

    # Try object
    obj_start = cleaned.find("{")
    obj_end = cleaned.rfind("}") + 1
    if obj_start >= 0 and obj_end > obj_start:
        try:
            return json.loads(cleaned[obj_start:obj_end])
        except json.JSONDecodeError:
            pass

    return None


def extract_policyholder_from_file(file_path: str) -> dict:
    """Parse document (PDF or DOCX) and extract policyholder data."""
    parsed = parse_file(file_path)
    if parsed.get("error"):
        return {"error": f"Parse failed: {parsed['error']}"}
    raw_text = parsed["raw_text"][:8000]
    if not raw_text.strip():
        return {"error": "No text content found in document"}
    prompt = POLICYHOLDER_PROMPT.format(text=raw_text)
    response = _call_cortex(prompt)
    result = _parse_json_response(response)
    if result and isinstance(result, dict):
        return result
    return {"error": "Failed to extract policyholder data", "raw": response[:300]}


# Keep backward compat alias
extract_policyholder_from_docx = extract_policyholder_from_file


def extract_policy_from_file(file_path: str) -> dict:
    """Parse document (PDF or DOCX) and extract policy/contract data."""
    parsed = parse_file(file_path)
    if parsed.get("error"):
        return {"error": f"Parse failed: {parsed['error']}"}
    raw_text = parsed["raw_text"][:8000]
    if not raw_text.strip():
        return {"error": "No text content found in document"}
    prompt = POLICY_PROMPT.format(text=raw_text)
    response = _call_cortex(prompt)
    
    if not response:
        return {"error": "Empty response from LLM"}
    
    result = _parse_json_response(response)
    
    if result and isinstance(result, dict):
        # Normalize numeric fields
        for field in ("coverage_limit", "premi_bulanan"):
            if field in result and isinstance(result[field], str):
                cleaned = result[field].replace("Rp", "").replace(".", "").replace(",", "").strip()
                try:
                    result[field] = int(cleaned)
                except ValueError:
                    pass
        return result
    
    # Fallback: try direct JSON parse after stripping common wrappers
    import re
    json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response, re.DOTALL)
    if json_match:
        try:
            fallback = json.loads(json_match.group())
            if isinstance(fallback, dict) and "plan_type" in fallback:
                return fallback
        except json.JSONDecodeError:
            pass
    
    return {"error": "Failed to extract policy data", "raw": response[:500]}


# Keep backward compat alias
extract_policy_from_docx = extract_policy_from_file


def extract_rules_from_file(file_path: str) -> list[dict]:
    """Parse document (PDF or DOCX) and extract claim rules (can be multiple)."""
    parsed = parse_file(file_path)
    if parsed.get("error"):
        return [{"error": f"Parse failed: {parsed['error']}"}]
    raw_text = parsed["raw_text"][:12000]
    if not raw_text.strip():
        return [{"error": "No text content found in document"}]
    prompt = RULES_PROMPT.format(text=raw_text)
    response = _call_cortex(prompt)
    result = _parse_json_response(response)
    if result and isinstance(result, list):
        return result
    if result and isinstance(result, dict):
        return [result]
    return [{"error": "Failed to extract rules", "raw": response[:300]}]


# Keep backward compat alias
extract_rules_from_docx = extract_rules_from_file
