import pytest
from pydantic import ValidationError
from agentlens.contracts.rca import RCAOutput

def test_p2_t11_rcaoutput_validation():
    rca = RCAOutput(
        primary_failure="loop",
        probable_root_cause="bug",
        evidence=[],
        impact=["delay"],
        recommended_action="fix it",
        confidence=0.8
    )
    assert rca.primary_failure == "loop"

def test_p2_t12_invalid_rcaoutput():
    with pytest.raises(ValidationError):
        RCAOutput(
            primary_failure="loop",
            probable_root_cause="bug",
            evidence=[],
            impact=["delay"],
            recommended_action="fix it",
            confidence=1.5 # Invalid confidence
        )
