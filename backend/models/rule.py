from pydantic import BaseModel
from typing import Optional


class RuleCreateRequest(BaseModel):
    rule_name: str
    rule_category: str  # ELIGIBILITY / COVERAGE_LIMIT / WAITING_PERIOD / EXCLUSION / DOCUMENTATION
    condition_expression: Optional[dict] = None
    action: str  # APPROVE / REJECT / FLAG
    priority: Optional[int] = 0
    is_active: Optional[bool] = True
    description: Optional[str] = None


class RuleUpdateRequest(BaseModel):
    rule_name: Optional[str] = None
    rule_category: Optional[str] = None
    condition_expression: Optional[dict] = None
    action: Optional[str] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None
    description: Optional[str] = None
