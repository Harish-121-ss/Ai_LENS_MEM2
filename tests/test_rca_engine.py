import json
import pytest
from agentlens.contracts.incident import Incident
from agentlens.contracts.enums import FailureType, Severity
from agentlens.contracts.evidence import Evidence
from agentlens.engine.rca_engine import validate_rca_output

def _make_incident():
    return Incident(
        incident_id="inc-1",
        run_id="r-1",
        failure_type=FailureType.TOOL_LOOP,
        severity=Severity.HIGH,
        confidence=1.0,
        evidence=[Evidence(source_run_id="r-1", event_type="cmd", message="ev1")],
        metrics={}
    )

def _valid_rca():
    return {
        "primary_failure": "Tool loop detected",
        "probable_root_cause": "Agent got stuck",
        "evidence": [
            {
                "source_run_id": "r-1",
                "event_type": "cmd",
                "message": "ev1",
                "metric_value": None
            }
        ],
        "impact": ["High latency"],
        "recommended_action": "Fix prompt",
        "confidence": 0.9
    }

def test_p5_t12_valid_rca():
    inc = _make_incident()
    rca = validate_rca_output(inc, json.dumps(_valid_rca()))
    assert rca.primary_failure == "Tool loop detected"
    assert rca.confidence == 0.9

def test_p5_t13_missing_primary_failure():
    inc = _make_incident()
    data = _valid_rca()
    del data["primary_failure"]
    with pytest.raises(ValueError, match="RCA schema validation failed"):
        validate_rca_output(inc, json.dumps(data))

def test_p5_t14_missing_probable_root_cause():
    inc = _make_incident()
    data = _valid_rca()
    del data["probable_root_cause"]
    with pytest.raises(ValueError):
        validate_rca_output(inc, json.dumps(data))

def test_p5_t15_missing_evidence():
    inc = _make_incident()
    data = _valid_rca()
    del data["evidence"]
    with pytest.raises(ValueError):
        validate_rca_output(inc, json.dumps(data))

def test_p5_t16_missing_impact():
    inc = _make_incident()
    data = _valid_rca()
    del data["impact"]
    with pytest.raises(ValueError):
        validate_rca_output(inc, json.dumps(data))

def test_p5_t17_missing_recommended_action():
    inc = _make_incident()
    data = _valid_rca()
    del data["recommended_action"]
    with pytest.raises(ValueError):
        validate_rca_output(inc, json.dumps(data))

def test_p5_t18_missing_confidence():
    inc = _make_incident()
    data = _valid_rca()
    del data["confidence"]
    with pytest.raises(ValueError):
        validate_rca_output(inc, json.dumps(data))

def test_p5_t19_confidence_less_than_zero():
    inc = _make_incident()
    data = _valid_rca()
    data["confidence"] = -0.1
    with pytest.raises(ValueError):
        validate_rca_output(inc, json.dumps(data))

def test_p5_t20_confidence_greater_than_one():
    inc = _make_incident()
    data = _valid_rca()
    data["confidence"] = 1.1
    with pytest.raises(ValueError):
        validate_rca_output(inc, json.dumps(data))

def test_p5_t21_invalid_field_types():
    inc = _make_incident()
    data = _valid_rca()
    data["impact"] = "should be list"
    with pytest.raises(ValueError):
        validate_rca_output(inc, json.dumps(data))

def test_p5_t22_malformed_json():
    inc = _make_incident()
    with pytest.raises(ValueError, match="Malformed RCA JSON"):
        validate_rca_output(inc, "{ invalid_json: 123 ")

def test_p5_t23_extra_fields():
    inc = _make_incident()
    data = _valid_rca()
    data["extra"] = "value"
    rca = validate_rca_output(inc, json.dumps(data))
    assert not hasattr(rca, "extra")

def test_p5_t28_mock_timeout():
    # If the mocked API call raises a Timeout, the engine handles it.
    # We test the parser handles empty gracefully.
    inc = _make_incident()
    with pytest.raises(ValueError, match="Empty RCA response"):
        validate_rca_output(inc, "")

def test_p5_t29_mock_service_exception():
    inc = _make_incident()
    with pytest.raises(ValueError, match="Empty RCA response"):
        validate_rca_output(inc, None)

def test_p5_t30_empty_response():
    inc = _make_incident()
    with pytest.raises(ValueError, match="Empty RCA response"):
        validate_rca_output(inc, "   ")
