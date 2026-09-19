# STAGE 5 CORRECTION REPORT

## Summary
The Stage 5 Incident Engine and RCA validation logic have been strictly corrected and hardened, focusing on data isolation, offline-provider boundaries, evidence fingerprinting, and full historical regression test coverage.

## Original Stage 5 Gaps
- `confidence` and `metrics` missing explicit formal definitions in the original spec context, though required for accuracy.
- Missing explicit separation of trusted instructions vs. untrusted user prompt data.
- Absence of a mocked Bedrock provider isolation boundary.
- Weak evidence grounding (allowing hallucinated messages within existing seq/tool pairs).
- Missing prompt-injection edge case tests.
- Placeholder `assert True` regression safety test.

## Corrections Implemented
1. **Contract Decision Documented**: Created `STAGE5_CONTRACT_DECISION.md` formally validating that `confidence` and `metrics` belong in `Incident` for strict determinism mapping.
2. **Trusted / Untrusted Data Boundary**: Created `src/agentlens/engine/rca_prompt.py`, strictly dumping telemetry as inert JSON string data under `=== UNTRUSTED INCIDENT DATA ===`.
3. **Mocked Bedrock Boundary**: Created `src/agentlens/engine/rca_provider.py` featuring a deterministic, offline mock to ensure AWS credentials and network calls are avoided entirely.
4. **Evidence Fingerprinting Hardened**: Updated `validate_rca_output` in `rca_engine.py` to fingerprint against ALL properties `(source_run_id, event_sequence, tool_name, event_type, message, metric_value)`. Fabricated messages are now strictly rejected.
5. **Prompt Injection Testing**: Added `test_rca_prompt.py` which demonstrates malicious payloads in the incident are confined to the untrusted data block and do not elevate into the system instructions.
6. **Regression Tests Restored**: Rewrote `test_p5_t43_regression_tests` in `test_stage5_safety.py` to physically run the `normalize_run` function and detectors against a raw dummy telemetry payload, verifying pipeline stability end-to-end.

## Files Changed
- `STAGE5_CONTRACT_DECISION.md` [NEW]
- `src/agentlens/engine/rca_prompt.py` [NEW]
- `src/agentlens/engine/rca_provider.py` [NEW]
- `src/agentlens/engine/rca_engine.py` [MODIFY]
- `tests/test_rca_engine.py` [MODIFY]
- `tests/test_rca_grounding.py` [MODIFY]
- `tests/test_rca_prompt.py` [NEW]
- `tests/test_stage5_safety.py` [MODIFY]

## Pytest Result
- `142 passed in 3.64s`
- Stages 2B-4 remain fully intact and frozen (95/95 original tests passing + Stage 5 tests + regression). No regressions were introduced.
- No network access, no AWS calls were made, and no credentials were required.

## Final Acceptance Status
**STAGE 5 READY FOR HUMAN ACCEPTANCE**
