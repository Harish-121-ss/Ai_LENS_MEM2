from typing import Dict, Any, List
from pydantic import BaseModel

from agentlens.contracts.run import Run
from agentlens.contracts.incident import Incident
from agentlens.contracts.rca import RCAOutput

from agentlens.normalization.normalizer import normalize_run
from agentlens.detectors.timeout_retry import detect_timeout_retry
from agentlens.detectors.tool_loop import detect_tool_loop
from agentlens.detectors.wrong_tool import detect_wrong_tool
from agentlens.detectors.token_anomaly import detect_token_anomaly

from agentlens.engine.incident_engine import process_detector_results
from agentlens.engine.rca_engine import generate_and_validate_rca
from agentlens.engine.rca_provider import RCAProvider


class PipelineResult(BaseModel):
    run: Run
    incidents: List[Incident]
    rca_outputs: Dict[str, RCAOutput]


def run_reliability_pipeline(raw_execution: Dict[str, Any], rca_provider: RCAProvider, baseline_tokens: float = 1000.0) -> PipelineResult:
    # 1. Normalize
    run = normalize_run(raw_execution)
    
    # 2. Detect (Stage 4)
    results = []
    for detector in [detect_timeout_retry, detect_tool_loop, detect_wrong_tool]:
        res = detector(run)
        if res is not None:
            results.append(res)
            
    res = detect_token_anomaly(run, baseline_tokens)
    if res is not None:
        results.append(res)
            
    # 3. Incident Engine (Stage 5)
    incidents = process_detector_results(run, results)
    
    # 4. RCA (Stage 5)
    rca_outputs = {}
    for incident in incidents:
        rca = generate_and_validate_rca(incident, rca_provider)
        rca_outputs[incident.incident_id] = rca
        
    return PipelineResult(
        run=run,
        incidents=incidents,
        rca_outputs=rca_outputs
    )
