import pytest
from agentlens.contracts.run import Run
from agentlens.contracts.events import AgentToolEvent
from agentlens.contracts.detector import FailureType, Severity
from agentlens.detectors.tool_loop import detect_tool_loop

def _make_run(tools):
    events = [AgentToolEvent(seq=i, type="tool_call", timestamp_ms=1000, tool=t) for i, t in enumerate(tools)]
    return Run(
        run_id="r-1", agent_version="1", prompt_version="1", request="test", 
        outcome="success", events=events, tool_calls=[]
    )

# P4-T01: exactly 3 calls → no detection
def test_p4_t01():
    assert detect_tool_loop(_make_run(["A", "A", "A"])) is None

# P4-T02: exactly 4 calls → detection
def test_p4_t02():
    result = detect_tool_loop(_make_run(["A", "A", "A", "A"]))
    assert result is not None
    assert result.failure_type == FailureType.TOOL_LOOP
    assert result.metrics["repetition_count"] == 4
    assert len(result.evidence) == 4

# P4-T03: 5+ calls → detection
def test_p4_t03():
    result = detect_tool_loop(_make_run(["A", "A", "A", "A", "A"]))
    assert result is not None
    assert result.metrics["repetition_count"] == 5
    assert len(result.evidence) == 5

# P4-T04: separated by other tools
def test_p4_t04():
    assert detect_tool_loop(_make_run(["A", "B", "A", "A", "A"])) is None

# P4-T05: multiple segments
def test_p4_t05():
    result = detect_tool_loop(_make_run(["A", "A", "A", "A", "B", "B", "B", "B"]))
    assert result is not None
    assert result.metrics["repetition_count"] == 4
    assert len(result.evidence) == 8 # 4 for A, 4 for B

# P4-T06: duplicate sequence numbers
def test_p4_t06():
    run = _make_run(["A", "A", "A", "A"])
    for e in run.events:
        object.__setattr__(e, 'seq', 0)
    result = detect_tool_loop(run)
    assert result is not None

# P4-T07: empty tool calls
def test_p4_t07():
    assert detect_tool_loop(_make_run([])) is None

# P4-T08: missing tool names
def test_p4_t08():
    assert detect_tool_loop(_make_run([None, None, None, None])) is None

# P4-T09: malformed (irrelevant as contracts prevent, but tested via None tool)
def test_p4_t09():
    assert detect_tool_loop(_make_run(["A", None, "A", "A", "A"])) is None

# P4-T10: deterministic repeated execution
def test_p4_t10():
    run = _make_run(["A", "A", "A", "A"])
    assert detect_tool_loop(run) == detect_tool_loop(run)
