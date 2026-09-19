import pytest
import json
import os
import re
from unittest.mock import patch
from agentlens.normalization.normalizer import normalize_run
from agentlens.normalization.errors import NormalizationError
from agentlens.contracts.run import Run
from agentlens.contracts.events import AgentToolEvent

def load_fixture(name):
    path = os.path.join(os.path.dirname(__file__), "fixtures", name)
    with open(path, "r") as f:
        return json.load(f)

# P3-T01: Valid normal telemetry normalizes successfully.
def test_p3_t01_valid_normal():
    raw = load_fixture("normal_run.json")
    run = normalize_run(raw)
    assert isinstance(run, Run)

# P3-T02: run_id is preserved exactly.
def test_p3_t02_run_id():
    raw = load_fixture("normal_run.json")
    run = normalize_run(raw)
    assert run.run_id == "r-norm-1"

# P3-T03: agent_version is preserved exactly.
def test_p3_t03_agent_version():
    raw = load_fixture("normal_run.json")
    run = normalize_run(raw)
    assert run.agent_version == "v1.2"

# P3-T04: prompt_version is preserved exactly.
def test_p3_t04_prompt_version():
    raw = load_fixture("normal_run.json")
    run = normalize_run(raw)
    assert run.prompt_version == "p-3"

# P3-T05: request is preserved exactly.
def test_p3_t05_request():
    raw = load_fixture("normal_run.json")
    run = normalize_run(raw)
    assert run.request == "Where is order #8271?"

# P3-T06: all valid events become AgentToolEvent objects.
def test_p3_t06_events():
    raw = load_fixture("normal_run.json")
    run = normalize_run(raw)
    assert len(run.events) == 1
    assert isinstance(run.events[0], AgentToolEvent)

# P3-T07: event sequence values are preserved.
def test_p3_t07_seq():
    raw = load_fixture("normal_run.json")
    run = normalize_run(raw)
    assert run.events[0].seq == 0

# P3-T08: event timestamps are preserved.
def test_p3_t08_timestamp():
    raw = load_fixture("normal_run.json")
    run = normalize_run(raw)
    assert run.events[0].timestamp_ms == 1000

# P3-T09: tool names are preserved.
def test_p3_t09_tool():
    raw = load_fixture("normal_run.json")
    run = normalize_run(raw)
    assert run.events[0].tool == "get_order"

# P3-T10: arguments are preserved.
def test_p3_t10_arguments():
    raw = load_fixture("normal_run.json")
    run = normalize_run(raw)
    assert run.events[0].arguments == {"order_id": "8271"}

# P3-T11: status/result information is preserved.
def test_p3_t11_status_result():
    raw = load_fixture("normal_run.json")
    run = normalize_run(raw)
    expected = 'Status: success | Result: {"status": "shipped"}'
    assert run.events[0].status_result == expected

# P3-T12: available latency is preserved.
def test_p3_t12_latency():
    raw = load_fixture("normal_run.json")
    run = normalize_run(raw)
    assert run.latency_ms == 800
    assert run.events[0].latency_ms == 150

# P3-T13: available token count is preserved.
def test_p3_t13_tokens():
    raw = load_fixture("normal_run.json")
    run = normalize_run(raw)
    assert run.tokens == 450

# P3-T14: missing latency remains None.
def test_p3_t14_missing_latency():
    raw = load_fixture("missing_optional_telemetry.json")
    run = normalize_run(raw)
    assert run.latency_ms is None
    assert run.events[0].latency_ms is None

# P3-T15: missing tokens remain None.
def test_p3_t15_missing_tokens():
    raw = load_fixture("missing_optional_telemetry.json")
    run = normalize_run(raw)
    assert run.tokens is None

# P3-T16: tool_calls are preserved.
def test_p3_t16_tool_calls():
    raw = load_fixture("normal_run.json")
    run = normalize_run(raw)
    assert run.tool_calls == [{"name": "get_order"}]

# P3-T17: errors are preserved.
def test_p3_t17_errors():
    raw = load_fixture("timeout_retry_run.json")
    run = normalize_run(raw)
    assert run.errors == ["timeout", "timeout", "timeout"]

# P3-T18: outcome is preserved.
def test_p3_t18_outcome():
    raw = load_fixture("timeout_retry_run.json")
    run = normalize_run(raw)
    assert run.outcome == "error"

# P3-T19: normalization does not invent detected failures.
def test_p3_t19_no_invented_failures():
    raw = load_fixture("timeout_retry_run.json")
    run = normalize_run(raw)
    assert run.detected_failures == []

# P3-T20: normalization does not execute detectors.
def test_p3_t20_no_detectors():
    raw = load_fixture("wrong_tool_run.json")
    run = normalize_run(raw)
    assert run.detected_failures == []

# P3-T21: timeout/retry telemetry is preserved.
def test_p3_t21_timeout_retry():
    raw = load_fixture("timeout_retry_run.json")
    run = normalize_run(raw)
    assert len(run.events) == 3
    assert run.events[0].status_result == 'Status: error | Result: timeout'

# P3-T22: wrong-tool telemetry is preserved.
def test_p3_t22_wrong_tool():
    raw = load_fixture("wrong_tool_run.json")
    run = normalize_run(raw)
    assert run.events[0].tool == "get_customer"

# P3-T23: token anomaly telemetry is preserved.
def test_p3_t23_token_anomaly():
    raw = load_fixture("token_anomaly_run.json")
    run = normalize_run(raw)
    assert run.tokens == 950000

# P3-T24: malformed required fields are rejected.
def test_p3_t24_malformed_required():
    raw_list = load_fixture("malformed_runs.json")
    with pytest.raises(NormalizationError):
        normalize_run(raw_list[0])

# P3-T25: negative event sequence is rejected.
def test_p3_t25_negative_seq():
    raw_list = load_fixture("malformed_runs.json")
    with pytest.raises(NormalizationError):
        normalize_run(raw_list[1])

# P3-T26: duplicate sequence behavior is deterministic.
def test_p3_t26_duplicate_seq():
    raw = load_fixture("normal_run.json")
    raw["events"].append(raw["events"][0])
    run = normalize_run(raw)
    assert len(run.events) == 2
    assert run.events[0].seq == 0
    assert run.events[1].seq == 0

# P3-T27: same raw input produces identical normalized output.
def test_p3_t27_deterministic_output():
    raw1 = load_fixture("normal_run.json")
    raw2 = load_fixture("normal_run.json")
    assert normalize_run(raw1) == normalize_run(raw2)

# P3-T28: JSON round-trip preserves normalized Run.
def test_p3_t28_json_round_trip():
    raw = load_fixture("normal_run.json")
    run1 = normalize_run(raw)
    run2 = Run.model_validate_json(run1.model_dump_json())
    assert run1 == run2

# P3-T29: synthetic fixtures contain no secrets.
def test_p3_t29_no_secrets():
    fixture_dir = os.path.join(os.path.dirname(__file__), "fixtures")
    patterns = [
        re.compile(r"AKIA[0-9A-Z]{16}"),
        re.compile(r"sk-[a-zA-Z0-9]{32,}"),
        re.compile(r"-----BEGIN RSA PRIVATE KEY-----"),
        re.compile(r"bearer [a-zA-Z0-9\-\._~+/]+", re.IGNORECASE)
    ]
    for filename in os.listdir(fixture_dir):
        if filename.endswith(".json"):
            with open(os.path.join(fixture_dir, filename), "r") as f:
                content = f.read()
                for p in patterns:
                    assert not p.search(content), f"Secret found in {filename}"

# P3-T30: normalization performs no network access.
@patch('socket.socket')
def test_p3_t30_zero_network_access(mock_socket):
    mock_socket.side_effect = Exception("Network access is strictly prohibited.")
    raw = load_fixture("normal_run.json")
    run = normalize_run(raw)
    assert run.run_id == "r-norm-1"
