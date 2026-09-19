import pytest
import json
import os
from pydantic import ValidationError
from agentlens.contracts.run import Run
from agentlens.contracts.events import AgentToolEvent

def test_p2_t13_json_serialization():
    run = Run(
        run_id="r-123", agent_version="v1.0", prompt_version="p-2", request="req",
        events=[], tool_calls=[], outcome="SUCCESS"
    )
    j = run.model_dump_json()
    assert isinstance(j, str)
    assert "r-123" in j

def test_p2_t14_json_round_trip():
    run = Run(
        run_id="r-123", agent_version="v1.0", prompt_version="p-2", request="req",
        events=[], tool_calls=[], outcome="SUCCESS"
    )
    j = run.model_dump_json()
    run2 = Run.model_validate_json(j)
    assert run == run2

def test_p2_t15_version_preservation():
    run = Run(
        run_id="r-123", agent_version="v1.0", prompt_version="p-2", request="req",
        events=[], tool_calls=[], outcome="SUCCESS"
    )
    j = run.model_dump_json()
    run2 = Run.model_validate_json(j)
    assert run2.agent_version == "v1.0"
    assert run2.prompt_version == "p-2"

def test_p2_t18_no_fabricated_telemetry():
    run = Run(
        run_id="r-123", agent_version="v1", prompt_version="p1", request="req",
        events=[], tool_calls=[], outcome="SUCCESS"
    )
    assert run.latency_ms is None
    assert run.tokens is None

def test_p2_t19_deterministic_representation():
    run1 = Run(run_id="r-1", agent_version="v1", prompt_version="p1", request="req", events=[], tool_calls=[], outcome="SUCCESS")
    run2 = Run(run_id="r-1", agent_version="v1", prompt_version="p1", request="req", events=[], tool_calls=[], outcome="SUCCESS")
    assert run1 == run2
    assert run1.model_dump_json() == run2.model_dump_json()

def test_p2_t20_synthetic_data_safety():
    # Scan fixtures for obvious secrets
    fixture_path = os.path.join(os.path.dirname(__file__), "fixtures", "synthetic_contract_data.json")
    with open(fixture_path, 'r') as f:
        content = f.read()
        assert "AKIA" not in content # No AWS keys
        assert "secret" not in content.lower() # basic check
