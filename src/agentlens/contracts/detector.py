from pydantic import BaseModel, ConfigDict, Field
from typing import List, Dict, Any
from .enums import FailureType, Severity
from .evidence import Evidence

class DetectorResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    failure_type: FailureType
    severity: Severity
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: List[Evidence]
    metrics: Dict[str, Any]
