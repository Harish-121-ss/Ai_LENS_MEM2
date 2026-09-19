import pytest
from pydantic import ValidationError
from agentlens.contracts.run import Run
from agentlens.contracts.events import AgentToolEvent

def test_p2_t01_run_valid_construction():
    run = Run(
        run_id="r-123",
        agent_version="v1.0",
        prompt_version="p-2",
        request="Do something",
        events=[],
        tool_calls=[],
        outcome="SUCCESS"
    )
    assert run.run_id == "r-123"

def test_p2_t02_run_required_field_validation():
    with pytest.raises(ValidationError) as exc_info:
        Run(
            agent_version="v1.0",
            prompt_version="p-2",
            request="Do something",
            events=[],
            tool_calls=[],
            outcome="SUCCESS"
        )
    assert "run_id" in str(exc_info.value)

def test_p2_t05_event_ordering():
    evt1 = AgentToolEvent(seq=1, type="cmd", timestamp_ms=100)
    evt2 = AgentToolEvent(seq=2, type="msg", timestamp_ms=101)
    run = Run(
        run_id="r-123",
        agent_version="v1.0",
        prompt_version="p-2",
        request="req",
        events=[evt1, evt2],
        tool_calls=[],
        outcome="SUCCESS"
    )
    assert run.events[0].seq == 1
    assert run.events[1].seq == 2

def test_p2_t16_run_id_preservation():
    run = Run(
        run_id="r-123",
        agent_version="v1.0",
        prompt_version="p-2",
        request="req",
        events=[],
        tool_calls=[],
        outcome="SUCCESS"
    )
    assert run.run_id == "r-123"
