import pytest
from agentlens.contracts.run import Run
from agentlens.contracts.events import AgentToolEvent
from agentlens.detectors.tool_loop import detect_tool_loop
from agentlens.detectors.timeout_retry import detect_timeout_retry
from agentlens.detectors.wrong_tool import detect_wrong_tool
from agentlens.detectors.token_anomaly import detect_token_anomaly

def _make_complex_run():
    events = [
        AgentToolEvent(seq=0, type="tool_call", timestamp_ms=1000, tool="get_customer", status_result="error"),
        AgentToolEvent(seq=1, type="tool_call", timestamp_ms=2000, tool="get_customer", status_result="success"),
        AgentToolEvent(seq=2, type="tool_call", timestamp_ms=3000, tool="A"),
        AgentToolEvent(seq=3, type="tool_call", timestamp_ms=4000, tool="A"),
        AgentToolEvent(seq=4, type="tool_call", timestamp_ms=5000, tool="A"),
        AgentToolEvent(seq=5, type="tool_call", timestamp_ms=6000, tool="A"),
    ]
    return Run(
        run_id="r-1", agent_version="1", prompt_version="1", 
        request="where is order #8271?", outcome="success", 
        events=events, tokens=6000, tool_calls=[]
    )

# P4-T41: timeout + tool loop
def test_p4_t41():
    run = _make_complex_run()
    assert detect_timeout_retry(run) is not None
    assert detect_tool_loop(run) is not None

# P4-T42: wrong tool + token anomaly
def test_p4_t42():
    run = _make_complex_run()
    assert detect_wrong_tool(run) is not None
    assert detect_token_anomaly(run, 1000) is not None

# P4-T43: all four
def test_p4_t43():
    run = _make_complex_run()
    assert detect_timeout_retry(run) is not None
    assert detect_tool_loop(run) is not None
    assert detect_wrong_tool(run) is not None
    assert detect_token_anomaly(run, 1000) is not None

# P4-T45: immutability
def test_p4_t45():
    run = _make_complex_run()
    run_id = id(run)
    events_id = id(run.events)
    
    detect_timeout_retry(run)
    detect_tool_loop(run)
    detect_wrong_tool(run)
    detect_token_anomaly(run, 1000)
    
    assert id(run) == run_id
    assert id(run.events) == events_id
