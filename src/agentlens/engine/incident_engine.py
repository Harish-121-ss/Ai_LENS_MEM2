from typing import List, Dict, Any
from agentlens.contracts.run import Run
from agentlens.contracts.detector import DetectorResult
from agentlens.contracts.incident import Incident

def process_detector_results(run: Run, results: List[DetectorResult]) -> List[Incident]:
    if not results:
        return []

    incidents_by_id: Dict[str, Incident] = {}

    for result in results:
        if not hasattr(result, "failure_type"):
            raise ValueError("Invalid DetectorResult: missing failure_type")
        
        inc_id = f"inc-{run.run_id}-{result.failure_type.value}"

        if inc_id in incidents_by_id:
            existing = incidents_by_id[inc_id]
            # Merge evidence
            merged_evidence = list(existing.evidence)
            for ev in result.evidence:
                if ev not in merged_evidence:
                    merged_evidence.append(ev)
            
            # Create a new updated Incident since it's frozen
            updated_inc = Incident(
                incident_id=existing.incident_id,
                run_id=existing.run_id,
                failure_type=existing.failure_type,
                severity=max(existing.severity, result.severity), # Keep highest severity
                confidence=result.confidence,
                evidence=merged_evidence,
                metrics={**existing.metrics, **result.metrics}
            )
            incidents_by_id[inc_id] = updated_inc
        else:
            inc = Incident(
                incident_id=inc_id,
                run_id=run.run_id,
                failure_type=result.failure_type,
                severity=result.severity,
                confidence=result.confidence,
                evidence=list(result.evidence),
                metrics=dict(result.metrics)
            )
            incidents_by_id[inc_id] = inc

    return list(incidents_by_id.values())
