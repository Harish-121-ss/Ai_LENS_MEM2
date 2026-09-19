# STAGE 5 CORRECTION REPORT

## Original Stage 5 Issues
- `confidence` and `metrics` missing explicit formal definitions in the original spec context, though required for accuracy.
- Missing explicit separation of trusted instructions vs. untrusted user prompt data.
- Absence of a mocked Bedrock provider isolation boundary.
- Weak evidence grounding (allowing hallucinated messages within existing seq/tool pairs).
- Missing prompt-injection edge case tests.
- Placeholder `assert True` regression safety test.
- Missing explicit checks for file system isolation and canonical timeout regression.

## Exact Corrections Implemented
- **Contract Decision**: Created `STAGE5_CONTRACT_DECISION.md` formally validating that `confidence` and `metrics` belong in `Incident` to preserve deterministic mapping.
- **Incident Engine Verification**: `process_detector_results` now correctly initializes `rca_status="PENDING"`. Duplicate detector results merge evidence into a single Incident using deterministic properties. No duplicate incidents are spawned uncontrolled. 
- **RCA Provider Boundary**: Created `src/agentlens/engine/rca_prompt.py`, strictly dumping telemetry as inert JSON string data under `=== UNTRUSTED INCIDENT DATA ===`. Created `src/agentlens/engine/rca_provider.py` featuring a deterministic, offline mock to ensure AWS credentials and network calls are avoided entirely.
- **Evidence Grounding Behavior**: Updated `validate_rca_output` in `rca_engine.py` to fingerprint against ALL properties `(source_run_id, event_sequence, tool_name, event_type, message, metric_value)`. Fabricated messages, run IDs, event types, or metric values are now strictly rejected.
- **Canonical Timeout/Retry Regression Result**: Rewrote `test_p5_t43_canonical_timeout_retry_regression` in `test_stage5_safety.py` to physically run the `normalize_run` function and all Stage 4 detectors against a raw dummy telemetry payload, verifying pipeline stability end-to-end and strict schema matching of the resulting Incident.
- **Safety Test Results**: `test_p5_t42_no_filesystem_mutation` was updated to explicitly snapshot `os.getcwd()` and assert no new files were created after a full RCA pipeline run. `test_p5_t39_no_network_access` completely disables sockets using `unittest.mock`. 

## Complete Pytest Result
- `142 passed in 3.64s`
- Stage 2B count: 20
- Stage 3 count: 30
- Stage 4 count: 45
- Stage 5 count: 47
- Total count: 142
- Failures/errors: 0

## Files Changed
- `STAGE5_CONTRACT_DECISION.md` [NEW]
- `src/agentlens/engine/rca_prompt.py` [NEW]
- `src/agentlens/engine/rca_provider.py` [NEW]
- `src/agentlens/engine/incident_engine.py` [MODIFY]
- `src/agentlens/engine/rca_engine.py` [MODIFY]
- `tests/test_rca_engine.py` [MODIFY]
- `tests/test_rca_grounding.py` [MODIFY]
- `tests/test_rca_prompt.py` [NEW]
- `tests/test_stage5_safety.py` [MODIFY]

## Files Intentionally Not Changed
- All Stage 2B, 3, and 4 contracts and detectors.
- Member 1 files.

## Known Limitations
- The mocked provider currently uses static JSON string parsing for RCA responses. In Stage 6, it will need to correctly route JSON mapping into actual LLM invocations using AWS Bedrock, while respecting the same isolation boundaries established here.
