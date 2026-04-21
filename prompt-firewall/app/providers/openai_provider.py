import os
import httpx
from typing import Any, Dict, List
from app.providers.base import BaseProvider, ProviderException

class OpenAIProvider(BaseProvider):
    def __init__(self, api_key: str = None, base_url: str = "https://api.openai.com/v1", timeout_sec: int = 10):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url
        self.timeout_sec = timeout_sec

    @property
    def provider_name(self) -> str:
        return "openai"

    async def chat_completion(self, model: str, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        if not self.api_key:
            raise ProviderException("auth_failure", "OpenAI API key not configured")

        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": messages,
            **kwargs
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout_sec) as client:
                response = await client.post(url, headers=headers, json=payload)
                
                if response.status_code == 401:
                    raise ProviderException("auth_failure", "Invalid OpenAI API Key")
                elif 400 <= response.status_code < 500:
                    raise ProviderException("upstream_4xx", f"OpenAI Error: {response.text}")
                elif response.status_code >= 500:
                    raise ProviderException("upstream_5xx", f"OpenAI Server Error: {response.text}")
                    
                data = response.json()
                if "choices" not in data or len(data["choices"]) == 0:
                    raise ProviderException("malformed_response", "OpenAI returned an empty response")
                    
                return data["choices"][0]["message"]
                
        except httpx.TimeoutException:
            raise ProviderException("timeout", f"OpenAI request timed out after {self.timeout_sec}s")
        except httpx.RequestError as e:
            raise ProviderException("network_error", f"OpenAI network error: {str(e)}")
        except Exception as e:
            if isinstance(e, ProviderException):
                raise e
            raise ProviderException("unknown_error", str(e))
