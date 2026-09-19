import pytest
from agentlens.contracts.run import Run
from agentlens.contracts.events import AgentToolEvent
from agentlens.contracts.detector import FailureType, Severity
from agentlens.detectors.timeout_retry import detect_timeout_retry

def _make_run(statuses):
    events = []
    for i, (tool, status) in enumerate(statuses):
        events.append(AgentToolEvent(seq=i, type="tool_call", timestamp_ms=1000, tool=tool, status_result=status))
    return Run(run_id="r-1", agent_version="1", prompt_version="1", request="test", outcome="success", events=events, tool_calls=[])

# P4-T11: timeout with no retry
def test_p4_t11():
    assert detect_timeout_retry(_make_run([("A", "timeout"), ("B", "success")])) is None

# P4-T12: timeout + 1 retry
def test_p4_t12():
    result = detect_timeout_retry(_make_run([("A", "timeout"), ("A", "success")]))
    assert result is not None
    assert result.severity == Severity.MEDIUM
    assert result.metrics["retry_count"] == 1

# P4-T13: timeout + multiple retries
def test_p4_t13():
    result = detect_timeout_retry(_make_run([("A", "timeout"), ("A", "timeout"), ("A", "success")]))
    assert result is not None
    assert result.severity == Severity.HIGH
    assert result.metrics["retry_count"] == 2

# P4-T14: timeout at retry limit
def test_p4_t14():
    result = detect_timeout_retry(_make_run([("A", "timeout"), ("A", "timeout"), ("A", "timeout")]))
    assert result is not None
    assert result.severity == Severity.HIGH
    assert result.metrics["retry_count"] == 2

# P4-T15: repeated tool calls without timeout
def test_p4_t15():
    assert detect_timeout_retry(_make_run([("A", "success"), ("A", "success")])) is None

# P4-T16: missing latency
def test_p4_t16():
    result = detect_timeout_retry(_make_run([("A", "timeout"), ("A", "success")]))
    assert result is not None

# P4-T17: missing error info
def test_p4_t17():
    assert detect_timeout_retry(_make_run([("A", None), ("A", None)])) is None

# P4-T18: multiple tools
def test_p4_t18():
    result = detect_timeout_retry(_make_run([("A", "timeout"), ("A", "success"), ("B", "timeout"), ("B", "error")]))
    assert result is not None
    assert result.metrics["retry_count"] == 2

# P4-T19: malformed telemetry
def test_p4_t19():
    assert detect_timeout_retry(_make_run([])) is None

# P4-T20: deterministic results
def test_p4_t20():
    run = _make_run([("A", "timeout"), ("A", "success")])
    assert detect_timeout_retry(run) == detect_timeout_retry(run)
