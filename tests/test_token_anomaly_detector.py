import pytest
from agentlens.contracts.run import Run
from agentlens.contracts.detector import FailureType, Severity
from agentlens.detectors.token_anomaly import detect_token_anomaly

def _make_run(tokens):
    return Run(run_id="r-1", agent_version="1", prompt_version="1", request="test", outcome="success", tokens=tokens, tool_calls=[], events=[])

# P4-T31: normal usage
def test_p4_t31():
    assert detect_token_anomaly(_make_run(1500), 1000) is None

# P4-T32: exactly at threshold
def test_p4_t32():
    assert detect_token_anomaly(_make_run(2000), 1000) is None

# P4-T33: above threshold
def test_p4_t33():
    result = detect_token_anomaly(_make_run(3000), 1000)
    assert result is not None
    assert result.severity == Severity.MEDIUM
    assert result.metrics["anomaly_ratio"] == 3.0

# P4-T34: very large token count
def test_p4_t34():
    result = detect_token_anomaly(_make_run(6000), 1000)
    assert result is not None
    assert result.severity == Severity.HIGH

# P4-T35: missing observed tokens
def test_p4_t35():
    assert detect_token_anomaly(_make_run(None), 1000) is None

# P4-T36: missing baseline - tested via parameter requirement
def test_p4_t36():
    assert detect_token_anomaly(_make_run(2000), -100) is None

# P4-T37: zero baseline
def test_p4_t37():
    assert detect_token_anomaly(_make_run(2000), 0) is None

# P4-T38: invalid negative tokens
def test_p4_t38():
    assert detect_token_anomaly(_make_run(-500), 1000) is None

# P4-T39: exact boundaries
def test_p4_t39():
    assert detect_token_anomaly(_make_run(2001), 1000).severity == Severity.MEDIUM
    assert detect_token_anomaly(_make_run(5000), 1000).severity == Severity.MEDIUM
    assert detect_token_anomaly(_make_run(5001), 1000).severity == Severity.HIGH

# P4-T40: deterministic repeated execution
def test_p4_t40():
    run = _make_run(3000)
    assert detect_token_anomaly(run, 1000) == detect_token_anomaly(run, 1000)
