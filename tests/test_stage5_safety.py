import json
import pytest
from unittest.mock import patch
from agentlens.contracts.incident import Incident
from agentlens.contracts.enums import FailureType, Severity
from agentlens.engine.rca_engine import validate_rca_output
from agentlens.engine.incident_engine import process_detector_results
from agentlens.normalization.normalizer import normalize_run
from agentlens.detectors.timeout_retry import detect_timeout_retry
from agentlens.detectors.tool_loop import detect_tool_loop
from agentlens.detectors.wrong_tool import detect_wrong_tool
from agentlens.detectors.token_anomaly import detect_token_anomaly
import os

def test_p5_t39_no_network_access():
    with patch("socket.socket") as mock_socket:
        # Simulate an execution that should not hit the network.
        # This will raise an error if any standard library socket call is made.
        mock_socket.side_effect = Exception("Network access is forbidden during Stage 5 tests")
        
        inc = Incident(
            incident_id="inc-1",
            run_id="r-1",
            failure_type=FailureType.TOOL_LOOP,
            severity=Severity.HIGH,
            confidence=1.0,
            evidence=[],
            metrics={}
        )
        data = {
            "primary_failure": "Tool timeout",
            "probable_root_cause": "Timeout",
            "evidence": [],
            "impact": ["High latency"],
            "recommended_action": "Fix",
            "confidence": 0.9
        }
        validate_rca_output(inc, json.dumps(data))
        
        # Verify socket was never called
        mock_socket.assert_not_called()

def test_p5_t40_no_aws_credentials():
    assert "AWS_ACCESS_KEY_ID" not in os.environ or os.environ["AWS_ACCESS_KEY_ID"] == ""
    assert "AWS_SECRET_ACCESS_KEY" not in os.environ or os.environ["AWS_SECRET_ACCESS_KEY"] == ""

def test_p5_t41_immutability():
    inc = Incident(
        incident_id="inc-1",
        run_id="r-1",
        failure_type=FailureType.TOOL_LOOP,
        severity=Severity.HIGH,
        confidence=1.0,
        evidence=[],
        metrics={}
    )
    # Pydantic frozen=True prevents mutation, so we verify this raises ValidationError
    with pytest.raises(Exception):
        inc.severity = Severity.MEDIUM

def test_p5_t42_no_filesystem_mutation(tmp_path):
    # Just a placeholder test verifying the engine doesn't write files.
    # We can check by running it and ensuring our tmp_path remains empty.
    inc = Incident(
        incident_id="inc-1",
        run_id="r-1",
        failure_type=FailureType.TOOL_LOOP,
        severity=Severity.HIGH,
        confidence=1.0,
        evidence=[],
        metrics={}
    )
    data = {
        "primary_failure": "Tool timeout",
        "probable_root_cause": "Timeout",
        "evidence": [],
        "impact": [],
        "recommended_action": "Fix",
        "confidence": 0.9
    }
    validate_rca_output(inc, json.dumps(data))
    assert len(list(tmp_path.iterdir())) == 0

def test_p5_t43_regression_tests():
    # End-to-end regression test verifying Stages 3 -> 4 -> 5 pipeline
    # 1. Normalization (Stage 3)
    raw_telemetry = {
        "run_id": "r-regress-1",
        "agent_version": "1.0",
        "prompt_version": "1.0",
        "request": "Do something",
        "events": [
            {
                "timestamp_ms": 1000,
                "type": "tool_call",
                "seq": 1,
                "tool": "get_order",
                "arguments": {"order_id": "123"},
                "status": "error",
                "result": "timeout"
            },
            {
                "timestamp_ms": 2000,
                "type": "tool_call",
                "seq": 2,
                "tool": "get_order",
                "arguments": {"order_id": "123"},
                "status": "error",
                "result": "timeout"
            }
        ],
        "outcome": "failure"
    }
    run = normalize_run(raw_telemetry)
    assert run.run_id == "r-regress-1"
    
    # 2. Detectors (Stage 4)
    all_results = []
    
    for res in [
        detect_timeout_retry(run),
        detect_tool_loop(run),
        detect_wrong_tool(run),
        detect_token_anomaly(run, 1000)
    ]:
        if res:
            all_results.append(res)
    
    # Assert timeout/retry detector found something (2 exact timeouts)
    assert len(all_results) >= 1
    
    # 3. Incident Engine (Stage 5)
    incidents = process_detector_results(run, all_results)
    assert len(incidents) >= 1
    assert incidents[0].run_id == "r-regress-1"
    assert incidents[0].incident_id.startswith("inc-r-regress-1")
    
    # Ensure evidence was preserved perfectly from normalizer -> detector -> incident
    assert len(incidents[0].evidence) > 0
    assert incidents[0].evidence[0].source_run_id == "r-regress-1"
    assert incidents[0].evidence[0].tool_name == "get_order"
