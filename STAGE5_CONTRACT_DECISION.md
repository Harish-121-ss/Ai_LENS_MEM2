# Stage 5 Contract Decision: Incident Confidence & Metrics

## Background

During the Stage 5 Implementation pass, a contract discrepancy was addressed. The initial formal list of fields for the `Incident` contract did not explicitly list `confidence` or `metrics`. However, the Stage 4 output (`DetectorResult`) and the overall Member 2 pipeline mandate strict preservation of detector-produced evidence, confidence, and metric context.

## Required Fields Decision

The fields `confidence` and `metrics` have been permanently added to the `Incident` contract. The explicit required fields are now:
- `incident_id`
- `run_id`
- `failure_type`
- `severity`
- `confidence`
- `evidence`
- `metrics`
- `rca_status`
- `rca_output` (Optional)

## Justification

* **Why metrics are preserved**: Without `metrics` (such as `observed_tokens` or `retry_count`), the subsequent RCA validation layer and RCA reasoning engine would lose the exact deterministic measurements that caused the anomaly, violating the principle of evidence grounding.
* **How confidence is handled**: `confidence` is directly carried over from the Stage 4 `DetectorResult`, indicating the mathematical/logical certainty of the deterministic detector. It remains a constrained float between 0.0 and 1.0.
* **Compatibility with DetectorResult**: This addition creates perfect 1:1 compatibility between the `DetectorResult` outputs generated in Stage 4 and the `Incident` created in Stage 5, preserving all critical context.
* **Compatibility with the Member 2 plan**: Member 2 owns telemetry normalization, deterministic detectors, structured incident creation, and evidence preservation. Removing evidence context would violate the core architectural premise of Member 2.
* **No Semantic Changes to Previous Stages**: This clarification only applies to Stage 5's `Incident` contract. No existing Stage 2B, 3, or 4 semantic contracts or implementations were changed to accommodate this.
