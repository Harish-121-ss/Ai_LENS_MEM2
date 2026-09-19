import pytest
from pydantic import ValidationError
from agentlens.contracts.incident import Incident
from agentlens.contracts.enums import FailureType, Severity
from agentlens.contracts.evidence import Evidence
from agentlens.contracts.rca import RCAOutput

def test_p2_t09_incident_validation():
    inc = Incident(
        incident_id="inc-1",
        run_id="r-123",
        failure_type=FailureType.TOOL_LOOP,
        severity=Severity.HIGH,
        confidence=1.0,
        evidence=[],
        metrics={"count": 5}
    )
    assert inc.incident_id == "inc-1"

def test_p2_t10_incident_evidence_preservation():
    ev = Evidence(source_run_id="r-123", event_type="cmd", message="err")
    inc = Incident(
        incident_id="inc-1",
        run_id="r-123",
        failure_type=FailureType.TOOL_LOOP,
        severity=Severity.HIGH,
        confidence=1.0,
        evidence=[ev],
        metrics={}
    )
    assert len(inc.evidence) == 1
    assert inc.evidence[0].message == "err"
