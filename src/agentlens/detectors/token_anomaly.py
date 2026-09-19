from typing import Optional
from agentlens.contracts.run import Run
from agentlens.contracts.detector import DetectorResult, Evidence, FailureType, Severity

def detect_token_anomaly(run: Run, baseline_tokens: float) -> Optional[DetectorResult]:
    if run.tokens is None or baseline_tokens <= 0 or run.tokens < 0:
        return None
        
    ratio = run.tokens / baseline_tokens
    
    if ratio <= 2.0:
        return None
        
    severity = Severity.MEDIUM if ratio <= 5.0 else Severity.HIGH
    
    evidence = [Evidence(
        source_run_id=run.run_id,
        event_sequence=None,
        tool_name=None,
        event_type="token_anomaly",
        message=f"Token anomaly ratio {ratio:.2f} > 2.0",
        metric_value=float(run.tokens)
    )]
    
    return DetectorResult(
        run_id=run.run_id,
        failure_type=FailureType.TOKEN_COST_ANOMALY,
        severity=severity,
        confidence=1.0,
        evidence=evidence,
        metrics={
            "observed_tokens": run.tokens,
            "baseline_tokens": baseline_tokens,
            "anomaly_ratio": ratio
        }
    )
