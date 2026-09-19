import pytest
from pydantic import ValidationError
from agentlens.contracts.detector import DetectorResult
from agentlens.contracts.enums import FailureType, Severity
from agentlens.contracts.evidence import Evidence
from agentlens.contracts.events import AgentToolEvent

def test_p2_t07_detectorresult_validation():
    ev = Evidence(source_run_id="r-123", event_type="cmd", message="failed")
    dr = DetectorResult(
        failure_type=FailureType.TOOL_LOOP,
        severity=Severity.HIGH,
        confidence=0.9,
        evidence=[ev],
        metrics={"repetition_count": 4}
    )
    assert dr.failure_type == FailureType.TOOL_LOOP

def test_p2_t08_invalid_detectorresult():
    with pytest.raises(ValidationError):
        DetectorResult(
            failure_type="UNKNOWN_TYPE",
            severity=Severity.HIGH,
            confidence=0.9,
            evidence=[],
            metrics={}
        )

def test_p2_t17_evidence_traceability():
    ev = Evidence(source_run_id="r-123", event_sequence=4, event_type="cmd", message="err")
    assert ev.event_sequence == 4
    assert ev.source_run_id == "r-123"
