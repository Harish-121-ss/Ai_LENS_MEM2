from pydantic import BaseModel, ConfigDict
from typing import Optional

class Evidence(BaseModel):
    model_config = ConfigDict(frozen=True)

    source_run_id: str
    event_sequence: Optional[int] = None
    tool_name: Optional[str] = None
    event_type: str
    message: str
    metric_value: Optional[float] = None
