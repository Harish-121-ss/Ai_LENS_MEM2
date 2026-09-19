import pytest
from agentlens.contracts.run import Run
from agentlens.contracts.detector import DetectorResult
from agentlens.contracts.enums import FailureType, Severity
from agentlens.contracts.evidence import Evidence
from agentlens.engine.incident_engine import process_detector_results

def _make_run():
    return Run(run_id="r-1", agent_version="1", prompt_version="1", request="test", outcome="success", tool_calls=[], events=[])

def _make_result(failure_type=FailureType.TOOL_LOOP, ev_msg="ev1"):
    return DetectorResult(
        failure_type=failure_type,
        severity=Severity.HIGH,
        confidence=1.0,
        evidence=[Evidence(source_run_id="r-1", event_type="cmd", message=ev_msg)],
        metrics={"count": 1}
    )

def test_p5_t01_map_valid_detectorresult():
    run = _make_run()
    res = _make_result()
    incidents = process_detector_results(run, [res])
    assert len(incidents) == 1
    assert incidents[0].run_id == "r-1"
    assert incidents[0].failure_type == FailureType.TOOL_LOOP
    assert incidents[0].severity == Severity.HIGH
    assert incidents[0].confidence == 1.0
    assert incidents[0].metrics == {"count": 1}

def test_p5_t02_missing_fields():
    # If the engine cannot find expected fields, we test a malformed detector result
    run = _make_run()
    class BadResult:
        failure_type = FailureType.TOOL_LOOP
    with pytest.raises(Exception):
        process_detector_results(run, [BadResult()])

def test_p5_t03_multiple_different_results():
    run = _make_run()
    res1 = _make_result(FailureType.TOOL_LOOP)
    res2 = _make_result(FailureType.TIMEOUT_RETRY)
    incidents = process_detector_results(run, [res1, res2])
    assert len(incidents) == 2

def test_p5_t04_identical_duplicate():
    run = _make_run()
    res1 = _make_result(FailureType.TOOL_LOOP, "ev1")
    res2 = _make_result(FailureType.TOOL_LOOP, "ev1")
    incidents = process_detector_results(run, [res1, res2])
    assert len(incidents) == 1
    assert len(incidents[0].evidence) == 1

def test_p5_t05_duplicate_failure_merge():
    run = _make_run()
    res1 = _make_result(FailureType.TOOL_LOOP, "ev1")
    res2 = _make_result(FailureType.TOOL_LOOP, "ev2")
    incidents = process_detector_results(run, [res1, res2])
    assert len(incidents) == 1
    assert len(incidents[0].evidence) == 2

def test_p5_t06_empty_input():
    run = _make_run()
    assert process_detector_results(run, []) == []

def test_p5_t07_invalid_detectorresult():
    run = _make_run()
    class BadResult:
        pass
    with pytest.raises(ValueError):
        process_detector_results(run, [BadResult()])

def test_p5_t08_invalid_failure_type():
    run = _make_run()
    class BadResult:
        failure_type = "NOT_A_VALID_TYPE"
    # Pydantic will fail when Incident is constructed with invalid enum string
    with pytest.raises(Exception):
        process_detector_results(run, [BadResult()])

def test_p5_t09_deterministic_id():
    run = _make_run()
    res = _make_result(FailureType.WRONG_TOOL)
    incidents = process_detector_results(run, [res])
    assert incidents[0].incident_id == "inc-r-1-WRONG_TOOL"

def test_p5_t10_provenance():
    run = _make_run()
    res = _make_result(FailureType.TOOL_LOOP, "ev1")
    incidents = process_detector_results(run, [res])
    assert incidents[0].evidence[0].source_run_id == "r-1"
    assert incidents[0].evidence[0].message == "ev1"

def test_p5_t11_scale():
    run = _make_run()
    evs = [Evidence(source_run_id="r-1", event_type="cmd", message=f"ev{i}") for i in range(100)]
    res = DetectorResult(
        failure_type=FailureType.TOOL_LOOP,
        severity=Severity.HIGH,
        confidence=1.0,
        evidence=evs,
        metrics={"count": 100}
    )
    incidents = process_detector_results(run, [res])
    assert len(incidents[0].evidence) == 100
