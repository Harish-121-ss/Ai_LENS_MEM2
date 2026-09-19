# Stage 5 Contract Decision: Incident Confidence & Metrics

## Background

During the Stage 5 Implementation pass, a contract discrepancy was addressed. The initial formal list of fields for the `Incident` contract did not explicitly list `confidence` or `metrics`. However, the Stage 4 output (`DetectorResult`) and the overall Member 2 pipeline mandate strict preservation of detector-produced evidence, confidence, and metric context.

## Decision

The fields `confidence` and `metrics` have been permanently added to the `Incident` contract.

```python
class Incident(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    incident_id: str
    run_id: str
    failure_type: FailureType
    severity: Severity
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: List[Evidence]
    metrics: Dict[str, Any]
    # ...
```

## Rationale

1. **Information Preservation**: `DetectorResult` generates both `confidence` and `metrics`. Dropping these when creating an `Incident` violates the principle of evidence preservation and results in loss of diagnostic context.
2. **Deterministic Context**: Without `metrics` (such as `observed_tokens` or `anomaly_ratio`), the subsequent RCA validation layer and RCA reasoning engine would lose the exact deterministic measurements that caused the anomaly.
3. **No Unrelated Redesign**: This is a direct alignment of the `Incident` schema to accurately map the data already generated in Stage 4, keeping the existing architecture and pipeline intact without unrelated structural redesign.
