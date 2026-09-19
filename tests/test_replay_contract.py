import pytest
from pydantic import ValidationError
from agentlens.contracts.replay import ReplayRecord

def test_p2_t06_replayrecord_validation():
    rec = ReplayRecord(
        run_id="r-123",
        prompt="hello",
        agent_version="v1.0",
        prompt_version="p-2",
        failure_mode="TOOL_LOOP",
        tool_calls=[],
        mocked_responses=[],
        expected_behavior="stop",
        original_incident_id="inc-1"
    )
    assert rec.run_id == "r-123"
