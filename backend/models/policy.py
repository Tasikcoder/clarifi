from pydantic import BaseModel
from typing import Optional
from datetime import date


class PolicyCreateRequest(BaseModel):
    policyholder_id: str
    plan_type: str  # INDIVIDU / KELUARGA / KORPORAT
    coverage_limit: float
    effective_date: date
    expiry_date: date
    exclusions: Optional[list[str]] = None
    premi_bulanan: Optional[float] = None
    status: Optional[str] = "ACTIVE"
