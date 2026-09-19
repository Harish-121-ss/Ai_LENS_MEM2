import json
from pydantic import ValidationError
from agentlens.contracts.incident import Incident
from agentlens.contracts.rca import RCAOutput
from agentlens.contracts.evidence import Evidence
from agentlens.engine.rca_prompt import build_rca_prompt
from agentlens.engine.rca_provider import RCAProvider

def validate_rca_output(incident: Incident, raw_rca_json: str) -> RCAOutput:
    if not raw_rca_json or not raw_rca_json.strip():
        raise ValueError("Empty RCA response")

    try:
        parsed_json = json.loads(raw_rca_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Malformed RCA JSON: {e}")

    # Pydantic will handle schema validation (missing fields, types, etc.)
    try:
        rca_output = RCAOutput(**parsed_json)
    except ValidationError as e:
        raise ValueError(f"RCA schema validation failed: {e}")

    # Evidence Grounding Validation
    # Ensure all evidence items returned by RCA actually exist in Incident.evidence
    # We strictly enforce that the RCA output does not fabricate any part of the evidence.
    # The fingerprint uses ALL fields to guarantee absolute fidelity.
    
    incident_evidence_fingerprints = {
        (ev.source_run_id, ev.event_sequence, ev.tool_name, ev.event_type, ev.message, ev.metric_value)
        for ev in incident.evidence
    }

    for rca_ev in rca_output.evidence:
        fingerprint = (rca_ev.source_run_id, rca_ev.event_sequence, rca_ev.tool_name, rca_ev.event_type, rca_ev.message, rca_ev.metric_value)
        if fingerprint not in incident_evidence_fingerprints:
            raise ValueError(f"Unsupported claim: RCA fabricated evidence {fingerprint}")


    return rca_output

def generate_and_validate_rca(incident: Incident, provider: RCAProvider) -> RCAOutput:
    """
    Constructs the prompt, calls the provider, and validates the output securely.
    """
    prompt = build_rca_prompt(incident)
    
    try:
        raw_json = provider.generate_rca(prompt)
    except Exception as e:
        # Wrap any provider-level exceptions safely
        raise RuntimeError(f"RCA provider failed safely: {e}")
        
    return validate_rca_output(incident, raw_json)
