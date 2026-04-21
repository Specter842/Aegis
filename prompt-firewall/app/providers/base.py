from abc import ABC, abstractmethod
from typing import Any, Dict, List

class ProviderException(Exception):
    def __init__(self, error_type: str, message: str):
        self.error_type = error_type
        self.message = message
        super().__init__(self.message)

class BaseProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the lowercase name of the provider (e.g. openai)"""
        pass
        
    @abstractmethod
    async def chat_completion(self, model: str, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        Send a chat completion request to the provider.
        Should return the structured assistant message: {"role": "assistant", "content": "..."}
        Raises ProviderException on structured failures.
        """
        pass
