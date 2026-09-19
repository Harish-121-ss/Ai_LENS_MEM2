import pytest
from unittest.mock import patch
from agentlens.contracts.run import Run
from agentlens.detectors.tool_loop import detect_tool_loop
from agentlens.detectors.timeout_retry import detect_timeout_retry
from agentlens.detectors.wrong_tool import detect_wrong_tool
from agentlens.detectors.token_anomaly import detect_token_anomaly

# P4-T44: Safety/Network Isolation
@patch('socket.socket')
def test_p4_t44_network_safety(mock_socket):
    mock_socket.side_effect = Exception("Network access is strictly prohibited.")
    run = Run(run_id="r-1", agent_version="1", prompt_version="1", request="test", outcome="success", tokens=6000, tool_calls=[], events=[])
    
    detect_tool_loop(run)
    detect_timeout_retry(run)
    detect_wrong_tool(run)
    detect_token_anomaly(run, 1000)
