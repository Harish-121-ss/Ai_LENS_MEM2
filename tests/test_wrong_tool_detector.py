import pytest
from agentlens.contracts.run import Run
from agentlens.contracts.events import AgentToolEvent
from agentlens.contracts.detector import FailureType, Severity
from agentlens.detectors.wrong_tool import detect_wrong_tool

def _make_run(request, tools):
    events = [AgentToolEvent(seq=i, type="tool_call", timestamp_ms=1000, tool=t) for i, t in enumerate(tools)]
    return Run(run_id="r-1", agent_version="1", prompt_version="1", request=request, outcome="success", events=events, tool_calls=[])

# P4-T21: expected tool called -> no detection
def test_p4_t21():
    assert detect_wrong_tool(_make_run("where is order #8271?", ["get_order"])) is None

# P4-T22: wrong tool called -> detection
def test_p4_t22():
    result = detect_wrong_tool(_make_run("where is order #8271?", ["get_customer"]))
    assert result is not None
    assert result.failure_type == FailureType.WRONG_TOOL

# P4-T23: multiple tool calls
def test_p4_t23():
    result = detect_wrong_tool(_make_run("where is order #8271?", ["get_customer", "get_order"]))
    assert result is not None
    assert result.metrics["actual_tool"] == "get_customer"
    assert len(result.evidence) == 1

# P4-T24: missing expected tool in config
def test_p4_t24():
    assert detect_wrong_tool(_make_run("unmapped intent", ["get_order"])) is None

# P4-T25: unknown tool called
def test_p4_t25():
    assert detect_wrong_tool(_make_run("where is order #8271?", ["unknown_tool"])) is not None

# P4-T26: empty tool call list
def test_p4_t26():
    assert detect_wrong_tool(_make_run("where is order #8271?", [])) is None

# P4-T27: malformed tool name
def test_p4_t27():
    assert detect_wrong_tool(_make_run("where is order #8271?", [None])) is None

# P4-T28: deterministic classification
def test_p4_t28():
    run = _make_run("where is order #8271?", ["get_customer"])
    assert detect_wrong_tool(run) == detect_wrong_tool(run)

# P4-T29: case insensitive check
def test_p4_t29():
    assert detect_wrong_tool(_make_run(" WHERE Is ORDER #8271? ", [" GET_Order "])) is None

# P4-T30: missing request string
def test_p4_t30():
    assert detect_wrong_tool(_make_run("", ["get_order"])) is None
