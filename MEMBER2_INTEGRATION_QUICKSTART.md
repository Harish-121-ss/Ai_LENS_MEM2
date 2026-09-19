# Member 2 Integration Quickstart

## What Member 2 Provides
Member 2 provides an offline, deterministic Reliability Intelligence pipeline that normalizes raw execution telemetry, detects anomalies (timeouts, loops), groups them into Incidents, and validates Root Cause Analyses ensuring strict evidence grounding.

## Import Path
```python
from agentlens.engine.orchestrator import run_reliability_pipeline
from agentlens.engine.rca_provider import MockBedrockProvider
import json
```

## Function Call
```python
# Provide a raw JSON execution
with open("tests/fixtures/timeout_retry_run.json", "r") as f:
    raw_execution = json.load(f)

# Initialize a Mock provider for local testing
rca_provider = MockBedrockProvider(response_mock='{"primary_failure": "timeout_retry", "probable_root_cause": "Timeouts calling get_order.", "evidence": [...], "impact": ["High latency"], "recommended_action": "Add bounded retries.", "confidence": 0.95}')

# Execute pipeline
result = run_reliability_pipeline(
    raw_execution=raw_execution,
    rca_provider=rca_provider,
    baseline_tokens=1000.0
)
```

## Handling Output
- **Healthy Execution:** `result.incidents` will be empty.
- **Incident Handling:** Access `result.incidents` to inspect `Incident` objects, including metrics, evidence, and severities.
- **RCA Handling:** Access `result.rca_outputs` using the `incident.incident_id` to retrieve grounded `RCAOutput` objects.

## Test Command
```bash
PYTHONPATH=src pytest -q
```

## Important Assumptions
- **Offline Safety:** The orchestrator guarantees zero network requests or filesystem mutations.
- **Evidence Immutability:** Any RCA logic provided must only return evidence explicitly provided to it in the prompt. Hallucinated evidence will result in a hard `ValueError`.
