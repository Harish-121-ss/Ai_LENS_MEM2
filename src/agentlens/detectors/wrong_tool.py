from typing import Optional
from agentlens.contracts.run import Run
from agentlens.contracts.detector import DetectorResult, Evidence, FailureType, Severity
from agentlens.detectors.common import normalize_string

EXPECTED_TOOLS = {
    "where is order #8271?": "get_order"
}

def detect_wrong_tool(run: Run) -> Optional[DetectorResult]:
    if not run.request or not run.events:
        return None
        
    normalized_request = normalize_string(run.request)
    
    if normalized_request not in EXPECTED_TOOLS:
        return None
        
    expected_tool = EXPECTED_TOOLS[normalized_request]
    evidence = []
    actual_tools = []
    
    for event in run.events:
        if not event.tool:
            continue
        normalized_tool = normalize_string(event.tool)
        if normalized_tool != expected_tool:
            actual_tools.append(event.tool)
            evidence.append(Evidence(
                source_run_id=run.run_id,
                event_sequence=event.seq,
                tool_name=event.tool,
                event_type=event.type,
                message=f"Expected {expected_tool} but found {event.tool}",
                metric_value=None
            ))
            
    if not evidence:
        return None
        
    return DetectorResult(
        run_id=run.run_id,
        failure_type=FailureType.WRONG_TOOL,
        severity=Severity.HIGH,
        confidence=1.0,
        evidence=evidence,
        metrics={
            "expected_tool": expected_tool,
            "actual_tool": actual_tools[0] if actual_tools else ""
        }
    )
