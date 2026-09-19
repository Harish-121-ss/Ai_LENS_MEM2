from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Dict, Any, List
from .events import AgentToolEvent

class Run(BaseModel):
    model_config = ConfigDict(frozen=True)

    run_id: str
    agent_version: str
    prompt_version: str
    request: str
    events: List[AgentToolEvent]
    tool_calls: List[Dict[str, Any]]
    tokens: Optional[int] = None
    latency_ms: Optional[int] = None
    errors: List[str] = Field(default_factory=list)
    outcome: str
    detected_failures: List[str] = Field(default_factory=list)
