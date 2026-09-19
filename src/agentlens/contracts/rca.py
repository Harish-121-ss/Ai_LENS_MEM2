from pydantic import BaseModel, ConfigDict, Field
from typing import List
from .evidence import Evidence

class RCAOutput(BaseModel):
    model_config = ConfigDict(frozen=True)

    primary_failure: str
    probable_root_cause: str
    evidence: List[Evidence]
    impact: List[str]
    recommended_action: str
    confidence: float = Field(ge=0.0, le=1.0)
