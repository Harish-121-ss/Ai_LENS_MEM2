import pytest
from pydantic import ValidationError
from agentlens.contracts.events import AgentToolEvent

def test_p2_t03_agenttoolevent_valid_construction():
    evt = AgentToolEvent(seq=1, type="cmd", timestamp_ms=123456)
    assert evt.seq == 1

def test_p2_t04_agenttoolevent_sequence_validation():
    with pytest.raises(ValidationError):
        AgentToolEvent(seq=-1, type="cmd", timestamp_ms=123456)
