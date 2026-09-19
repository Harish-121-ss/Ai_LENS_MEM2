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
    import os
    from agentlens.engine.rca_engine import generate_and_validate_rca
    from agentlens.engine.rca_provider import MockBedrockProvider
    
    # Snapshot initial working directory contents
    work_dir = os.getcwd()
    initial_files = set(os.listdir(work_dir))
    
    # Execute full RCA pipeline
    inc = Incident(
        incident_id="inc-1",
        run_id="r-1",
        failure_type=FailureType.TOOL_LOOP,
        severity=Severity.HIGH,
        confidence=1.0,
        evidence=[],
        metrics={}
    )
    
    mock_provider = MockBedrockProvider(
        response_mock=json.dumps({
            "primary_failure": "Tool timeout",
            "probable_root_cause": "Timeout",
            "evidence": [],
            "impact": [],
            "recommended_action": "Fix",
            "confidence": 0.9
        })
    )
    
    generate_and_validate_rca(inc, mock_provider)
    
    # Snapshot final working directory contents
    final_files = set(os.listdir(work_dir))
    
    assert initial_files == final_files, "Unexpected files were created during RCA pipeline execution"


def test_p5_t43_canonical_timeout_retry_regression():
    raw_telemetry = {
        "run_id": "r-timeout-canonical",
        "agent_version": "1.0",
        "prompt_version": "1.0",
        "request": "Do something",
        "events": [
            {
                "timestamp_ms": 1000,
                "type": "tool_call",
                "seq": 1,
                "tool": "fetch_data",
                "arguments": {"id": "x"},
                "status": "error",
                "result": "timeout"
            },
            {
                "timestamp_ms": 2000,
                "type": "tool_call",
                "seq": 2,
                "tool": "fetch_data",
                "arguments": {"id": "x"},
                "status": "error",
                "result": "timeout"
            }
        ],
        "outcome": "failure"
    }
    
    # Normalizer (Stage 3)
    run = normalize_run(raw_telemetry)
    assert run.run_id == "r-timeout-canonical"
    
    # Detectors (Stage 4)
    all_results = []
    for detect_func in [detect_timeout_retry, detect_tool_loop, detect_wrong_tool, detect_token_anomaly]:
        res = detect_func(run) if detect_func != detect_token_anomaly else detect_func(run, 1000)
        if res:
            all_results.append(res)
    
    # Verify exact detector result
    assert len(all_results) == 1
    det = all_results[0]
    assert det.failure_type == FailureType.TIMEOUT_RETRY
    assert det.severity == Severity.MEDIUM
    assert len(det.evidence) == 2
    assert det.metrics["retry_count"] == 1
    assert det.metrics["timeout_count"] == 1
    
    # Incident Engine (Stage 5)
    incidents = process_detector_results(run, all_results)
    assert len(incidents) == 1
    inc = incidents[0]
    
    # Explicitly verify Incident properties
    assert inc.run_id == run.run_id
    assert inc.failure_type == det.failure_type
    assert len(inc.evidence) == len(det.evidence)
    assert inc.metrics == det.metrics
    assert inc.incident_id == f"inc-{run.run_id}-{FailureType.TIMEOUT_RETRY.value}"
    assert inc.rca_status == "PENDING"
