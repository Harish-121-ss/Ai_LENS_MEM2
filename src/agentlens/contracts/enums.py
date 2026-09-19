from enum import Enum

class FailureType(str, Enum):
    TOOL_LOOP = "TOOL_LOOP"
    TIMEOUT_RETRY = "TIMEOUT_RETRY"
    WRONG_TOOL = "WRONG_TOOL"
    TOKEN_COST_ANOMALY = "TOKEN_COST_ANOMALY"

class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
