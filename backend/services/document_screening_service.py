"""
Document Screening Service — Pre-validate documents before expensive LLM extraction.
Checks: 1) minimum text length, 2) AI-based relevancy classification.
Saves LLM costs by rejecting irrelevant/garbage documents early.
"""

from services.snowflake_service import execute_query

# Minimum characters to consider a document "readable"
MIN_TEXT_LENGTH = 30

# Categories for classification
RELEVANT_CATEGORIES = [
    "medical_document",
    "insurance_claim",
    "invoice_receipt",
    "lab_result",
    "prescription",
    "referral_letter",
    "policy_document",
]

IRRELEVANT_CATEGORIES = [
    "irrelevant",
    "spam",
    "personal_photo",
    "advertisement",
    "unreadable",
]

ALL_CATEGORIES = RELEVANT_CATEGORIES + IRRELEVANT_CATEGORIES


def screen_document(raw_text: str, file_name: str = "") -> dict:
    """
    Pre-screen a document before extraction.
    Returns:
        {
            "passed": bool,
            "category": str,
            "confidence": str,
            "reason": str,
        }
    """
    # Step 1: Basic text length check
    if not raw_text or len(raw_text.strip()) < MIN_TEXT_LENGTH:
        return {
            "passed": False,
            "category": "unreadable",
            "confidence": "high",
            "reason": f"Document has insufficient text content ({len(raw_text.strip()) if raw_text else 0} chars, minimum {MIN_TEXT_LENGTH})",
        }

    # Step 2: AI-based classification using Cortex
    text_sample = raw_text[:2000]  # Use first 2000 chars for efficiency
    try:
        category = _classify_document(text_sample)
    except Exception:
        # If AI classification fails, pass the document (fail-open for MVP)
        return {
            "passed": True,
            "category": "unknown",
            "confidence": "low",
            "reason": "Classification unavailable, document passed by default",
        }

    # If classification returned unknown, pass the document (fail-open)
    if category == "unknown":
        return {
            "passed": True,
            "category": "unknown",
            "confidence": "low",
            "reason": "Classification inconclusive, document passed by default",
        }

    is_relevant = category in RELEVANT_CATEGORIES

    if is_relevant:
        return {
            "passed": True,
            "category": category,
            "confidence": "high",
            "reason": f"Document classified as '{category}' — relevant to insurance claims",
        }
    else:
        return {
            "passed": False,
            "category": category,
            "confidence": "high",
            "reason": f"Document classified as '{category}' — not relevant to insurance claim processing",
        }


def _classify_document(text_sample: str) -> str:
    """Use Snowflake Cortex AI_CLASSIFY to categorize the document."""
    escaped_text = text_sample.replace("'", "''")[:1500]

    # Build category list for AI_CLASSIFY
    categories_str = ", ".join(f"'{c}'" for c in ALL_CATEGORIES)

    sql = f"""SELECT AI_CLASSIFY(
        '{escaped_text}',
        ARRAY_CONSTRUCT({categories_str})
    ) AS result"""

    rows = execute_query(sql)
    if not rows:
        return "unknown"

    result = rows[0].get("RESULT")
    if isinstance(result, dict):
        # Handle both formats: {"label": "..."} and {"labels": ["..."]}
        if "label" in result:
            return result["label"]
        if "labels" in result and isinstance(result["labels"], list) and result["labels"]:
            return result["labels"][0]
        return "unknown"
    if isinstance(result, str):
        import json
        try:
            parsed = json.loads(result)
            if "label" in parsed:
                return parsed["label"]
            if "labels" in parsed and isinstance(parsed["labels"], list) and parsed["labels"]:
                return parsed["labels"][0]
            return "unknown"
        except (json.JSONDecodeError, AttributeError):
            return result.strip().lower()

    return "unknown"
