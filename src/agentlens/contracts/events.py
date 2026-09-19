from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Dict, Any

class AgentToolEvent(BaseModel):
    model_config = ConfigDict(frozen=True)

    seq: int = Field(ge=0)
    type: str
    timestamp_ms: int
    tool: Optional[str] = None
    arguments: Optional[Dict[str, Any]] = None
    status_result: Optional[str] = None
    latency_ms: Optional[int] = None
