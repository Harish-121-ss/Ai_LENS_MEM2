import json
from typing import Dict, Any, Optional
from pydantic import ValidationError
from agentlens.contracts.run import Run
from agentlens.contracts.events import AgentToolEvent
from agentlens.normalization.errors import NormalizationError

def _deterministic_serialize(val: Any) -> str:
    if isinstance(val, str):
        return val
    return json.dumps(val, sort_keys=True)

def _normalize_status_result(raw_event: Dict[str, Any]) -> Optional[str]:
    status = raw_event.get("status")
    result = raw_event.get("result")
    
    if status is not None and result is not None:
        return f"Status: {_deterministic_serialize(status)} | Result: {_deterministic_serialize(result)}"
    elif status is not None:
        return _deterministic_serialize(status)
    elif result is not None:
        return _deterministic_serialize(result)
    return None

def _normalize_event(raw_event: Dict[str, Any]) -> AgentToolEvent:
    try:
        return AgentToolEvent(
            seq=raw_event["seq"],
            type=raw_event["type"],
            timestamp_ms=raw_event["timestamp_ms"],
            tool=raw_event.get("tool"),
            arguments=raw_event.get("arguments"),
            status_result=_normalize_status_result(raw_event),
            latency_ms=raw_event.get("latency_ms")
        )
    except KeyError as e:
        raise NormalizationError(f"Missing required event field: {e}")
    except ValidationError as e:
        raise NormalizationError(f"Event validation failed: {e}")

def normalize_run(raw_telemetry: Dict[str, Any]) -> Run:
    try:
        raw_events = raw_telemetry.get("events", [])
        events = [_normalize_event(ev) for ev in raw_events]
        
        return Run(
            run_id=raw_telemetry["run_id"],
            agent_version=raw_telemetry["agent_version"],
            prompt_version=raw_telemetry["prompt_version"],
            request=raw_telemetry["request"],
            events=events,
            tool_calls=raw_telemetry.get("tool_calls", []),
            tokens=raw_telemetry.get("tokens"),
            latency_ms=raw_telemetry.get("latency_ms"),
            errors=raw_telemetry.get("errors", []),
            outcome=raw_telemetry["outcome"],
            detected_failures=raw_telemetry.get("detected_failures", [])
        )
    except KeyError as e:
        raise NormalizationError(f"Missing required Run field: {e}")
    except ValidationError as e:
        raise NormalizationError(f"Run validation failed: {e}")
