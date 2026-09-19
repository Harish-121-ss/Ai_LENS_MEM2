from typing import Optional
from agentlens.contracts.run import Run
from agentlens.contracts.detector import DetectorResult, Evidence, FailureType, Severity

def detect_timeout_retry(run: Run) -> Optional[DetectorResult]:
    if not run.events:
        return None

    evidence = []
    retry_count = 0
    timeout_count = 0

    i = 0
    while i < len(run.events) - 1:
        event = run.events[i]
        next_event = run.events[i+1]
        
        status = (event.status_result or "").casefold()
        
        if ("timeout" in status or "error" in status) and event.tool:
            if event.tool == next_event.tool:
                timeout_count += 1
                retry_count += 1
                
                evidence.append(Evidence(
                    source_run_id=run.run_id,
                    event_sequence=event.seq,
                    tool_name=event.tool,
                    event_type=event.type,
                    message="Timeout/Error observed",
                    metric_value=None
                ))
                evidence.append(Evidence(
                    source_run_id=run.run_id,
                    event_sequence=next_event.seq,
                    tool_name=next_event.tool,
                    event_type=next_event.type,
                    message="Immediate retry observed",
                    metric_value=None
                ))
        i += 1

    if retry_count == 0:
        return None
        
    severity = Severity.MEDIUM if retry_count == 1 else Severity.HIGH

    return DetectorResult(
        run_id=run.run_id,
        failure_type=FailureType.TIMEOUT_RETRY,
        severity=severity,
        confidence=1.0,
        evidence=evidence,
        metrics={
            "retry_count": retry_count,
            "timeout_count": timeout_count
        }
    )
