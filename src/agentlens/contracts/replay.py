from pydantic import BaseModel, ConfigDict
from typing import Dict, Any, List

class ReplayRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

    run_id: str
    prompt: str
    agent_version: str
    prompt_version: str
    failure_mode: str
    tool_calls: List[Dict[str, Any]]
    mocked_responses: List[Dict[str, Any]]
    expected_behavior: str
    original_incident_id: str
