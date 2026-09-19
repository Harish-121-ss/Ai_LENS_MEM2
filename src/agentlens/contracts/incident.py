from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Dict, Any
from .enums import FailureType, Severity
from .evidence import Evidence
from .rca import RCAOutput

class Incident(BaseModel):
    model_config = ConfigDict(frozen=True)

    incident_id: str
    run_id: str
    failure_type: FailureType
    severity: Severity
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: List[Evidence]
    metrics: Dict[str, Any]
    rca_status: Optional[str] = None
    rca_output: Optional[RCAOutput] = None
    recommended_fix: Optional[str] = None
