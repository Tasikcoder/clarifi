"""
Extraction Service — Use Snowflake Cortex LLM to extract structured clinical facts
from parsed document text.
"""

import json
from services.snowflake_service import execute_query


EXTRACTION_PROMPT = """Kamu adalah sistem ekstraksi data klaim asuransi kesehatan. 
Dari teks dokumen klaim berikut, extract informasi terstruktur dalam format JSON.

INSTRUKSI:
1. Extract semua fakta klinis yang relevan
2. Identifikasi ketidaksesuaian (misalnya prosedur yang tidak berkorelasi dengan diagnosis)
3. Detect potensi pre-existing condition
4. Identifikasi apakah setiap prosedur medically indicated atau tidak

OUTPUT FORMAT (JSON ketat, tanpa komentar):
{{
  "patient_name": "string",
  "policy_number": "string",
  "claim_number": "string",
  "diagnosis_primary": {{"code": "ICD-10 code", "name": "nama diagnosis"}},
  "diagnosis_secondary": [{{"code": "string", "name": "string"}}],
  "procedures": [
    {{
      "code": "CPT/kode tindakan",
      "name": "nama prosedur",
      "cost": angka_biaya,
      "medically_indicated": true/false,
      "reason": "alasan kenapa indicated/tidak"
    }}
  ],
  "length_of_stay_days": angka,
  "admission_date": "YYYY-MM-DD",
  "discharge_date": "YYYY-MM-DD",
  "total_cost": angka_total,
  "attending_doctor": "nama dokter",
  "hospital": "nama RS",
  "clinical_findings": "ringkasan temuan klinis",
  "doctor_notes": "catatan penting dokter",
  "pre_existing_flags": ["list of pre-existing concerns jika ada"],
  "correlation_issues": ["list of ketidaksesuaian antara diagnosis dan prosedur/temuan"],
  "document_completeness": "complete/partial/incomplete",
  "risk_indicators": ["list of red flags untuk adjudikasi"]
}}

TEKS DOKUMEN:
{document_text}

PENTING: Output HANYA JSON valid, tanpa teks tambahan sebelum atau sesudah JSON.
"""


def extract_facts_from_text(combined_text: str) -> dict:
    """
    Send combined document text to Snowflake Cortex LLM for structured extraction.
    Returns extracted facts as a dict.
    """
    prompt = EXTRACTION_PROMPT.format(document_text=combined_text[:15000])  # limit to ~15K chars
    
    # Escape single quotes for SQL
    escaped_prompt = prompt.replace("'", "''")
    
    sql = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('mistral-large2', '{escaped_prompt}') AS result"
    
    rows = execute_query(sql)
    if not rows:
        return {"error": "No response from Cortex LLM"}
    
    raw_response = rows[0]["RESULT"]
    
    # Parse JSON from LLM response
    try:
        # Try to find JSON in the response (LLM might add extra text)
        json_start = raw_response.find("{")
        json_end = raw_response.rfind("}") + 1
        if json_start >= 0 and json_end > json_start:
            json_str = raw_response[json_start:json_end]
            return json.loads(json_str)
        else:
            return {"error": "No JSON found in LLM response", "raw": raw_response[:500]}
    except json.JSONDecodeError as e:
        return {"error": f"JSON parse error: {str(e)}", "raw": raw_response[:500]}


def extract_facts_for_claim(parsed_docs: list[dict]) -> dict:
    """
    Given a list of parsed documents, combine and extract structured facts.
    
    Args:
        parsed_docs: Output from document_parser.parse_multiple_docs()
    
    Returns:
        Extracted facts dict
    """
    from services.document_parser import combine_docs_text
    
    combined_text = combine_docs_text(parsed_docs)
    
    if not combined_text.strip():
        return {"error": "No text content found in documents"}
    
    facts = extract_facts_from_text(combined_text)
    
    # Add metadata
    facts["_metadata"] = {
        "source_documents": [d["file_name"] for d in parsed_docs if not d.get("error")],
        "doc_types": [d["doc_type"] for d in parsed_docs if not d.get("error")],
        "extraction_method": "cortex_llm",
    }
    
    return facts
