from typing import Optional
from agentlens.contracts.run import Run
from agentlens.contracts.detector import DetectorResult, Evidence, FailureType, Severity

def detect_tool_loop(run: Run) -> Optional[DetectorResult]:
    if not run.events:
        return None

    segments = []
    current_tool = None
    current_tally = 0
    current_events = []

    def flush_segment():
        if current_tally >= 4 and current_tool is not None:
            segments.append((current_tool, current_tally, current_events.copy()))

    for event in run.events:
        tool = event.tool
        if not tool:
            flush_segment()
            current_tool = None
            current_tally = 0
            current_events = []
            continue

        if current_tool == tool:
            current_tally += 1
            current_events.append(event)
        else:
            flush_segment()
            current_tool = tool
            current_tally = 1
            current_events = [event]
            
    flush_segment()

    if not segments:
        return None

    all_evidence = []
    max_repetition = 0
    looped_tools = []
    
    for tool, tally, evs in segments:
        looped_tools.append(tool)
        if tally > max_repetition:
            max_repetition = tally
        for ev in evs:
            all_evidence.append(Evidence(
                source_run_id=run.run_id,
                event_sequence=ev.seq,
                tool_name=ev.tool,
                event_type=ev.type,
                message=f"Consecutive looped tool: {tool}",
                metric_value=float(tally)
            ))

    return DetectorResult(
        run_id=run.run_id,
        failure_type=FailureType.TOOL_LOOP,
        severity=Severity.HIGH,
        confidence=1.0,
        evidence=all_evidence,
        metrics={
            "repetition_count": max_repetition,
            "looped_tool": looped_tools[0] if looped_tools else ""
        }
    )
