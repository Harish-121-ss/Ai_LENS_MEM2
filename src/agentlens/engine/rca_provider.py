import abc

class RCAProvider(abc.ABC):
    """
    Abstract interface for RCA generation providers.
    """
    @abc.abstractmethod
    def generate_rca(self, prompt: str) -> str:
        pass

class MockBedrockProvider(RCAProvider):
    """
    Offline mock provider for deterministic testing of the RCA boundary.
    Does not perform any real network or AWS calls.
    """
    def __init__(self, response_mock: str = "", simulate_timeout: bool = False, simulate_exception: bool = False):
        self.response_mock = response_mock
        self.simulate_timeout = simulate_timeout
        self.simulate_exception = simulate_exception

    def generate_rca(self, prompt: str) -> str:
        if self.simulate_timeout:
            raise TimeoutError("Mocked AWS Bedrock timeout")
        if self.simulate_exception:
            raise RuntimeError("Mocked AWS Bedrock internal service exception")
        
        return self.response_mock
