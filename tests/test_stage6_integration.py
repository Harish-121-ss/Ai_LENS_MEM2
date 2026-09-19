import json
import os
import copy
import pytest
from unittest.mock import patch

from agentlens.contracts.detector import FailureType, Severity
from agentlens.engine.rca_provider import MockBedrockProvider
from agentlens.engine.orchestrator import run_reliability_pipeline
from pydantic import ValidationError

def _load_fixture(name):
    with open(os.path.join(os.path.dirname(__file__), "fixtures", name)) as f:
        return json.load(f)

MOCKED_RCA_JSON = json.dumps({
    "primary_failure": "timeout_retry",
    "probable_root_cause": "The agent repeatedly encountered timeouts when calling get_order.",
    "evidence": [
        {
            "source_run_id": "r-to-1",
            "event_sequence": 0,
            "tool_name": "get_order",
            "event_type": "tool_call",
            "message": "Timeout/Error observed"
        },
        {
            "source_run_id": "r-to-1",
            "event_sequence": 1,
            "tool_name": "get_order",
            "event_type": "tool_call",
            "message": "Immediate retry observed"
        },
        {
            "source_run_id": "r-to-1",
            "event_sequence": 2,
            "tool_name": "get_order",
            "event_type": "tool_call",
            "message": "Immediate retry observed"
        }
    ],
    "impact": ["High latency", "Request failure"],
    "recommended_action": "Implement bounded retries with fallback.",
    "confidence": 0.95
})

# T6-01 - Canonical end-to-end reliability pipeline
def test_t6_01_canonical_pipeline():
    raw_execution = _load_fixture("timeout_retry_run.json")
    provider = MockBedrockProvider(response_mock=MOCKED_RCA_JSON)
    
    result = run_reliability_pipeline(raw_execution, provider)
    
    assert result.run.run_id == "r-to-1"
    assert len(result.incidents) == 1
    
    incident = result.incidents[0]
    assert incident.failure_type == FailureType.TIMEOUT_RETRY
    assert incident.incident_id in result.rca_outputs
    
    rca = result.rca_outputs[incident.incident_id]
    assert rca.primary_failure == "timeout_retry"

# T6-02 - Exact timeout/retry detection
def test_t6_02_exact_detection():
    raw_execution = _load_fixture("timeout_retry_run.json")
    provider = MockBedrockProvider(response_mock=MOCKED_RCA_JSON)
    
    result = run_reliability_pipeline(raw_execution, provider)
    incident = result.incidents[0]
    
    assert incident.failure_type == FailureType.TIMEOUT_RETRY
    assert incident.severity == Severity.HIGH
    assert incident.metrics["retry_count"] == 2
    assert incident.metrics["timeout_count"] == 2

# T6-03 - Incident traceability
def test_t6_03_incident_traceability():
    raw_execution = _load_fixture("timeout_retry_run.json")
    provider = MockBedrockProvider(response_mock=MOCKED_RCA_JSON)
    
    result = run_reliability_pipeline(raw_execution, provider)
    incident = result.incidents[0]
    
    assert incident.run_id == result.run.run_id
    assert len(incident.evidence) == 4

# T6-04 - RCA evidence traceability
def test_t6_04_rca_evidence_traceability():
    raw_execution = _load_fixture("timeout_retry_run.json")
    provider = MockBedrockProvider(response_mock=MOCKED_RCA_JSON)
    
    result = run_reliability_pipeline(raw_execution, provider)
    incident = result.incidents[0]
    rca = result.rca_outputs[incident.incident_id]
    
    assert len(rca.evidence) == 3
    for ev in rca.evidence:
        assert ev.source_run_id == incident.run_id

# T6-05 - Fabricated RCA evidence rejection
def test_t6_05_fabricated_evidence_rejection():
    raw_execution = _load_fixture("timeout_retry_run.json")
    fabricated_rca = json.dumps({
        "primary_failure": "timeout_retry",
        "probable_root_cause": "The agent repeatedly encountered timeouts when calling get_order.",
        "evidence": [
            {
                "source_run_id": "r-to-1",
                "event_sequence": 999,  # Fabricated!
                "tool_name": "get_order",
                "event_type": "tool_call",
                "message": "timeout"
            }
        ],
        "impact": ["High latency", "Request failure"],
        "recommended_action": "Implement bounded retries with fallback.",
        "confidence": 0.95
    })
    
    provider = MockBedrockProvider(response_mock=fabricated_rca)
    
    with pytest.raises(ValueError, match="Unsupported claim: RCA fabricated evidence"):
        run_reliability_pipeline(raw_execution, provider)

# T6-06 - Normal execution
def test_t6_06_normal_execution():
    raw_execution = _load_fixture("normal_run.json")
    provider = MockBedrockProvider(response_mock=MOCKED_RCA_JSON)
    
    result = run_reliability_pipeline(raw_execution, provider)
    assert len(result.incidents) == 0
    assert len(result.rca_outputs) == 0

# T6-07 - Deterministic repeated execution
def test_t6_07_deterministic_execution():
    raw_execution = _load_fixture("timeout_retry_run.json")
    provider = MockBedrockProvider(response_mock=MOCKED_RCA_JSON)
    
    result1 = run_reliability_pipeline(copy.deepcopy(raw_execution), provider)
    result2 = run_reliability_pipeline(copy.deepcopy(raw_execution), provider)
    
    assert result1.run.model_dump() == result2.run.model_dump()
    assert result1.incidents[0].model_dump() == result2.incidents[0].model_dump()
    incident_id = result1.incidents[0].incident_id
    assert result1.rca_outputs[incident_id].model_dump() == result2.rca_outputs[incident_id].model_dump()

# T6-08 - Immutability
def test_t6_08_immutability():
    raw_execution = _load_fixture("timeout_retry_run.json")
    provider = MockBedrockProvider(response_mock=MOCKED_RCA_JSON)
    
    result = run_reliability_pipeline(raw_execution, provider)
    
    with pytest.raises(ValidationError):
        result.run.run_id = "mutated"
        
    with pytest.raises(ValidationError):
        result.incidents[0].incident_id = "mutated"

# T6-09 - Local safety
@patch("socket.socket")
def test_t6_09_local_safety(mock_socket):
    mock_socket.side_effect = RuntimeError("Network access forbidden")
    
    raw_execution = _load_fixture("timeout_retry_run.json")
    provider = MockBedrockProvider(response_mock=MOCKED_RCA_JSON)
    
    run_reliability_pipeline(raw_execution, provider)

# T6-10 - Filesystem safety
def test_t6_10_filesystem_safety():
    before_files = set(os.listdir(os.getcwd()))
    
    raw_execution = _load_fixture("timeout_retry_run.json")
    provider = MockBedrockProvider(response_mock=MOCKED_RCA_JSON)
    
    run_reliability_pipeline(raw_execution, provider)
    
    after_files = set(os.listdir(os.getcwd()))
    assert before_files == after_files
